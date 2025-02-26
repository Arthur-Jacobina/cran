from embeddings import embed

class UpsertPipeline:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def __repr__(self):
        return f"UpsertPipeline(vector_store={self.vector_store})"
    
    def __str__(self):
        return self.__repr__()
    
    def __call__(self, text):
        return self.upsert(text)
    
    def upsert(self, text):
        vector = embed(text)
        self.vector_store.add_vector(vector)
        return self.vector_store
    
    def upsert_many(self, texts):
        for text in texts:
            self.upsert(text)
        return self.vector_store
    
    