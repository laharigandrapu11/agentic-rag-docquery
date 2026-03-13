# Populated in F1 - Document Upload and Ingestion
import os
from uuid import uuid4
import aiofiles
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.schemas import UploadResponse, DocumentMeta, DeleteResponse
from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_documents
from app.ingestion.indexer import upsert_chunks, get_all_documents, delete_document

router = APIRouter()

@router.get("/documents", response_model=list[DocumentMeta])
async def list_documents():
    return get_all_documents()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(None), url: str = Form(None)):
    if not file and not url:
        raise HTTPException(status_code=400, detail="No file or URL provided")
    doc_id = str(uuid4())
    if file:
        tmp_path = f"/tmp/{file.filename}"
        async with aiofiles.open(tmp_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        filename = file.filename
        source = tmp_path
        
    else:
        filename = url.split("/")[-1]
        source = url
    docs = load_documents(source)
    chunks = chunk_documents(docs, doc_id)
    upsert_chunks(chunks)
    if file:
        os.remove(tmp_path)
    return UploadResponse(doc_id=doc_id, filename=filename, chunk_count=len(chunks))

@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def remove_document(doc_id: str):
    documents = get_all_documents()
    doc_ids = [doc.doc_id for doc in documents]
    
    if doc_id not in doc_ids:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")
    
    delete_document(doc_id)
    return DeleteResponse(doc_id=doc_id, deleted=True)