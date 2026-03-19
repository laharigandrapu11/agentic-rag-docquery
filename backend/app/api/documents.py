# Populated in F1 - Document Upload and Ingestion
import os
import uuid
from uuid import uuid4
import aiofiles
from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Request
from app.security.rate_limiter import enforce_rate_limit
from app.schemas import UploadResponse, DocumentMeta, DeleteResponse
from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_documents
from app.ingestion.indexer import upsert_chunks, get_all_documents, delete_document

router = APIRouter()

@router.get("/documents", response_model=list[DocumentMeta])
async def list_documents(request: Request):
    enforce_rate_limit(request=request, key_suffix=None, limit=30, window_seconds=60)
    return get_all_documents()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(request: Request, file: UploadFile = File(None), url: str = Form(None)):
    enforce_rate_limit(request=request, key_suffix=None, limit=30, window_seconds=60)

    # Strict multipart validation: accept exactly one input source.
    if not file and not url:
        raise HTTPException(status_code=400, detail="No file or URL provided")
    if file and url:
        raise HTTPException(status_code=400, detail="Provide either file OR url, not both.")

    if url is not None:
        url = url.strip()
        if len(url) < 1 or len(url) > 2048:
            raise HTTPException(status_code=400, detail="URL length is invalid.")
        if not (url.startswith("http://") or url.startswith("https://")):
            raise HTTPException(status_code=400, detail="URL scheme must be http/https.")

    doc_id = str(uuid4())
    tmp_path: str | None = None

    if file:
        filename = (file.filename or "").strip()
        if len(filename) < 1 or len(filename) > 200:
            raise HTTPException(status_code=400, detail="Filename length is invalid.")

        allowed_ext = {".pdf", ".docx", ".txt", ".md"}
        ext = ("." + filename.split(".")[-1].lower()) if "." in filename else ""
        if ext not in allowed_ext:
            raise HTTPException(status_code=400, detail="Unsupported file type.")

        tmp_path = f"/tmp/{uuid.uuid4()}_{filename}"
        source = tmp_path

        # Keep file uploads bounded to avoid resource exhaustion.
        max_bytes = 10 * 1024 * 1024  # 10MB
        try:
            async with aiofiles.open(tmp_path, "wb") as f:
                content = await file.read()
                if len(content) > max_bytes:
                    raise HTTPException(status_code=413, detail="File too large (max 10MB).")
                await f.write(content)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    else:
        filename = url.split("/")[-1]
        source = url
    try:
        docs = load_documents(source)
        chunks = chunk_documents(docs, doc_id)
        upsert_chunks(chunks)
        return UploadResponse(doc_id=doc_id, filename=filename, chunk_count=len(chunks))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def remove_document(request: Request, doc_id: str):
    enforce_rate_limit(request=request, key_suffix=None, limit=30, window_seconds=60)
    documents = get_all_documents()
    doc_ids = [doc.doc_id for doc in documents]
    
    if doc_id not in doc_ids:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    
    delete_document(doc_id)
    return DeleteResponse(doc_id=doc_id, deleted=True)