from pydantic import BaseModel, ConfigDict, Field

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

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

class QueryRequest(StrictBaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    provider: str = Field("groq", pattern="^(groq|gemini|mistral)$")
    top_k: int = Field(5, ge=1, le=10)
    session_id: str | None = Field(default=None, max_length=128)
    doc_ids: list[str] | None = Field(default=None, max_length=50)

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]

class CitationChunk(BaseModel):
    doc_id: str
    source: str      # filename
    page: str        # page number as string (PDFs return it as string)
    chunk_index: int
    text: str        # the actual chunk text shown in the citation panel


class SummarizeRequest(StrictBaseModel):
    doc_id: str = Field(..., min_length=1, max_length=128)
    session_id: str | None = Field(default=None, max_length=128)
    provider: str = Field("groq", pattern="^(groq|gemini|mistral)$")

class CompareRequest(StrictBaseModel):
    doc_ids: list[str] = Field(..., min_length=1, max_length=50)
    question: str = Field(..., min_length=1, max_length=4000)
    provider: str = Field("groq", pattern="^(groq|gemini|mistral)$")
    top_k: int = Field(5, ge=1, le=10)