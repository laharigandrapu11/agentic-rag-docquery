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


def retrieve_by_doc_id(doc_id: str) -> list[dict]:
    """Return every stored chunk that belongs to doc_id (no embedding needed)."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    client = get_qdrant_client()
    points, _ = client.scroll(
        collection_name=settings.qdrant_collection_name,
        scroll_filter=Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
        ),
        limit=1000,
        with_payload=True,
    )
    return [p.payload for p in points]
   
def retrieve_filtered(question: str, doc_ids: list[str], top_k: int = 5) -> list[dict]:
    """Semantic search restricted to a specific set of doc_ids."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    model = SentenceTransformer(settings.embedding_model)
    query_vector = model.encode(question).tolist()
    client = get_qdrant_client()
    results = client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        query_filter=Filter(
            should=[
                FieldCondition(key="doc_id", match=MatchValue(value=did))
                for did in doc_ids
            ]
        ),
        limit=top_k,
    ).points
    return [r.payload for r in results]