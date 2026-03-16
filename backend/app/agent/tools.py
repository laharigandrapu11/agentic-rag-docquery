# Populated in F4 - Agentic Multi-hop Reasoning
# Extended in F6 - Summarize and Compare

from app.retrieval.retriever import retrieve, retrieve_by_doc_id, retrieve_filtered


def rag_search(question: str, top_k: int = 5) -> list[dict]:
    """Retrieve the top-k most relevant chunks for a question.

    Thin wrapper around the Qdrant retriever so that nodes (and later
    LangGraph tool-calling in F6) talk to a single named function rather
    than importing the retriever directly.
    """
    return retrieve(question, top_k)

def get_doc_chunks(doc_id: str) -> list[dict]:
    """Return all stored chunks for a single document (used by summarize)."""
    return retrieve_by_doc_id(doc_id)
    
def filtered_rag_search(question: str, doc_ids: list[str], top_k: int = 5) -> list[dict]:
    """Semantic search limited to the supplied doc_ids (used by compare)."""
    return retrieve_filtered(question, doc_ids, top_k)