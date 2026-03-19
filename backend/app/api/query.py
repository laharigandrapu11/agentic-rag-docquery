# Populated in F2 - Basic Q&A
# Extended in F3 - Streaming and Citations
# Extended in F4 - Agentic Multi-hop Reasoning
# Extended in F6 - Summarize and Compare

import json
from fastapi import APIRouter, Request
from app.security.rate_limiter import enforce_rate_limit
from fastapi.responses import StreamingResponse
from langchain_core.prompts import PromptTemplate

from app.schemas import QueryRequest, CitationChunk, SummarizeRequest, CompareRequest
from app.core.llm_factory import get_llm
from app.agent.graph import compiled_graph, summarize_graph, compare_graph
from app.agent.prompts import QA_PROMPT, SUMMARIZE_REDUCE_PROMPT, COMPARE_PROMPT
from app.agent.memory import get_history, append_turn, clear_session as _clear_session

router = APIRouter()

@router.post("/query")
async def query(req: Request, request: QueryRequest):

    enforce_rate_limit(
        request=req,
        key_suffix=request.session_id,
        limit=60,
        window_seconds=60,
    )
    async def event_stream():

        # ----------------------------------------------------------------
        # Step 1: run the agentic graph (router → decomposer? → rag_retrieve)
        #
        # astream(state, stream_mode="updates") yields one dict per node:
        #   { "node_name": { ...keys that node returned... } }
        # This lets us emit a hop_trace SSE event as each node completes,
        # so the frontend sees the reasoning chain building up in real time
        # before the first answer token arrives.
        # ----------------------------------------------------------------
                # Load prior turns for this session to give the LLM conversation context
        history = get_history(request.session_id) if request.session_id else []
        history_text = (
            "\n".join(
                f"{'User' if t['role'] == 'user' else 'Assistant'}: {t['content']}"
                for t in history
            )
            if history else "(no previous conversation)"
        )
        initial_state = {
            "question": request.question,
            "provider": request.provider,
            "top_k": request.top_k,
            "route": "",
            "sub_questions": [],
            "retrieved_chunks": [],
            "hop_traces": [],
            "doc_ids": request.doc_ids,  # None = search all docs; list = filter to selected docs
        }

        # final_state accumulates the full state as nodes complete
        final_state = dict(initial_state)

        async for updates in compiled_graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in updates.items():
                # Merge this node's output into our local final_state
                final_state.update(node_output)

                # Each node appends its own entry to hop_traces.
                # We emit only the latest entry (this node's trace) as SSE.
                hop_entries = node_output.get("hop_traces", [])
                if hop_entries:
                    latest = hop_entries[-1]
                    yield f'data: {json.dumps({"type": "hop_trace", "node": latest["node"], "data": latest["data"]})}\n\n'

        # ----------------------------------------------------------------
        # Step 2: build numbered context from retrieved chunks
        # (identical to F3 — chunks now come from the graph instead of
        # a direct retrieve() call)
        # ----------------------------------------------------------------
        chunks = final_state.get("retrieved_chunks", [])
        context = "\n\n".join(
            f"[{i+1}] [Source: {c.get('source','')}, Page: {c.get('page','?')}]\n{c.get('text','')}"
            for i, c in enumerate(chunks)
        )

        # ----------------------------------------------------------------
        # Step 3: stream answer tokens — synthesizer uses the big model
        # (routing=False is the default so small_model=False not needed)
        # ----------------------------------------------------------------
        llm = get_llm(request.provider)
        prompt = PromptTemplate(template=QA_PROMPT, input_variables=["context", "question", "history"])
        chain = prompt | llm

        # Accumulate the full answer so we can save it to memory after streaming
        full_answer = ""
        async for token in chain.astream({"context": context, "question": request.question, "history": history_text}):
            full_answer += token.content
            yield f'data: {json.dumps({"type": "token", "content": token.content})}\n\n'

        # ----------------------------------------------------------------
        # Step 4: emit one citation event per chunk (identical to F3)
        # ----------------------------------------------------------------
        for chunk in chunks:
            citation = CitationChunk(
                doc_id=chunk.get("doc_id", ""),
                source=chunk.get("source", ""),
                page=str(chunk.get("page", "")),
                chunk_index=chunk.get("chunk_index", 0),
                text=chunk.get("text", ""),
            )
            yield f'data: {json.dumps({"type": "citation", **citation.model_dump()})}\n\n'

        # ----------------------------------------------------------------
        # Step 5: save turn to memory, then signal done
        # ----------------------------------------------------------------
        if request.session_id:
            append_turn(request.session_id, "user", request.question)
            append_turn(request.session_id, "assistant", full_answer)

        yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.post("/summarize")
async def summarize(req: Request, request: SummarizeRequest):
    enforce_rate_limit(
        request=req,
        key_suffix=request.session_id,
        limit=30,
        window_seconds=60,
    )
    async def event_stream():
        initial_state = {
            "doc_id": request.doc_id,
            "provider": request.provider,
            "chunks": [],
            "chunk_summaries": [],
            "hop_traces": [],
        }
        final_state = dict(initial_state)

        # Run map step — small model summarizes each batch of chunks
        async for updates in summarize_graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in updates.items():
                final_state.update(node_output)
                hop_entries = node_output.get("hop_traces", [])
                if hop_entries:
                    latest = hop_entries[-1]
                    yield f'data: {json.dumps({"type": "hop_trace", "node": latest["node"], "data": latest["data"]})}\n\n'

        # Stream reduce step — full model merges batch summaries into final summary
        summaries_text = "\n\n".join(
            f"[Part {i + 1}] {s}"
            for i, s in enumerate(final_state.get("chunk_summaries", []))
        )
        llm = get_llm(request.provider)
        prompt = PromptTemplate(
            template=SUMMARIZE_REDUCE_PROMPT,
            input_variables=["summaries"],
        )
        chain = prompt | llm

        async for token in chain.astream({"summaries": summaries_text}):
            yield f'data: {json.dumps({"type": "token", "content": token.content})}\n\n'

        yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/compare")
async def compare(req: Request, request: CompareRequest):
    enforce_rate_limit(
        request=req,
        key_suffix=None,
        limit=30,
        window_seconds=60,
    )
    async def event_stream():
        initial_state = {
            "doc_ids": request.doc_ids,
            "question": request.question,
            "provider": request.provider,
            "top_k": request.top_k,
            "retrieved_chunks": [],
            "hop_traces": [],
        }
        final_state = dict(initial_state)

        # Run compare retrieve node — filtered semantic search across doc_ids
        async for updates in compare_graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_output in updates.items():
                final_state.update(node_output)
                hop_entries = node_output.get("hop_traces", [])
                if hop_entries:
                    latest = hop_entries[-1]
                    yield f'data: {json.dumps({"type": "hop_trace", "node": latest["node"], "data": latest["data"]})}\n\n'

        # Build numbered context tagged with source doc
        chunks = final_state.get("retrieved_chunks", [])
        context = "\n\n".join(
            f"[{i + 1}] [Source: {c.get('source', '')}, Doc: {c.get('doc_id', '')}, Page: {c.get('page', '?')}]\n{c.get('text', '')}"
            for i, c in enumerate(chunks)
        )

        # Stream comparison synthesis
        llm = get_llm(request.provider)
        prompt = PromptTemplate(
            template=COMPARE_PROMPT,
            input_variables=["context", "question"],
        )
        chain = prompt | llm

        async for token in chain.astream({"context": context, "question": request.question}):
            yield f'data: {json.dumps({"type": "token", "content": token.content})}\n\n'

        # Emit citations
        for chunk in chunks:
            citation = CitationChunk(
                doc_id=chunk.get("doc_id", ""),
                source=chunk.get("source", ""),
                page=str(chunk.get("page", "")),
                chunk_index=chunk.get("chunk_index", 0),
                text=chunk.get("text", ""),
            )
            yield f'data: {json.dumps({"type": "citation", **citation.model_dump()})}\n\n'

        yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.delete("/session/{session_id}")
def clear_session_endpoint(req: Request, session_id: str):
    enforce_rate_limit(
        request=req,
        key_suffix=session_id,
        limit=30,
        window_seconds=60,
    )
    """Clears all conversation history for a session — triggered by 'New session' button."""
    _clear_session(session_id)
    return {"cleared": session_id}