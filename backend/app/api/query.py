# Populated in F2 - Basic Q&A
# Extended in F3 - Streaming and Citations
# Extended in F6 - Summarize and Compare

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from langchain_core.prompts import PromptTemplate

from app.schemas import QueryRequest, CitationChunk
from app.retrieval.retriever import retrieve
from app.core.llm_factory import get_llm
from app.agent.prompts import QA_PROMPT

router = APIRouter()

@router.post("/query")
async def query(request: QueryRequest):

    async def event_stream():
        # Step 1: retrieve relevant chunks from Qdrant
        chunks = retrieve(request.question, request.top_k)

        # Step 2: build numbered context
        context = "\n\n".join(
            f"[{i+1}] [Source: {c.get('source','')}, Page: {c.get('page','?')}]\n{c.get('text','')}"
            for i, c in enumerate(chunks)
        )

        # Step 3: build the prompt and stream tokens from LLM
        llm = get_llm(request.provider)
        prompt = PromptTemplate(template=QA_PROMPT, input_variables=["context", "question"])
        chain = prompt | llm

        async for token in chain.astream({"context": context, "question": request.question}):
            yield f'data: {json.dumps({"type": "token", "content": token.content})}\n\n'

        # Step 4: emit one citation event per chunk
        for chunk in chunks:
            citation = CitationChunk(
                doc_id=chunk.get("doc_id", ""),
                source=chunk.get("source", ""),
                page=str(chunk.get("page", "")),
                chunk_index=chunk.get("chunk_index", 0),
                text=chunk.get("text", ""),
            )
            yield f'data: {json.dumps({"type": "citation", **citation.model_dump()})}\n\n'

        # Step 5: signal the frontend that streaming is complete
        yield 'data: {"type": "done"}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")