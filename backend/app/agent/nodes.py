# Populated in F4 - Agentic Multi-hop Reasoning

from langchain_core.prompts import PromptTemplate

from app.core.llm_factory import get_llm
from app.agent.tools import rag_search
from app.agent.prompts import ROUTER_PROMPT, DECOMPOSER_PROMPT


def router_node(state: dict) -> dict:
    """Classify the question as 'simple' or 'complex'.

    Uses the small fast model — binary classification needs no reasoning
    capacity beyond understanding the question's structure.
    """
    llm = get_llm(state.get("provider", "groq"), small_model=True)
    prompt = PromptTemplate(template=ROUTER_PROMPT, input_variables=["question"])
    chain = prompt | llm

    raw = chain.invoke({"question": state["question"]})
    raw_text = raw.content.strip().lower()

    # Partial match handles "Simple." / "COMPLEX query" / etc.
    # Only falls back to complex on truly unrecognisable output
    if "simple" in raw_text:
        decision = "simple"
    elif "complex" in raw_text:
        decision = "complex"
    else:
        decision = "complex"

    return {
        "route": decision,
        "hop_traces": state.get("hop_traces", []) + [
            {"node": "router", "data": {"decision": decision}}
        ],
    }


def decomposer_node(state: dict) -> dict:
    """Break a complex question into 2-4 focused sub-questions.

    Uses the full model — the quality of sub-questions directly determines
    what gets retrieved from Qdrant, so this step earns the bigger model.
    """
    llm = get_llm(state.get("provider", "groq"), small_model=False)
    prompt = PromptTemplate(template=DECOMPOSER_PROMPT, input_variables=["question"])
    chain = prompt | llm

    raw = chain.invoke({"question": state["question"]})

    sub_questions = []
    for line in raw.content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading "1. " / "2) " / "- " / "* " etc.
        for prefix in ["1.", "2.", "3.", "4.", "1)", "2)", "3)", "4)", "-", "*"]:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
                break
        if line:
            sub_questions.append(line)

    return {
        "sub_questions": sub_questions,
        "hop_traces": state.get("hop_traces", []) + [
            {"node": "decomposer", "data": {"sub_questions": sub_questions}}
        ],
    }


def rag_retrieve_node(state: dict) -> dict:
    """Retrieve relevant chunks from Qdrant.

    Simple route  → one retrieval call for the original question.
    Complex route → one retrieval call per sub-question; results are merged
                    and deduplicated by chunk text so the synthesizer never
                    sees the same passage cited twice.
    No LLM involved — purely a Qdrant vector search.
    """
    top_k = state.get("top_k", 5)

    if state.get("route") == "complex" and state.get("sub_questions"):
        seen: set[str] = set()
        merged: list[dict] = []
        for sq in state["sub_questions"]:
            for chunk in rag_search(sq, top_k):
                text = chunk.get("text", "")
                if text not in seen:
                    seen.add(text)
                    merged.append(chunk)
        retrieved = merged
    else:
        retrieved = rag_search(state["question"], top_k)

    return {
        "retrieved_chunks": retrieved,
        "hop_traces": state.get("hop_traces", []) + [
            {"node": "rag_retrieve", "data": {"chunks_found": len(retrieved)}}
        ],
    }