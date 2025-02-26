from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .embeddings import embed
from .encrypted_vector_store import EncryptedVectorStore
from .upsert import UpsertPipeline
import tenseal as ts

app = FastAPI(title="Cranberry API")

class TextInput(BaseModel):
    text: str

class TextsInput(BaseModel):
    texts: List[str]

class SearchResult(BaseModel):
    id: str
    similarity: float

class VectorStoreInput(BaseModel):
    context: ts.Context

@app.post("/create-vector-store")
async def create_vector_store(input: VectorStoreInput):
    vector_store = EncryptedVectorStore(input.context)
    upsert_pipeline = UpsertPipeline(vector_store)
    return {"vector_store": vector_store}

@app.post("/upsert")
async def upsert_text(input: TextInput, vector_store: EncryptedVectorStore):
    try:
        upsert_pipeline = UpsertPipeline(vector_store)
        vector_id = upsert_pipeline(input.text)
        return {"vector_id": vector_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upsert-batch")
async def upsert_texts(input: TextsInput):
    try:
        vector_store = upsert_pipeline.upsert_many(input.texts)
        return {"message": f"Successfully inserted {len(input.texts)} texts"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=List[SearchResult])
async def search(input: TextInput, top_k: Optional[int] = 3):
    try:
        query_vector = embed(input.text)
        results = vector_store.cosine_similarity(query_vector, top_k=top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
