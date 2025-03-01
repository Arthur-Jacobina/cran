import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid
from .entry import Entry
from dotenv import load_dotenv
from datetime import datetime

MAX_TOKENS = 120000.0
AVAILABLE_TOKENS = MAX_TOKENS*0.7

load_dotenv()

class WorkingContext:
    def __init__(self, agent_id: str):
        self.memory = []
        self.system = []
        self.agent_id = agent_id
        self.pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.conversation_history = []
        self.max_history_length = 20

    def __repr__(self):
        return f"WorkingContext(memory={self.memory})"

    def __str__(self):
        return self.__repr__()
        
    def __call__(self) -> str:
        return self.memory
    
    def _shift(self):
        if self.memory:
            return self.memory.pop(0)
        raise ValueError("No memory to shift")
    
    def _add_memory(self, entry: Entry):
        if sum([e.tokens for e in self.memory]) + entry.tokens > AVAILABLE_TOKENS:
            print(f"Not enough tokens to add memory. Current tokens: {sum([e.tokens for e in self.memory])}, available tokens: {AVAILABLE_TOKENS}")
            while sum([e.tokens for e in self.memory]) + entry.tokens > 0.5*AVAILABLE_TOKENS:
                self.insert_to_long_term(self.shift())
            self.memory.append(entry)
            return f"Memory added successfully. Current tokens: {sum([e.tokens for e in self.memory])}, available tokens: {AVAILABLE_TOKENS}"
        self.memory.append(entry)
        return f"Memory added successfully. Current tokens: {sum([e.tokens for e in self.memory])}, available tokens: {AVAILABLE_TOKENS}"

    def _ensure_index_exists(self):
        try:
            indexes = self.pc.list_indexes()
            index_exists = any(index.name == self.agent_id for index in indexes)
            
            if not index_exists:
                print(f"Creating new index: {self.agent_id}")
                self.pc.create_index(
                    name=self.agent_id,
                    dimension=384,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                print(f"Index {self.agent_id} created successfully")
            else:
                print(f"Index {self.agent_id} already exists")
                
            return True
        except Exception as e:
            print(f"Error checking/creating index: {e}")
            return False

    def _insert_to_long_term(self, entry: Entry):
        try:
            if not self._ensure_index_exists():
                return f"Failed to ensure index exists for agent {self.agent_id}"
            
            index = self.pc.Index(name=self.agent_id)
            
            embed = self.model.encode(entry.content)
            
            index.upsert(
                vectors=[
                    {
                        "id": str(uuid.uuid4()),
                        "values": embed,
                        "metadata": {"role": entry.role, "content": entry.content}
                    }
                ],
                namespace=self.agent_id
            )
            return f"Memory inserted to long term memory successfully."
        except Exception as e:
            return f"Error inserting memory to long term memory: {e}"
    
    def _get_from_long_term(self, query: str, top_k: int = 3):
        try:
            if not self._ensure_index_exists():
                return f"No long term memory found for agent {self.agent_id}"
            
            index = self.pc.Index(name=self.agent_id)
            
            embed = self.model.encode(query).tolist()
            
            results = index.query(
                vector=embed,
                top_k=top_k,
                include_metadata=True,
                namespace=self.agent_id
            )
            return results
        except Exception as e:
            return f"Error getting from long term memory: {e}"

    def _add_system_message(self, message: str):
        self.system.append(Entry("system", message))
        return f"System message added successfully."
    
    def _get_system_message(self):
        return self.system
    
    def _remove_system_message(self, message: str):
        self.system = [m for m in self.system if m.content != message]
        return f"System message removed successfully."
    
    def _clear_system_messages(self):
        self.system = []
        return f"System messages cleared successfully."

    def add_conversation_entry(self, role: str, content: str) -> None:
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(entry)
        
        if len(self.conversation_history) > self.max_history_length:
            old_entry = self.conversation_history.pop(0)
            self._insert_to_long_term(Entry(old_entry["role"], old_entry["content"]))
        
        self._add_memory(Entry(role, content))

    def get_conversation_history(self, limit: int = None) -> list:
        if limit is None:
            return self.conversation_history
        return self.conversation_history[-limit:]

    def get_relevant_memories(self, query: str = None, top_k: int = 5) -> list:
        try:
            recent_memories = self.get_conversation_history(limit=top_k)
            
            if query:
                long_term_results = self._get_from_long_term(query, top_k=top_k)
                if isinstance(long_term_results, dict) and 'matches' in long_term_results:
                    for match in long_term_results['matches']:
                        if match['metadata'] not in recent_memories:
                            recent_memories.append(match['metadata'])
            
            return recent_memories[:top_k]
            
        except Exception as e:
            print(f"Error getting relevant memories: {e}")
            return []

