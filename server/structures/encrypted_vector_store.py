from server.structures.value import Value
import tenseal as ts
import uuid

class Entry:
    def __init__(self, encrypted_text: str, encrypted_vector: ts.ckks_vector):
        self.encrypted_text = encrypted_text
        self.encrypted_vector = encrypted_vector
    
class EncryptedVectorStore:
    def __init__(self, context):
        self.id = str(uuid.uuid4())
        self.vectors = {}
        self.context = ts.context_from(context.serialize(save_secret_key=True))
        
    def add_vector(self, entry: Entry):
        entry_to_value = Value(entry.encrypted_vector, self.context)
        self.vectors[entry_to_value.index] = zip(entry.encrypted_text, entry_to_value)
        return entry_to_value.index
    
    def get_vector(self, vector_id):
        if vector_id in self.vectors:
            return self.vectors[vector_id]
        else:
            raise ValueError(f"Vector with ID {vector_id} not found")
    
    def cosine_similarity(self, query_vector, top_k=3):
        if not isinstance(query_vector, Value):
            encrypted_query = ts.ckks_vector(self.context, query_vector)
            query_vector = Value(encrypted_query, self.context)
        
        results = []
        for vector_id, (encrypted_text, vector) in self.vectors.items():
            similarity = (vector.dot(query_vector)).decrypt()[0]
            results.append({
                "id": vector_id,
                "text": encrypted_text,
                "similarity": abs(similarity)
            })
        results = sorted(results, key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
        
        