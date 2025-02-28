from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.api.routes import agent, user, room, message
from db.app import get_db

app = FastAPI(title="Chat API", version="1.0.0", root_path="/api/v1")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include all routers
app.include_router(agent.router)
app.include_router(user.router)
app.include_router(room.router)
app.include_router(message.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chat API"} 

@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # Use text() to wrap the SQL query
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "connected", "test_query": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}