# Populated in F4 - Agentic Multi-hop Reasoning
# Extended in F6 - Summarize and Compare

from app.retrieval.retriever import retrieve


def rag_search(question: str, top_k: int = 5) -> list[dict]:
    """Retrieve the top-k most relevant chunks for a question.

    Thin wrapper around the Qdrant retriever so that nodes (and later
    LangGraph tool-calling in F6) talk to a single named function rather
    than importing the retriever directly.
    """
    return retrieve(question, top_k)