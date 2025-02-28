from tables.base import Base, engine
from tables.user import User
from tables.agent import Agent
from tables.room import Room
from tables.messages import Message

def create_all_tables():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_all_tables() 