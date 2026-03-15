# Populated in F2 - Basic Q&A
# Extended in F3 - Streaming and Citations
# Extended in F4 - Agentic Multi-hop Reasoning
# Extended in F6 - Summarize and Compare

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.prompts import PromptTemplate

from app.schemas import QueryRequest, CitationChunk
from app.core.llm_factory import get_llm
from app.agent.prompts import QA_PROMPT
from app.agent.graph import compiled_graph

router = APIRouter()

@router.post("/query")
async def query(request: QueryRequest):

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
        initial_state = {
            "question": request.question,
            "provider": request.provider,
            "top_k": request.top_k,
            "route": "",
            "sub_questions": [],
            "retrieved_chunks": [],
            "hop_traces": [],
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
        prompt = PromptTemplate(template=QA_PROMPT, input_variables=["context", "question"])
        chain = prompt | llm

        async for token in chain.astream({"context": context, "question": request.question}):
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
        # Step 5: signal done (identical to F3)
        # ----------------------------------------------------------------
        yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")