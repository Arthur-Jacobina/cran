from uuid import UUID
from sqlalchemy.orm import Session
from ..tables.agent import Agent
from typing import Optional, List, Dict, Any

def create_agent(db: Session, agent_data: Dict[str, Any]) -> Agent:
    """Create a new agent"""
    db_agent = Agent(**agent_data)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agent(db: Session, agent_id: UUID) -> Optional[Agent]:
    """Get an agent by ID"""
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    """Get all agents with pagination"""
    return db.query(Agent).offset(skip).limit(limit).all()

def update_agent(db: Session, agent_id: UUID, agent_data: Dict[str, Any]) -> Optional[Agent]:
    """Update an agent"""
    db_agent = get_agent(db, agent_id)
    if db_agent:
        for key, value in agent_data.items():
            setattr(db_agent, key, value)
        db.commit()
        db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: UUID) -> bool:
    """Delete an agent"""
    db_agent = get_agent(db, agent_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
        return True
    return False 