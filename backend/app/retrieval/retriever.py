# Populated in F2 - Basic Q&A
from sentence_transformers import SentenceTransformer
from app.ingestion.indexer import get_qdrant_client
from app.core.config import settings

def retrieve(question:str, top_k:int = 5) -> list[dict]:
    model = SentenceTransformer(settings.embedding_model)
    query_vector = model.encode(question).tolist()

    client = get_qdrant_client()

    # .query_points() is the modern API in qdrant-client >= 1.7 (replaces .search())
    results = client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        limit=top_k,
    ).points

    return [result.payload for result in results]
    
   