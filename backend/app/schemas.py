from pydantic import BaseModel

class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    source: str
    chunk_count: int
    created_at: str


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int


class DeleteResponse(BaseModel):
    doc_id: str
    deleted: bool

class QueryRequest(BaseModel):
    question: str
    provider:str = "groq"
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

class CitationChunk(BaseModel):
    doc_id: str
    source: str      # filename
    page: str        # page number as string (PDFs return it as string)
    chunk_index: int
    text: str        # the actual chunk text shown in the citation panel