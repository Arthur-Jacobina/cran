from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ..structures.storage_entities import StorageEntity
from server.structures.encrypted_vector_store import EncryptedVectorStore, Entry
from server.structures.upsert_pipeline import UpsertPipeline
import tenseal as ts

app = FastAPI(title="Cranberry Storage", root_path="/api/v1/")

storage = StorageEntity()

class VectorStoreInput(BaseModel):
    context: ts.Context

class VectorStoreResponse(BaseModel):
    id: str
    message: str

class VectorStoreUpdate(BaseModel):
    id: str
    context: ts.Context

@app.post("/vector-stores", response_model=VectorStoreResponse)
async def create_vector_store(input: VectorStoreInput):
    '''
    Create a new vector store
    @param input: VectorStoreInput
        context: tenseal.Context
    @return VectorStoreResponse
        id: str
        message: str
    '''
    try:
        vector_store = EncryptedVectorStore(input.context)
        store_id = storage.insert(vector_store)
        return {"id": store_id, "message": "Vector store created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-stores/{store_id}")
async def get_vector_store(store_id: str):
    '''
    Get a vector store by id
    @param store_id: str
    @return VectorStoreResponse
        vector_store: EncryptedVectorStore
    '''
    try:
        if store_id not in storage:
            raise HTTPException(status_code=404, detail="Vector store not found")
        return {"vector_store": storage.get(store_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-stores")
async def list_vector_stores():
    '''
    List all vector stores
    @return VectorStoreResponse
        vector_stores: list[EncryptedVectorStore]
    '''
    try:
        stores = storage.get_all()
        return {"vector_stores": stores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/vector-stores/{store_id}")
async def update_vector_store(store_id: str, input: EncryptedVectorStore) -> VectorStoreResponse:
    '''
    Update a vector store by id
    @param store_id: str
    @param input: EncryptedVectorStore
        context: tenseal.Context
        vectors: list[Entry]
        id: str
    @return VectorStoreResponse
        message: str
    '''
    try:
        if store_id not in storage:
            raise HTTPException(status_code=404, detail="Vector store not found")
        storage.update(store_id, input)
        return {"id": store_id, "message": f"Vector store {store_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vector-stores/{store_id}")
async def delete_vector_store(store_id: str):
    '''
    Delete a vector store by id
    @param store_id: str
    @return VectorStoreResponse
        message: str
    '''
    try:
        if store_id not in storage:
            raise HTTPException(status_code=404, detail="Vector store not found")
        storage.delete(store_id)
        return {"message": "Vector store deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vector-stores/{store_id}/add-vector")
async def add_vector(store_id: str, input: Entry) -> VectorStoreResponse:
    '''
    Add a vector to a vector store
    @param store_id: str
    @param input: Entry
        encrypted_text: str
        encrypted_vector: tenseal.ckks_vector
    @return VectorStoreResponse
        message: str
    '''
    try:
        if store_id not in storage:
            raise HTTPException(status_code=404, detail="Vector store not found")
        vector_store = storage.get(store_id)
        upsert_pipeline = UpsertPipeline(vector_store)
        vector_id = upsert_pipeline(input)
        return {"id": vector_id, "message": f"Vector added successfully to vector store {store_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vector-stores/{store_id}/similarity-search")
async def similarity_search(store_id: str, input: Entry, top_k: int = 3) -> VectorStoreResponse:
    '''
    Search for vectors in a vector store by similarity
    @param store_id: str
    @param input: Entry
        encrypted_text: str
        encrypted_vector: tenseal.ckks_vector
    @param top_k: int
        The number of results to return
    @return VectorStoreResponse
        results: {id: str, encrypted_text: str, similarity: float}
    '''
    try:
        if store_id not in storage:
            raise HTTPException(status_code=404, detail="Vector store not found")
        vector_store = storage.get(store_id)
        similarity = vector_store.cosine_similarity(input.encrypted_vector, top_k)
        return {"results": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vector-stores")
async def clear_vector_stores():
    '''
    Clear all vector stores
    @return VectorStoreResponse
        message: str
    @warning: This will delete all vector stores, use with caution
    '''
    try:
        storage.clear()
        return {"message": "All vector stores cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    '''
    Check the health of the server
    @return HealthCheckResponse
        status: str
        store_count: int
    '''
    return {"status": "healthy", "store_count": len(storage)}