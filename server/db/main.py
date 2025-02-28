from fastapi import FastAPI
from db.api.routes import agent, user, room, message
from db.app import get_db

app = FastAPI(title="Chat API", version="1.0.0")

# Include all routers
app.include_router(agent.router)
app.include_router(user.router)
app.include_router(room.router)
app.include_router(message.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Chat API"} 