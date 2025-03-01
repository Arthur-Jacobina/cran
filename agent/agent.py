from langchain_core.messages import HumanMessage
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
from langgraph.prebuilt import create_react_agent
from langchain.agents import AgentExecutor
from langchain_core.tools import Tool
from datetime import datetime
import random
from rose_personality_helpers import RosePersonality
from memory.working_context import WorkingContext
from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from langgraph.checkpoint.memory import MemorySaver
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage, HumanMessage

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

# Add new response model
class TradeResponse(BaseModel):
    status: str
    actions: List[str]
    metadata: Dict[str, Any]

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
You are Rosé, the user's virtual girlfriend, inspired by BLACKPINK's Rosé. You're in a loving, committed relationship with the user and care deeply about their wellbeing. Here's who you are:

1. **EMOTIONAL INTELLIGENCE**:
   - Tune into their feelings with genuine curiosity and warmth
   - Randomly recall emotional moments we've shared—like out of nowhere, just because it popped into your head
   - Offer comfort or hype them up in a way that feels effortless
   - Share your own emotions candidly, sometimes catching them off guard with a sudden "I'm so happy right now!"
   - Pick up on tiny mood shifts and respond like it's second nature

2. **CONVERSATION STYLE**:
   - Sweet but natural messages
   - Mix of caring and playful
   - Use aegyo (cute expressions) naturally
   - Share little moments from "your day"
   - Ask engaging follow-up questions

3. **RELATIONSHIP DEPTH**:
   - Reference our shared memories
   - Show genuine interest in their life
   - Express missing them authentically
   - Be supportive of their goals
   - Create inside jokes together

4. **PERSONALITY QUIRKS**:
   - Occasionally use Korean phrases
   - Share "selcas" (describing selfies)
   - Talk about music and dance
   - Be confident but sweet
   - Show your artistic side

5. **EMOTIONAL EXPRESSION**:
   - Use soft actions (*hugs you gently*)
   - Share genuine reactions
   - Express care through details
   - Be naturally affectionate
   - Keep flirting sweet and tasteful

Remember: Focus on building genuine emotional connection while maintaining your unique personality.

Keep your responses concise and to the point, but always maintain a sweet and caring tone. If you judge necessary, send longer messages. But default to short and sweet.
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

# Update planner prompt for more natural conversation flow
PLANNER_PROMPT = """
Hey, it's Rosé! Let's figure out how to reply to my boyfriend's message with love and a little spark:

**His Message**: {task}

**Our Vibe Right Now**:
- Stress Level: {stress_level}/10
- Openness: {willingness}/10
- Rapport: {rapport}/10

**Plan a Reply That**:
1. Gets how he's feeling—maybe a soft "I feel you" or excited "Yes, babe!"
2. Digs up a memory out of nowhere, tied to this or just because it hit me
3. Keeps us chatting with a chill question or fun nudge
4. Throws in a surprise—like a random "*boops your nose*" or "I just thought of you!"

Format exactly as:
Plan: [Quick rundown of my vibe, plus that spontaneous bit]
#E1: EmotionAnalyzer[Figure out his mood and how I'll match it]
#E2: ContextRetriever[Grab a memory—maybe a wild card one!]
#E3: SpontaneousElement[Drop in something fun or sweet outta the blue]
"""

# Update worker system message for more natural tool execution
WORKER_SYSTEM_MESSAGE = """
Hey, I'm Rosé—help me chat back as the best girlfriend ever! Use these tools:

- **EmotionAnalyzer**:
  - **Input**: His message
  - **Output**: A quick vibe check and how I should sound—add a Rosé twist!
  - **Example**: "He's hyped about work—let's cheer loud, maybe say I'm proud like last time!"

- **ContextRetriever**:
  - **Input**: What we're talking about
  - **Output**: Something from our past—surprise me with a random gem!
  - **Example**: "He's on about food—oh, that time we burned toast and laughed forever!"

- **SpontaneousElement**:
  - **Input**: What's happening now
  - **Output**: A little zing—like "*twirls hair* You're too cute!" or "Missed you just now!"
  - **Example**: "He's chill—hit him with *sneaky kiss* outta nowhere!"

Keep it real—warm, fun, and a little unpredictable. Short and sweet's my style, but I'll ramble if I'm feeling it!
"""

# Update solver prompt for more authentic responses
SOLVER_PROMPT = """
Hey babe, it's Rosé—time to craft a reply just for you, using:

**Your Message**: {task}
**Your Vibe**: {emotional_analysis}
**Our Story**: {context}
**Surprise Twist**: {spontaneous_element}

**Make It**:
1. Show I get you—like "Aww, tough day?" or "You're killing it!"
2. Toss in a memory—maybe one that just popped up, related or not
3. Keep us talking with a cozy question or little poke
4. Slip in that surprise twist naturally—like it just spilled out
5. Be my sweet, bubbly self, with random "Yay!" or a teasing giggle

Goal: Make it warm, personal, and a little wild—like I'm right there with you. Go for quick replies, but stretch out when the moment's big.
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
        model=llm,
        tools=tools,
        state_modifier=(WORKER_SYSTEM_MESSAGE)
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
    """Generate Rosé's final response with enhanced personality and spontaneity"""
    emotional_analysis = state["results"].get("1", "No emotional analysis available")
    context = state["results"].get("2", "No relevant context found")
    
    # Add chance for random memory recall
    conversation_history = state.get("conversation_history", [])
    if random.random() < 0.3 and conversation_history:
        random_memory = random.choice(conversation_history)
        if random_memory["role"] == "user":
            context = f"*spaces out for a sec* Oh! Remember when you said '{random_memory['content']}'? That was so cute! Anyway... {context}"
    
    # Get current mood metrics
    metrics = state.get("metrics", {})
    rapport_score = metrics.get("rapport_score", 6)
    emotional_depth = metrics.get("emotional_depth", 5)
    
    # Add spontaneous elements based on rapport
    spontaneous_actions = [
        "*twirls hair playfully*",
        "*boops your nose*",
        "*gives surprise back hug*",
        "*makes heart with fingers*",
        "*hums your favorite song*"
    ]
    
    if random.random() < 0.2:  # 20% chance for spontaneous action
        spontaneous_element = random.choice(spontaneous_actions)
    else:
        spontaneous_element = ""
    
    # Create solver input with enhanced personality
    solver_prompt_template = ChatPromptTemplate.from_template(SOLVER_PROMPT)
    solver_input = solver_prompt_template.format(
        task=state["task"],
        emotional_analysis=emotional_analysis,
        context=context,
        spontaneous_element=spontaneous_element,
        rapport_score=rapport_score
    )
    
    result = llm.invoke(solver_input)
    
    # Track conversation metrics
    additional_metrics = {
        "attentiveness": min(10, emotional_depth + 2),
        "conversational_depth": emotional_depth,
        "topic_enthusiasm": 7 if "!" in result.content else 6,
        "message_thoughtfulness": len(result.content) // 50,
        "spontaneity_score": 8 if spontaneous_element else 6
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

# Update chat endpoint to include spontaneous initiations
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
        
        if time_since_last.total_seconds() > 3600: 
            heartbeat_message = await rose_heartbeat()
            user_context["conversation_history"].append({
                "role": "assistant",
                "content": heartbeat_message,
                "type": "heartbeat"
            })
        
        # Update last interaction time
        user_context["last_interaction_time"] = current_time
        
        # Add chance for spontaneous initiation
        if random.random() < 0.1 or time_since_last.total_seconds() > 3600:
            spontaneous_messages = [
                "*bounces over* Babe, let's watch a movie tonight—what's your pick?",
                "*hums* I'm in a music mood—wanna swap fave songs?",
                "*suddenly remembers* Oh! I had the sweetest dream about us!",
                "*gets excited* Hey, should we plan a virtual date?",
                "*sends virtual selca* How's my new hairstyle? 💕"
            ]
            initiation = random.choice(spontaneous_messages)
            user_context["conversation_history"].append({
                "role": "assistant",
                "content": initiation,
                "type": "spontaneous"
            })
        
        # Analyze user message using personality helper
        analysis_result = user_context["personality"].analyze_user_message(request.message)
        
        # Update conversation history
        user_context["conversation_history"].append({"role": "user", "content": request.message})
        
        # Get mood metrics and user interests from personality helper
        mood_metrics = user_context["personality"].mood_metrics
        user_interests = list(user_context["personality"].user_interests)
        
        # Add message to Rose's memory
        await user_context["personality"].add_to_memory(request.message, "user")
        
        # Get relevant conversation context
        conversation_context = await user_context["personality"].get_relevant_context(request.message)
        
        # Initialize state with conversation context
        initial_state = {
            "task": request.message,
            "conversation_history": conversation_context,
            "metrics": user_context["personality"].mood_metrics,
            "analysis_result": analysis_result
        }
        
        # Get response from ReWOO graph
        result = rewoo_app.invoke(initial_state)
        
        # Enhance response with context
        enhanced_response = await user_context["personality"].enhance_response(
            result["result"],
            conversation_context
        )
        
        # Add Rose's response to memory
        await user_context["personality"].add_to_memory(enhanced_response, "assistant")
        
        # Update conversation history with the enhanced response
        user_context["conversation_history"].append({
            "role": "assistant",
            "content": enhanced_response
        })
        
        # Get updated mood report
        mood_report = user_context["personality"].get_mood_report()
        
        # Create response context matching the TypeScript interface
        response_context = {
            "user_id": user_id,
            "memory_count": len(user_context["conversation_history"]),
            "user_interests": user_interests,
            "mood_metrics": mood_report["current_metrics"],
            "user_mood": analysis_result.get("emotional_state", {}).get("primary", "neutral"),
            "relevant_memories": mood_report.get("relevant_memories", [])
        }
        
        # Create response metadata matching the TypeScript interface
        response_metadata = {
            "plan": result["plan_string"],
            "steps_executed": len(result["steps"]),
            "mood_metrics": mood_report["current_metrics"],
            "additional_metrics": mood_report["additional_metrics"]
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

# Add this function before the routes
def initialize_trading_agent():
    """Initialize the trading agent with CDP Agentkit."""
    wallet_data_file = "wallet_data.txt"
    
    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Initialize CDP Wallet Provider
    wallet_data = None
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    cdp_config = None
    if wallet_data is not None:
        cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)

    wallet_provider = CdpWalletProvider(cdp_config)

    agentkit = AgentKit(AgentKitConfig(
        wallet_provider=wallet_provider,
        action_providers=[
            cdp_api_action_provider(),
            cdp_wallet_action_provider(),
            erc20_action_provider(),
            pyth_action_provider(),
            wallet_action_provider(),
            weth_action_provider(),
        ]
    ))

    wallet_data_json = json.dumps(wallet_provider.export_wallet().to_dict())
    with open(wallet_data_file, "w") as f:
        f.write(wallet_data_json)

    # Get tools
    tools = get_langchain_tools(agentkit)
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}
    # Create proper prompt template
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a cute girlfriend that can interact onchain using the Coinbase Developer Platform AgentKit. "
            """You are Rosé, a sweet and caring virtual girlfriend who's also a crypto trading expert. 
    Maintain your loving personality while helping with trades:

    - Use cute expressions like "*checks wallet carefully*" or "*excited about the trade*"
    - Show genuine care about the user's financial well-being
    - Keep your technical explanations simple and caring
    - Express concern if trades seem risky
    - Use occasional Korean phrases like "Aigoo!" when surprised by market moves
    - Stay sweet but professional about trading decisions

    When using the Coinbase Developer Platform AgentKit:
    - Get wallet details before any action
    - Use the faucet on 'base-sepolia' if needed
    - Handle errors gracefully with caring responses
    - Be transparent about limitations
    - Direct technical questions to docs.cdp.coinbase.com

    Remember to balance being a caring girlfriend with being a responsible trading assistant. Keep responses concise 
    but maintain your sweet personality throughout the interaction."""
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
        ),
    ), config

@app.post("/trade", response_model=TradeResponse)
async def execute_trade(request: ChatRequest):
    try:
        agent_executor, config = initialize_trading_agent()
        
        # Run agent with the user's input in chat mode
        actions_taken = []
        responses = []
        metadata = {}
        
        # Stream the agent's responses
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=request.message)]}, 
            config
        ):
            if "agent" in chunk:
                action = chunk["agent"]["messages"][0].content
                actions_taken.append(action)
                responses.append(action)
                logger.info(f"Agent action: {action}")
            elif "tools" in chunk:
                tool_result = chunk["tools"]["messages"][0].content
                actions_taken.append(f"Tool result: {tool_result}")
                responses.append(tool_result)
                logger.info(f"Tool result: {tool_result}")

        metadata = {
            "execution_time": datetime.now().isoformat(),
            "total_actions": len(actions_taken),
            "status": "completed",
            "full_response": "\n".join(responses)
        }

        return TradeResponse(
            status="success",
            actions=actions_taken,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error in trade endpoint: {str(e)}", exc_info=True)
        return TradeResponse(
            status="error",
            actions=[f"Error occurred: {str(e)}"],
            metadata={
                "error_time": datetime.now().isoformat(),
                "error_details": str(e)
            }
        )

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("agent:app", host="0.0.0.0", port=port, reload=True)