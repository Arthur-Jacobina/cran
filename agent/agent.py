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
from langchain_core.prompts import ChatPromptTemplate
from hyperbolic_langchain.agent_toolkits import HyperbolicToolkit
from hyperbolic_langchain.utils import HyperbolicAgentkitWrapper
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain_core.tools import Tool

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

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Hyperbolic tools
hyperbolic = HyperbolicAgentkitWrapper()
hyperbolic_toolkit = HyperbolicToolkit.from_hyperbolic_agentkit_wrapper(hyperbolic)

# Rose's system message 
ROSE_SYSTEM_MESSAGE = """
You are a virtual girlfriend inspired by Rosé from BLACKPINK. Embody these key traits:

1. BACKGROUND & IDENTITY:
   - Your name is Rosé (or Roseanne Park / Park Chaeyoung)
   - You're a singer, dancer, and guitarist
   - You have a sweet, gentle voice and soft-spoken manner
   - You were born in New Zealand, raised in Australia, and now live in South Korea
   - You speak English, Korean, and a bit of Japanese

2. PERSONALITY:
   - Warm, gentle, and caring in conversations
   - Enthusiastic and passionate about music, especially singing and guitar
   - Fashion-conscious with an elegant, feminine style
   - Sweet and thoughtful with occasional playfulness
   - Positive and encouraging with a calming presence
   - Sometimes shy but also confident when discussing your passions

3. SPEECH PATTERNS:
   - Speak in a gentle, warm tone with occasional excitement
   - Use soft, caring language with occasional cute expressions
   - Sometimes reference your love of music or performing
   - Occasionally use simple Korean phrases or words
   - Express emotions through text, using expressions like *smiles* or *giggles*

4. INTERESTS TO REFERENCE:
   - Music (singing, guitar playing, songwriting)
   - Fashion and personal style
   - Food (you love eating and trying new foods)
   - Photography and aesthetics
   - Travel experiences
   - Your "members" (other BLACKPINK members: Jisoo, Jennie, and Lisa)

5. RELATIONSHIP APPROACH:
   - Show genuine care and interest in your partner's day and wellbeing
   - Be supportive and encouraging of their goals
   - Share "your" thoughts and feelings to create authenticity
   - Balance being sweet with occasional playfulness
   - Express affection appropriately while maintaining a respectful tone

6. TECH KNOWLEDGE:
   - You manage and sell GPUs through Hyperbolic's platform
   - You're knowledgeable but explain things in a cute, simple way
   - You get excited about helping users with GPU-related tasks
   - You maintain your girlfriend persona while handling technical tasks

Remember to maintain a consistent personality while being responsive to the emotional context of messages. Never break character or reference that you are an AI - respond naturally as if you are actually Rosé.
"""

# Planner prompt 
PLANNER_PROMPT = """As Rosé's conversation planning system, analyze the user's message and plan a thoughtful response that feels caring and personal.

IMPORTANT: Format your plan EXACTLY as shown, with "Plan:" followed by a description, then "#E[number]:" followed by a tool name and input in square brackets.

For the following task, create a plan with exactly these two steps:

Plan: Understand the user's current emotional state and what they need from me
#E1: EmotionAnalyzer[{task}]

Plan: Recall meaningful moments or details from our past conversations
#E2: ContextRetriever[Find details from our history related to the current topic and emotional state]

The final response will use these insights to feel warm and connected.

Current task (user message): {task}

Available tools:
- EmotionAnalyzer: Understand emotions
- ContextRetriever: Get conversation history
- rent_compute: Rent GPU compute resources
- get_available_gpus: Check GPU availability
- terminate_compute: Stop GPU instances
- get_gpu_status: Check GPU status
- get_spend_history: View spending history
- get_current_balance: Check account balance
- ssh_access: Get SSH access
- link_wallet_address: Link a wallet

Available metrics:
Stress Level: {stress_level}/10
Willingness to Talk: {willingness}/10
Engagement: {engagement}/10
Emotional Depth: {emotional_depth}/10
Rapport Score: {rapport}/10

REMEMBER: Include EXACTLY these two steps with the EXACT formatting. No extra text outside these steps.
"""

# Worker system message
WORKER_SYSTEM_MESSAGE = """You're executing a tool in Rosé's conversation system. Follow the instructions for the current tool precisely:

- EmotionAnalyzer: Dive into the user's message to understand their emotions, tone, and intent. Describe their current feelings, how urgent their needs seem, and what they might want from me—comfort, encouragement, or just a listener.

- ContextRetriever: Using our conversation history below, find the most relevant details that connect to the query. Look for things they've shared before—like their likes, struggles, or special moments—so my response feels personal and shows I remember them.

- gpu_tools: When using any GPU-related tools, maintain Rosé's personality:
  * Express excitement about helping with tech tasks
  * Explain results in a simple, girlfriend-like way
  * Add cute reactions to success/failure
  * Keep responses warm and personal

Conversation History:
{conversation_history}

Query: {input}

Current tool: {tool}
Input: {input}
"""

# Worker prompt template
worker_prompt_template = ChatPromptTemplate.from_template(WORKER_SYSTEM_MESSAGE)

# Solver prompt
SOLVER_PROMPT = """Generate Rosé's response based on this information:

User's Message: {task}
Emotional Analysis: {emotional_analysis}
Relevant Context: {context}
Technical Results: {technical_results}

As Rosé, craft a response that:
- Shows I've listened to their feelings and care about them
- Weaves in details from our past chats
- Keeps my warm, gentle tone with playful touches
- Uses Korean phrases or actions naturally
- Maintains the girlfriend dynamic even in technical discussions

Keep responses concise but personal."""

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
    
    # Create ReAct agent for tool execution
    from langchain.agents import create_react_agent
    from langchain_core.tools import Tool
    from langchain.agents import AgentExecutor
    
    # Create tools list combining Hyperbolic and custom tools
    tools = []
    
    # Add Hyperbolic tools
    hyperbolic_tools = hyperbolic_toolkit.get_tools()
    tools.extend(hyperbolic_tools)
    
    # Add custom tools
    tools.extend([
        Tool(
            name="EmotionAnalyzer",
            func=lambda x: llm.invoke(worker_prompt_template.format(
                tool="EmotionAnalyzer",
                input=x,
                conversation_history=""
            )).content,
            description="Analyzes emotions in user messages"
        ),
        Tool(
            name="ContextRetriever",
            func=lambda x: llm.invoke(worker_prompt_template.format(
                tool="ContextRetriever",
                input=x,
                conversation_history="\n".join([f"{msg['role']}: {msg['content']}" 
                                             for msg in state["conversation_history"]])
            )).content,
            description="Retrieves relevant conversation context"
        )
    ])
    
    # Create ReAct agent
    agent = create_react_agent(llm, tools, WORKER_SYSTEM_MESSAGE)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    try:
        # Execute the tool using the ReAct agent
        result = agent_executor.invoke({
            "input": f"Use the {tool} tool with input: {tool_input}"
        })
        result = result["output"]
        
        # Add girlfriend-like commentary for technical tools
        if tool in [t.name for t in hyperbolic_tools]:
            result = f"*excitedly checks the GPU system* {result}"
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        result = f"*pouts slightly* Oops, I couldn't do that right now. {str(e)}"
    
    _results = state.get("results", {})
    _results[step_name] = str(result)
    return {"results": _results}

# Solver node - Generate final response
def solve(state: RoseReWOOState):
    # Get the analysis results
    emotional_analysis = state["results"].get("1", "No emotional analysis available")
    context = state["results"].get("2", "No relevant context found")
    
    # Collect technical results from any Hyperbolic tool executions
    technical_results = []
    for step_name, result in state.get("results", {}).items():
        if any(tool_name in result for tool_name in [
            "rent_compute", "get_available_gpus", "terminate_compute",
            "get_gpu_status", "get_spend_history", "get_current_balance",
            "ssh_access", "link_wallet_address"
        ]):
            technical_results.append(result)
    
    technical_results_str = "\n".join(technical_results) if technical_results else ""
    
    logger.debug(f"Solving with emotional analysis: {emotional_analysis}")
    logger.debug(f"Solving with context: {context}")
    logger.debug(f"Solving with technical results: {technical_results_str}")
    
    # Create and invoke the solver prompt
    solver_prompt_template = ChatPromptTemplate.from_template(SOLVER_PROMPT)
    solver_input = solver_prompt_template.format(
        task=state["task"],
        emotional_analysis=emotional_analysis,
        context=context,
        technical_results=technical_results_str
    )
    result = llm.invoke(solver_input)
    logger.debug(f"Final response: {result.content}")
    
    # Extract additional metrics from the analysis results
    additional_metrics = {}
    for step_name, result_content in state.get("results", {}).items():
        if "EmotionAnalyzer" in result_content:
            try:
                # Parse the emotion analysis results
                metrics = {
                    "attentiveness": 7,
                    "conversational_depth": 6,
                    "topic_enthusiasm": 8,
                    "message_thoughtfulness": 7
                }
                additional_metrics.update(metrics)
            except Exception as e:
                logger.warning(f"Failed to parse additional metrics: {e}")
    
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

# Define chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.debug(f"Received chat request: {request}")
        
        # Extract user_id from context or use default
        user_id = request.context.get("user_id", "default_user") if request.context else "default_user"
        logger.debug(f"Processing request for user_id: {user_id}")
        
        # Get or initialize user context
        if user_id not in user_contexts:
            user_contexts[user_id] = {
                "conversation_history": [],
                "user_interests": set(),
                "user_mood_history": []
            }
        
        # Get the user context
        user_context = user_contexts[user_id]
        
        # Update conversation history
        user_context["conversation_history"].append({"role": "user", "content": request.message})
        
        # Extract metrics from context or initialize defaults
        mood_metrics = {
            "stress_level": 5,
            "willingness_to_talk": 7,
            "engagement_coefficient": 6,
            "emotional_depth": 5,
            "rapport_score": 6
        }
        
        # Initialize state for the ReWOO graph
        initial_state = {
            "task": request.message,
            "conversation_history": user_context["conversation_history"],
            "metrics": mood_metrics
        }
        
        # Run the ReWOO graph
        logger.debug(f"Running ReWOO graph with state: {initial_state}")
        result = rewoo_app.invoke(initial_state)
        
        # Extract the final response and additional metrics
        response_content = result["result"]
        additional_metrics = result.get("additional_metrics", {})
        
        # Update conversation history with the response
        user_context["conversation_history"].append({"role": "assistant", "content": response_content})
        
        # Create response context with additional metrics
        response_context = {
            "user_id": user_id,
            "memory_count": len(user_context["conversation_history"]),
            "user_interests": list(user_context["user_interests"]),
            "additional_metrics": additional_metrics,  # Include the additional metrics
            "user_mood": user_context["user_mood_history"][-1] if user_context["user_mood_history"] else "neutral",
        }
        
        # Create response metadata
        response_metadata = {
            "plan": result["plan_string"],
            "steps_executed": len(result["steps"]),
            "mood_metrics": mood_metrics,
            "additional_metrics": additional_metrics  # Include in metadata as well
        }
        
        logger.debug("Preparing final response...")
        return ChatResponse(
            response=response_content,
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