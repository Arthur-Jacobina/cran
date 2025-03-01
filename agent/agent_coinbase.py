from fastapi import FastAPI, HTTPException
import os

# Import Coinbase AgentKit components
from coinbase_agentkit import AgentKit, AgentKitConfig, CdpWalletProvider, CdpWalletProviderConfig, cdp_api_action_provider

# Import LangChain integration for Coinbase AgentKit
from coinbase_agentkit_langchain import get_langchain_tools

# Import LangChain/OpenAI components and React agent creator
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


app = FastAPI(title="Coinbase Agent API")

# Configure Coinbase wallet provider using environment variables
wallet_provider = CdpWalletProvider(CdpWalletProviderConfig(
    api_key_name=os.getenv("COINBASE_API_KEY_NAME", "default_key_name"),
    api_key_private=os.getenv("COINBASE_API_KEY_PRIVATE", "default_api_key"),
    network_id=os.getenv("COINBASE_NETWORK_ID", "base-mainnet")
))

# Create AgentKit instance with the wallet provider and action providers
agent_kit = AgentKit(AgentKitConfig(
    wallet_provider=wallet_provider,
    action_providers=[
        cdp_api_action_provider(
            api_key_name=os.getenv("COINBASE_API_KEY_NAME", "default_key_name"),
            api_key_private=os.getenv("COINBASE_API_KEY_PRIVATE", "default_api_key")
        )
    ]
))

# Get LangChain tools based on the configured AgentKit
tools = get_langchain_tools(agent_kit)

# Initialize the LLM (ensure OPENAI_API_KEY is set in the environment)
llm = ChatOpenAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))

# Create a React Agent using the LLM and Coinbase tools
agent = create_react_agent(llm=llm, tools=tools)


@app.post("/coinbase_chat")
async def coinbase_chat(query: str):
    """Endpoint to interact with the Coinbase agent."""
    try:
        # Invoke the agent with the provided query
        result = agent.invoke({"input": query})
        return {"response": result.get("output", "No output returned")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
