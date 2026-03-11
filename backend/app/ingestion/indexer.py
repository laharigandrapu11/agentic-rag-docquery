# Populated in F1 - Document Upload and Ingestion
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.schemas import DocumentMeta


def get_qdrant_client()->QdrantClient:
    client = QdrantClient(url=settings.qdrant_url)
    if not client.collection_exists(settings.qdrant_collection_name):
        client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    return client


def upsert_chunks(chunks:list[dict]):
    client = get_qdrant_client()
    model = SentenceTransformer(settings.embedding_model)

    points = []
    for chunk in chunks:
        embedding = model.encode(chunk["text"])
        points.append(PointStruct(id=str(uuid4()), vector=embedding.tolist(), payload=chunk))
        
    client.upsert(
        collection_name=settings.qdrant_collection_name,
        points=points,
    )

def get_all_documents()->list[DocumentMeta]:
    client = get_qdrant_client()
    points, _ = client.scroll(
        collection_name=settings.qdrant_collection_name,
        limit=1000,
        with_payload=True,
    )

    # Group by doc_id
    from collections import defaultdict
    groups = defaultdict(list)
    for point in points:
        groups[point.payload["doc_id"]].append(point)

    result = []
    for doc_id, pts in groups.items():
        p = pts[0].payload
        result.append(DocumentMeta(
            doc_id=doc_id,
            filename=p.get("source", ""),
            source=p.get("source", ""),
            chunk_count=len(pts),
            created_at=p.get("created_at", ""),
        ))
    return result


def delete_document(doc_id:str)-> int:
    client = get_qdrant_client()
    return client.delete(
        collection_name=settings.qdrant_collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))],
        ),
    )

