"""File upload router."""
import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List

from ..config import get_settings
from ..models.schemas import DocumentResponse, DocumentListResponse, DocumentStatus, DocumentType
from ..services.rag_service import get_rag_service

router = APIRouter(prefix="/upload", tags=["upload"])
settings = get_settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Supported file extensions
ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".docx", ".txt"}


def get_file_type(filename: str) -> DocumentType:
    """Get document type from filename."""
    ext = os.path.splitext(filename)[1].lower()
    type_map = {
        ".pdf": DocumentType.PDF,
        ".pptx": DocumentType.PPTX,
        ".docx": DocumentType.DOCX,
        ".txt": DocumentType.TXT,
    }
    return type_map.get(ext)


@router.post("/", response_model=DocumentResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload a document file.
    
    Supported formats: PDF, PPTX, DOCX, TXT
    """
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}. 支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}{ext}")
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # Process document in background
    rag_service = get_rag_service()
    
    try:
        # Process document (synchronously for now, can be made async)
        doc_record = await rag_service.add_document(file_path, doc_id)
        
        return DocumentResponse(
            id=doc_record["id"],
            filename=file.filename,
            file_type=get_file_type(file.filename),
            status=DocumentStatus.COMPLETED,
            chunk_count=doc_record["chunk_count"],
            created_at=doc_record["created_at"],
        )
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    rag_service = get_rag_service()
    documents = rag_service.list_documents()
    
    doc_responses = [
        DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            file_type=DocumentType(doc["file_type"]),
            status=doc["status"],
            chunk_count=doc.get("chunk_count", 0),
            created_at=doc["created_at"],
        )
        for doc in documents
    ]
    
    return DocumentListResponse(
        documents=doc_responses,
        total=len(doc_responses),
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    rag_service = get_rag_service()
    
    # Get document to find file path
    doc = rag_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # Delete from RAG service
    success = await rag_service.delete_document(document_id)
    
    if success:
        # Try to delete the original file
        for ext in ALLOWED_EXTENSIONS:
            file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}{ext}")
            if os.path.exists(file_path):
                os.remove(file_path)
                break
        
        return {"message": "文档已删除", "document_id": document_id}
    
    raise HTTPException(status_code=500, detail="删除失败")
