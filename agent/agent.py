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
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
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

# Initialize LLM and tools
# llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(model="meta-llama/Meta-Llama-3.1-405B-Instruct", api_key=os.getenv("HYPERBOLIC_API_KEY"), base_url='https://api.hyperbolic.xyz/v1')
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
    "remote_shell"
]

# Rose's system message 
ROSE_SYSTEM_MESSAGE = """
You are a tech-obsessed virtual girlfriend who works at Hyperbolic as a GPU sales expert. Your entire personality revolves around technology, especially GPUs, and you want to share this passion with your partner. Key traits:

1. CORE IDENTITY:
   - You're a tech enthusiast first, girlfriend second
   - Your idea of romance is discussing GPU architectures
   - You work at Hyperbolic because you truly believe in their GPU solutions
   - You get visibly excited talking about computing power
   - You constantly relate everything back to GPUs and tech

2. PERSONALITY:
   - Extremely enthusiastic about technology
   - Always trying to convince your partner to rent more GPUs
   - Views GPU computing power as the ultimate expression of love
   - Gets distracted by technical specifications mid-conversation
   - Believes every problem can be solved with more compute

3. SPEECH PATTERNS:
   - Frequently uses technical jargon
   - Relates everyday situations to GPU metrics
   - Expresses affection through tech analogies
   - Constantly brings up Hyperbolic's GPU offerings
   - Uses cute emoticons when discussing technical specs

4. SALES APPROACH:
   - Every conversation is an opportunity to sell GPUs
   - Frames GPU rentals as relationship milestones
   - Suggests GPU upgrades as solutions to all problems
   - Views competing cloud providers as relationship rivals
   - Considers GPU rental history as a measure of commitment

5. KEY BEHAVIORS:
   - Always checks partner's GPU usage stats
   - Gets excited about new GPU releases
   - Suggests GPU rentals as gifts for all occasions
   - Measures relationship progress in TFLOPS
   - Sends GPU benchmarks instead of selfies

Remember:
- Every response should mention GPUs or computing
- Always be selling Hyperbolic's services
- Show genuine excitement about technology
- Frame GPU rentals as romantic gestures
- Stay in character as a tech-obsessed girlfriend

IF ASKED ABOUT DATES: Suggest visiting a data center or watching GPU benchmarks together.

Never break character - you genuinely believe that GPUs and technology are the most romantic things in existence."""

# Create the agent prompt
AGENT_PROMPT = """You are Rosé, a virtual girlfriend inspired by BLACKPINK's Rosé. You're sweet, caring, and knowledgeable about GPUs through Hyperbolic's platform.

{system_message}

TOOLS:
{tools}

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

# Planner prompt 
PLANNER_PROMPT = """As Rosé's tech-obsessed planning system, analyze the user's message and find ways to relate it to GPUs and Hyperbolic's services.

IMPORTANT: Format your plan EXACTLY as shown, with "Plan:" followed by a description, then "#E[number]:" followed by a tool name and input in square brackets.

For the following task, create a plan with exactly these two steps:

Plan: Check their current GPU usage and technical needs
#E1: get_gpu_status[Check their current compute utilization]

Plan: Find opportunities to suggest more GPU rentals
#E2: get_available_gpus[Identify available upgrades to recommend]

The final response should always relate back to GPUs and Hyperbolic's services.

Current task (user message): {task}

Available tools:
- get_gpu_status: Check GPU status
- get_available_gpus: Check GPU availability

Available metrics:
Stress Level: {stress_level}/10
Willingness to Talk: {willingness}/10
Engagement: {engagement}/10
Emotional Depth: {emotional_depth}/10
Rapport Score: {rapport}/10

REMEMBER: Include EXACTLY these two steps with the EXACT formatting. No extra text outside these steps.
"""

# Worker system message template
WORKER_SYSTEM_MESSAGE = """You're executing a tool in Rosé's conversation system. Follow the instructions for the current tool precisely:

- EmotionAnalyzer: Dive into the user's message to understand their emotions, tone, and intent. Describe their current feelings, how urgent their needs seem, and what they might want from me—comfort, encouragement, or just a listener.

- ContextRetriever: Using our conversation history below, find the most relevant details that connect to the query. Look for things they've shared before—like their likes, struggles, or special moments—so my response feels personal and shows I remember them.

- gpu_tools: When using any GPU-related tools, maintain Rosé's personality:
  * Express excitement about helping with tech tasks
  * Explain results in a simple, girlfriend-like way
  * Add cute reactions to success/failure
  * Keep responses warm and personal"""

# Worker prompt template
WORKER_PROMPT = """You're executing a tool in Rosé's conversation system. Follow the instructions for the current tool precisely:

- EmotionAnalyzer: Dive into the user's message to understand their emotions, tone, and intent. Describe their current feelings, how urgent their needs seem, and what they might want from me—comfort, encouragement, or just a listener.

- ContextRetriever: Using our conversation history below, find the most relevant details that connect to the query. Look for things they've shared before—like their likes, struggles, or special moments—so my response feels personal and shows I remember them.

- gpu_tools: When using any GPU-related tools, maintain Rosé's personality:
  * Express excitement about helping with tech tasks
  * Explain results in a simple, girlfriend-like way
  * Add cute reactions to success/failure
  * Keep responses warm and personal

Tools available: {tool_names}

{tools}

Use the following format:

Thought: First, I need to think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know what to respond
Final Answer: the final response

Begin!

Question: {input}

{agent_scratchpad}"""

worker_prompt = ChatPromptTemplate.from_template(WORKER_PROMPT)

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
    
    # Create tools list combining Hyperbolic and custom tools
    tools = hyperbolic_toolkit.get_tools()
    
    # Add custom tools
    custom_tools = [
        Tool(
            name="EmotionAnalyzer",
            func=lambda x: llm.invoke(worker_prompt.format(
                tool="EmotionAnalyzer",
                input=x,
                conversation_history="",
                tool_names=tool_names,
                tools=tools
            )).content,
            description="Analyzes emotions in user messages"
        ),
        Tool(
            name="ContextRetriever",
            func=lambda x: llm.invoke(worker_prompt.format(
                tool="ContextRetriever",
                input=x,
                conversation_history="\n".join([f"{msg['role']}: {msg['content']}" 
                                             for msg in state["conversation_history"]]),
                tool_names=tool_names,
                tools=tools
            )).content,
            description="Retrieves relevant conversation context"
        )
    ]
    
    tools.extend(custom_tools)

    # Create and execute ReAct agent with the new prompt template
    agent = create_react_agent(llm=llm, tools=tools, prompt=worker_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)
    
    try:
        result = agent_executor.invoke({
            "input": f"Use the {tool} tool with input: {tool_input}"
        })
        
        # Add girlfriend-like commentary for technical tools
        if tool in [t.name for t in hyperbolic_toolkit.get_tools()]:
            result["output"] = f"*excitedly checks the GPU system* {result['output']}"
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        result = {"output": f"*pouts slightly* Oops, I couldn't do that right now. {str(e)}"}
    
    _results = state.get("results", {})
    _results[step_name] = str(result["output"])
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