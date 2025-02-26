from encryption.encrypted_vector_store import EncryptedVectorStore

class StorageEntity:
    def __init__(self):
        self.row = {}

    def __repr__(self):
        return f"StorageEntity(row={self.row})"
    
    def insert(self, encrypted_vector_store: EncryptedVectorStore):
        id = encrypted_vector_store.id
        self.row[id] = encrypted_vector_store
        return f"Vector store {id} created"
    
    def __len__(self):
        return len(self.row)
    
    def __contains__(self, id: str):
        return id in self.row
    
    def __iter__(self):
        return iter(self.row)
    
    def delete(self, id: str):
        del self.row[id]
        return f"Vector store {id} deleted"
        
    def get(self, id: str) -> EncryptedVectorStore:
        return self.row[id]
    
    def get_all(self) -> list[EncryptedVectorStore]:
        return list(self.row.values())
    
    def update(self, id: str, encrypted_vector_store: EncryptedVectorStore):
        self.row[id] = encrypted_vector_store
        return encrypted_vector_store
        
    def clear(self):
        self.row = {}
        return "All vector stores deleted"



        
        