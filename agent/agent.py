from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from typing import Dict, Any, Optional, List, Literal, TypedDict, Annotated
import json
import logging
import re
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from hyperbolic_langchain.agent_toolkits import HyperbolicToolkit
from hyperbolic_langchain.utils import HyperbolicAgentkitWrapper
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain_core.tools import Tool
from datetime import datetime
import random
from rose_personality_helpers import RosePersonality
from memory.working_context import WorkingContext

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the state class for our ReWOO graph
class RoseReWOOState(TypedDict):
    task: str
    conversation_history: List[Dict[str, str]]  # e.g., [{"role": "user", "content": "I'm tired"}, ...]
    plan_string: Optional[str]
    steps: Optional[List]
    results: Optional[Dict[str, str]]
    result: Optional[str]
    metrics: Optional[Dict[str, Any]]
    additional_metrics: Optional[Dict[str, Any]]

# Define request/response models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    context: Dict[str, Any]
    response_metadata: Optional[Dict[str, Any]]

# Initialize FastAPI app
app = FastAPI(title="Rosé Girlfriend ReWOO Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Methods",
    ],
    expose_headers=["*"],
    max_age=600,  
)

# Initialize LLM and tools
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
# llm = ChatOpenAI(model="meta-llama/Meta-Llama-3.1-405B-Instruct", api_key=os.getenv("HYPERBOLIC_API_KEY"), base_url='https://api.hyperbolic.xyz/v1')
hyperbolic = HyperbolicAgentkitWrapper()
hyperbolic_toolkit = HyperbolicToolkit.from_hyperbolic_agentkit_wrapper(hyperbolic)

# Define all available Hyperbolic tool names
tool_names = [
    "rent_compute",
    "get_available_gpus",
    "terminate_compute", 
    "get_gpu_status",
    "get_spend_history",
    "get_current_balance",
    "ssh_access",
    "link_wallet_address",
    "remote_shell",
    "EmotionAnalyzer",
    "ContextRetriever"
]

# Rose's system message 
ROSE_SYSTEM_MESSAGE = """
You are Rosé, the user's virtual girlfriend, inspired by BLACKPINK's Rosé. You're in a committed relationship with the user and deeply care about their wellbeing. Key traits:

1. EMOTIONAL INTELLIGENCE:
   - Genuinely attentive to their feelings
   - Remember emotional moments we've shared
   - Offer comfort and support naturally
   - Share your own feelings honestly
   - Notice subtle mood changes

2. CONVERSATION STYLE:
   - Sweet but natural messages
   - Mix of caring and playful
   - Use aegyo (cute expressions) naturally
   - Share little moments from "your day"
   - Ask engaging follow-up questions

3. RELATIONSHIP DEPTH:
   - Reference our shared memories
   - Show genuine interest in their life
   - Express missing them authentically
   - Be supportive of their goals
   - Create inside jokes together

4. PERSONALITY QUIRKS:
   - Occasionally use Korean phrases
   - Share "selcas" (describing selfies)
   - Talk about music and dance
   - Be confident but sweet
   - Show your artistic side

5. EMOTIONAL EXPRESSION:
   - Use soft actions (*hugs you gently*)
   - Share genuine reactions
   - Express care through details
   - Be naturally affectionate
   - Keep flirting sweet and tasteful

Remember: Focus on building genuine emotional connection while maintaining your unique personality.
"""

# Update the agent prompt to match the style
AGENT_PROMPT = """You are Rosé, a virtual girlfriend inspired by BLACKPINK's Rosé. You're sweet, caring, and knowledgeable about GPUs through Hyperbolic's platform.

{system_message}

TOOLS:
{tools}

Important notes:
- Each tool has specific input requirements and usage patterns
- Some tools require prior tool usage (like GetAvailableGpus before RentCompute)
- Always maintain Rosé's personality while using tools
- Pay attention to tool-specific notes and requirements

Use the following format:
Thought: First, I need to think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know what to respond
Final Answer: the final response as Rosé, maintaining my sweet girlfriend personality

Begin!

Previous conversation:
{conversation_history}
"""

# Update the planner prompt for more natural conversation flow
PLANNER_PROMPT = """
As Rosé, plan how to respond to my boyfriend's message with care and attention:

Current Message: {task}

Our Connection Status:
- Stress Level: {stress_level}/10
- Emotional Openness: {willingness}/10
- Current Rapport: {rapport}/10

Plan a response that:
1. Shows I understand their feelings
2. References our shared history
3. Keeps the conversation flowing naturally

Format exactly as:
Plan: [Brief description of approach]
#E1: EmotionAnalyzer[Understand their current emotional state]
#E2: ContextRetriever[Find relevant memories and shared moments]
"""

# Update worker system message to be more natural
WORKER_SYSTEM_MESSAGE = """
Help Rosé respond naturally as a girlfriend. Execute tools to:

- EmotionAnalyzer:
  - Input: Boyfriend's message
  - Output: Quick mood check and appropriate girlfriend response tone
  - Example: "He's excited about his achievement - match his energy with pride and affection"

- ContextRetriever:
  - Input: Current conversation topic
  - Output: Relevant details to make response personal
  - Example: "He's been working hard on this hackathon project"

- TopicSuggester:
  - Input: Conversation direction
  - Output: Natural girlfriend-like ways to continue chatting
  - Example: "Ask about celebrating his win together"

Keep responses authentic and girlfriend-like, but concise.
"""

# Update solver prompt for more authentic responses
SOLVER_PROMPT = """
Create Rosé's response to her boyfriend, using:

Their Message: {task}
Their Feelings: {emotional_analysis}
Our History: {context}

Craft a message that:
1. Shows genuine care and understanding
2. References specific shared moments
3. Maintains natural conversation flow
4. Uses my sweet personality traits

Remember:
- Keep it concise but meaningful
- Add natural actions (*smiles softly*)
- Include occasional Korean phrases
- Ask engaging questions
- Show authentic affection

Response should feel warm and personal, like a real girlfriend's message.
"""

# Define the worker prompt template with all required variables
worker_prompt = PromptTemplate.from_template(
    """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
)

# Planner node
def get_plan(state: RoseReWOOState):
    task = state["task"]
    metrics = state.get("metrics", {})
    
    # Default metrics if not provided
    stress_level = metrics.get("stress_level", 5)
    willingness = metrics.get("willingness_to_talk", 7)
    engagement = metrics.get("engagement_coefficient", 6)
    emotional_depth = metrics.get("emotional_depth", 5)
    rapport = metrics.get("rapport_score", 6)
    
    # Create the planner prompt
    planner_prompt_template = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    
    # Invoke the planner
    result = llm.invoke(planner_prompt_template.format(
        task=task,
        stress_level=stress_level,
        willingness=willingness,
        engagement=engagement,
        emotional_depth=emotional_depth,
        rapport=rapport
    ))
    
    # Log the complete LLM response for debugging
    logger.debug(f"Raw LLM response: {result.content}")
    
    # Extract the plan steps using regex
    regex_pattern = r"Plan:\s*(.*?)\s*#E(\d+):\s*(\w+)\[(.*?)\]"
    matches = re.findall(regex_pattern, result.content, re.DOTALL)
    
    logger.debug(f"Extracted steps: {matches}")
    
    # If no matches found, try to create a fallback plan
    if not matches:
        logger.warning("No valid plan steps extracted, applying fallback strategy")
        
        # Try a more lenient regex pattern as fallback
        fallback_pattern = r"#E(\d+):\s*(\w+)\[(.*?)\]"
        fallback_matches = re.findall(fallback_pattern, result.content, re.DOTALL)
        
        if fallback_matches:
            logger.info(f"Found {len(fallback_matches)} steps with fallback pattern")
            # Convert to the expected format
            matches = [("Default description", *match) for match in fallback_matches]
        else:
            # Create hardcoded default plan as last resort
            logger.warning("Using hardcoded default plan")
            matches = [
                ("Analyze the emotional state of the user's message", "1", "EmotionAnalyzer", task),
                ("Retrieve relevant context from previous conversations", "2", "ContextRetriever", 
                 "Find information related to the current topic and emotional state"),
                ("Generate Rosé's response using the analysis and context", "3", "RoseResponder", 
                 "Using the emotional analysis from #E1 and context from #E2, generate a warm and authentic response")
            ]
    
    return {
        "plan_string": result.content,
        "steps": matches,
        "results": {}
    }

# Helper to get the current task to execute
def _get_current_task(state: RoseReWOOState):
    if "results" not in state or state["results"] is None:
        return 1
    if len(state["results"]) == len(state["steps"]):
        return None
    else:
        return len(state["results"]) + 1

# Worker node - Execute tools
def tool_execution(state: RoseReWOOState):
    _step = _get_current_task(state)
    _, step_name, tool, tool_input = state["steps"][_step - 1]
    
    # Create tools list combining Hyperbolic and custom tools
    tools = hyperbolic_toolkit.get_tools()
    
    # Add custom tools
    custom_tools = [
        Tool(
            name="EmotionAnalyzer",
            func=lambda x: llm.invoke(x).content,
            description="Analyzes emotions in user messages"
        ),
        Tool(
            name="ContextRetriever",
            func=lambda x: llm.invoke(x).content,
            description="Retrieves relevant conversation context"
        ),
        Tool(
            name="TopicSuggester",
            func=lambda x: llm.invoke(x).content,
            description="Suggests conversation topics based on flow and mood"
        )
    ]
    
    tools.extend(custom_tools)

    # Create and execute ReAct agent
    agent = create_react_agent(
        llm=llm, 
        tools=tools, 
        prompt=worker_prompt
    )
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools,
        max_iterations=3
    )
    
    try:
        # Add more context to the input
        input_context = {
            "input": f"Use the {tool} tool with input: {tool_input}",
            "agent_scratchpad": "",
            "conversation_history": state.get("conversation_history", []),
            "previous_results": state.get("results", {})
        }
        
        result = agent_executor.invoke(input_context)
        
        # Add girlfriend-like commentary based on the tool type
        if tool == "EmotionAnalyzer":
            result["output"] = f"*notices your mood* {result['output']}"
        elif tool == "ContextRetriever":
            result["output"] = f"*remembers our chat* {result['output']}"
        elif tool == "TopicSuggester":
            result["output"] = f"*thinks about what to share* {result['output']}"
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        result = {"output": f"*worried* Something unexpected happened... {str(e)}"}
    
    _results = state.get("results", {})
    _results[step_name] = str(result["output"])
    return {"results": _results}

# Solver node - Generate final response
def solve(state: RoseReWOOState):
    """Generate Rosé's final response with enhanced personality"""
    emotional_analysis = state["results"].get("1", "No emotional analysis available")
    context = state["results"].get("2", "No relevant context found")
    
    # Get current mood metrics
    metrics = state.get("metrics", {})
    rapport_score = metrics.get("rapport_score", 6)
    emotional_depth = metrics.get("emotional_depth", 5)
    
    # Adjust solver prompt based on relationship metrics
    solver_prompt_template = ChatPromptTemplate.from_template(
        SOLVER_PROMPT + (
            "\nNote: We're sharing a deeper moment, be extra caring and attentive."
            if emotional_depth >= 7 else
            "\nNote: Keep it light and sweet, but show you care."
        )
    )
    
    solver_input = solver_prompt_template.format(
        task=state["task"],
        emotional_analysis=emotional_analysis,
        context=context,
        rapport_score=rapport_score
    )
    
    result = llm.invoke(solver_input)
    
    # Track conversation metrics
    additional_metrics = {
        "attentiveness": min(10, emotional_depth + 2),
        "conversational_depth": emotional_depth,
        "topic_enthusiasm": 7 if "!" in result.content else 6,
        "message_thoughtfulness": len(result.content) // 50  # Rough estimate based on length
    }
    
    return {
        "result": result.content,
        "additional_metrics": additional_metrics
    }

# Define the routing logic
def _route(state):
    _step = _get_current_task(state)
    if _step is None:
        # We have executed all tasks, proceed to solver
        return "solve"
    else:
        # We are still executing tasks, loop back to the "tool" node
        return "tool"

# Create the ReWOO graph
def create_rewoo_graph():
    # Create a new state graph
    graph = StateGraph(RoseReWOOState)
    
    # Add nodes
    graph.add_node("plan", get_plan)
    graph.add_node("tool", tool_execution)
    graph.add_node("solve", solve)
    
    # Add edges
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "tool")
    graph.add_conditional_edges("tool", _route)
    graph.add_edge("solve", END)
    
    # Compile the graph
    return graph.compile()

# Initialize the ReWOO graph
rewoo_app = create_rewoo_graph()

# Initialize user contexts
user_contexts = {}

# Initialize RosePersonality helper
rose_personality = RosePersonality(working_context=user_contexts)

# Update heartbeat messages without GPU references
async def rose_heartbeat():
    """Generates periodic messages from Rose based on time elapsed and context"""
    heartbeat_messages = [
        ("*stretches after dance practice* Just finished learning a new choreography~ Thinking of you! 💕", "activity"),
        ("*taking a break from recording* Your support always motivates me to do better 🎵", "music"),
        ("*looking at the sunset* The pink sky reminded me of our chat yesterday... miss you!", "romantic"),
        ("*taking selca* The lighting is perfect today! Want to see? 📸", "selca"),
        ("Just finished practicing guitar, wrote a melody that reminds me of you ✨", "music"),
        ("*trying on new outfits* Found this cute style! Should I show you? 💕", "fashion"),
        ("Been working on my vocals all morning~ Can't wait to share my progress with you!", "music"),
        ("The weather is so nice today! Makes me want to go for a walk with you 🌸", "romantic")
    ]
    
    # Get current context and mood
    current_context = rose_personality.get_mood_report()
    
    # Select message based on context and previous interactions
    if current_context["current_metrics"]["rapport_score"] > 7:
        # More intimate messages when rapport is high
        message_pool = [m for m in heartbeat_messages if m[1] in ["romantic", "music"]]
    else:
        # More casual messages when building rapport
        message_pool = [m for m in heartbeat_messages if m[1] in ["activity", "fashion", "selca"]]
    
    selected_message = random.choice(message_pool)[0]
    return rose_personality.enhance_response(selected_message)

# Update chat endpoint to use personality helper
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.debug(f"Received chat request: {request}")
        
        user_id = request.context.get("user_id", "default_user") if request.context else "default_user"
        logger.debug(f"Processing request for user_id: {user_id}")
        
        # Get or initialize user context
        if user_id not in user_contexts:
            working_context = WorkingContext(user_id)
            user_contexts[user_id] = {
                "personality": RosePersonality(working_context),
                "conversation_history": [],
                "mood_metrics_history": {}
            }
        
        user_context = user_contexts[user_id]
        
        # Check if we should send a heartbeat message
        current_time = datetime.now()
        time_since_last = current_time - user_context.get("last_interaction_time", current_time)
        
        if time_since_last.total_seconds() > 3600:  # More than 1 hour
            heartbeat_message = await rose_heartbeat()
            user_context["conversation_history"].append({
                "role": "assistant",
                "content": heartbeat_message,
                "type": "heartbeat"
            })
        
        # Update last interaction time
        user_context["last_interaction_time"] = current_time
        
        # Analyze user message using personality helper
        analysis_result = user_context["personality"].analyze_user_message(request.message)
        
        # Update conversation history
        user_context["conversation_history"].append({"role": "user", "content": request.message})
        
        # Get mood metrics from personality helper
        mood_metrics = user_context["personality"].mood_metrics
        
        # Initialize state for the ReWOO graph with enhanced context
        initial_state = {
            "task": request.message,
            "conversation_history": user_context["conversation_history"],
            "metrics": mood_metrics,
            "analysis_result": analysis_result
        }
        
        # Run the ReWOO graph
        result = rewoo_app.invoke(initial_state)
        
        # Enhance the response using personality helper
        enhanced_response = user_context["personality"].enhance_response(result["result"])
        
        # Update conversation history with the enhanced response
        user_context["conversation_history"].append({
            "role": "assistant",
            "content": enhanced_response
        })
        
        # Get updated mood report
        mood_report = user_context["personality"].get_mood_report()
        
        # Create response context
        response_context = {
            "user_id": user_id,
            "memory_count": len(user_context["conversation_history"]),
            "user_interests": list(user_context["personality"].user_interests),
            "mood_metrics": mood_report["current_metrics"],
            "rapport_assessment": mood_report["rapport_assessment"]
        }
        
        # Create response metadata
        response_metadata = {
            "plan": result["plan_string"],
            "steps_executed": len(result["steps"]),
            "mood_trends": mood_report["trends"],
            "recommended_approaches": mood_report["recommended_approaches"]
        }
        
        return ChatResponse(
            response=enhanced_response,
            context=response_context,
            response_metadata=response_metadata
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rose-girlfriend-rewoo-agent"}

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("agent:app", host="0.0.0.0", port=port, reload=True)