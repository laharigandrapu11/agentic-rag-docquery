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