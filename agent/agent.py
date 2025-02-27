from langchain import hub
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
import os

load_dotenv() 

tools = []
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
prompt = "You are a lovely girlfriend."
agent_executor = create_react_agent(llm, tools, prompt=prompt)

print(agent_executor.invoke({"messages": [("user", "who is the winnner of the us open")]}))