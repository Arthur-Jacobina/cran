from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .memory.working_context import WorkingContext
from .memory.entry import Entry
from .agent import agent_executor

app = FastAPI(title="Agent API", description="API for the agent", root_path="/api/v1")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    agent_id: str

class SystemMessageRequest(BaseModel):
    message: str
    agent_id: str

class LongTermMemoryRequest(BaseModel):
    entry: Entry
    agent_id: str

agent_contexts = {}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if request.agent_id not in agent_contexts:
            agent_contexts[request.agent_id] = WorkingContext(request.agent_id)
        
        context = agent_contexts[request.agent_id]
        
        for message in request.messages:
            entry = Entry(message.role, message.content)
            context._add_memory(entry)

        response = agent_executor.invoke({
            "messages": [(msg.role, msg.content) for msg in request.messages]
        })
        entry = Entry("assistant", response)
        context._add_memory(entry)
        
        return {"response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system/add")
async def add_system_message(request: SystemMessageRequest):
    try:
        if request.agent_id not in agent_contexts:
            agent_contexts[request.agent_id] = WorkingContext(request.agent_id)
        
        context = agent_contexts[request.agent_id]
        result = context._add_system_message(request.message)
        return {"status": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/{agent_id}")
async def get_system_messages(agent_id: str):
    try:
        if agent_id not in agent_contexts:
            return {"messages": []}
        
        context = agent_contexts[agent_id]
        messages = context._get_system_message()
        return {"messages": [{"role": m.role, "content": m.content} for m in messages]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/system/{agent_id}")
async def clear_system_messages(agent_id: str):
    try:
        if agent_id not in agent_contexts:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        context = agent_contexts[agent_id]
        result = context._clear_system_messages()
        return {"status": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/long-term")
async def query_long_term_memory(agent_id: str, query: str, top_k: Optional[int] = 3):
    try:
        if agent_id not in agent_contexts:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        context = agent_contexts[agent_id]
        results = context._get_from_long_term(query, top_k)
        return {"results": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/long-term")
async def add_long_term_memory(request: LongTermMemoryRequest):
    try:
        if request.agent_id not in agent_contexts:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        context = agent_contexts[request.agent_id]
        result = context._insert_to_long_term(request.entry)
        return {"status": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
