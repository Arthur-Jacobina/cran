from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...crud import agent as agent_crud
from ...app import get_db
from ..schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/", response_model=AgentResponse)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_crud.create_agent(db, agent.dict())

@router.get("/{agent_id}", response_model=AgentResponse)
def read_agent(agent_id: UUID, db: Session = Depends(get_db)):
    db_agent = agent_crud.get_agent(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.get("/", response_model=List[AgentResponse])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return agent_crud.get_agents(db, skip=skip, limit=limit)

@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: UUID, agent: AgentUpdate, db: Session = Depends(get_db)):
    db_agent = agent_crud.update_agent(db, agent_id, agent.dict(exclude_unset=True))
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.delete("/{agent_id}")
def delete_agent(agent_id: UUID, db: Session = Depends(get_db)):
    success = agent_crud.delete_agent(db, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"} 