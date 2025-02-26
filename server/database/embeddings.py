from sentence_transformers import SentenceTransformer

def embed(text, model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    return model.encode(text)

