# Populated in F2 - Basic Q&A
# Extended in F3 - Streaming and Citations
# Extended in F6 - Summarize and Compare

from fastapi import APIRouter
from langchain_core.prompts import PromptTemplate

from app.schemas import QueryRequest, QueryResponse
from app.retrieval.retriever import retrieve
from app.core.llm_factory import get_llm
from app.agent.prompts import QA_PROMPT

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    chunks = retrieve(request.question, request.top_k)      #we get the payloads here [{source: str, page: int, chunk_index: int, text: str}]

    context = "\n\n".join(
        f"[Source: {c.get('source', 'unknown')}, Page: {c.get('page', '?')}]\n{c.get('text', '')}"
        for c in chunks
    )

    llm = get_llm(request.provider)
    prompt = PromptTemplate(template=QA_PROMPT, input_variables=["context", "question"])

    # LCEL style: pipe prompt into llm, then call invoke
    chain = prompt | llm
    result = chain.invoke({"context": context, "question": request.question})

    # result.content is the plain text string returned by the LLM
    answer = result.content

    return QueryResponse(answer=answer.strip(), sources=chunks)
