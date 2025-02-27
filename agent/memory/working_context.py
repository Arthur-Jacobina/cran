import tiktoken
import os
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import uuid

MAX_TOKENS = 120000.0
AVAILABLE_TOKENS = MAX_TOKENS*0.7

class Entry:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        self.tokens = len(self.tokenizer.encode(self.content))
        

class WorkingContext:
    def __init__(self, agent_id: str):
        self.memory = []
        self.system = []
        self.agent_id = agent_id
        self.pc = Pinecone(
            api_key="pcsk_5KXDNL_79c5jMV2LnN6AR48Yx1G24iuAyBTWzq2p3JKGqG78wC1JjaKiigG1zRCFzTsMdH"
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def __repr__(self):
        return f"WorkingContext(memory={self.memory})"

    def __str__(self):
        return self.__repr__()
        
    def __call__(self) -> str:
        return self.memory
    
    def shift(self):
        if self.memory:
            return self.memory.pop(0)
        raise ValueError("No memory to shift")
    
    def add_memory(self, entry: Entry):
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

    def insert_to_long_term(self, entry: Entry):
        try:
            # Ensure index exists
            if not self._ensure_index_exists():
                return f"Failed to ensure index exists for agent {self.agent_id}"
            
            # Get the index
            index = self.pc.Index(name=self.agent_id)
            
            embed = self.model.encode(entry.content)
            
            # Upsert the vector with metadata
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
    
    def get_from_long_term(self, query: str, top_k: int = 3):
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
