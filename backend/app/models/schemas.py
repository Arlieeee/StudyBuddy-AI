"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    PPTX = "pptx"
    DOCX = "docx"
    TXT = "txt"


# ============ Document Schemas ============

class DocumentBase(BaseModel):
    """Base document schema."""
    filename: str
    file_type: DocumentType


class DocumentCreate(DocumentBase):
    """Document creation schema."""
    pass


class DocumentResponse(DocumentBase):
    """Document response schema."""
    id: str
    status: DocumentStatus
    chunk_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """List of documents response."""
    documents: List[DocumentResponse]
    total: int


# ============ Q&A Schemas ============

class QuestionRequest(BaseModel):
    """Question request schema."""
    question: str = Field(..., min_length=1, max_length=2000)
    document_ids: Optional[List[str]] = None  # Filter by specific documents


class SourceReference(BaseModel):
    """Source reference in answer."""
    document_id: str
    document_name: str
    chunk_text: str
    relevance_score: float


class AnswerResponse(BaseModel):
    """Answer response schema."""
    answer: str
    sources: List[SourceReference]
    thinking_process: Optional[str] = None


# ============ Image Generation Schemas ============

class ImageGenerateRequest(BaseModel):
    """Image generation request."""
    prompt: str = Field(..., min_length=1, max_length=1000)
    knowledge_context: Optional[str] = None  # Include related knowledge from RAG
    conversation_history: Optional[str] = None  # Previous chat history for context
    style: str = "educational"  # educational, diagram, mindmap, infographic
    aspect_ratio: str = "16:9"


class ImageResponse(BaseModel):
    """Image generation response."""
    image_base64: str
    description: str


# ============ Chat Schemas ============

class ChatMessage(BaseModel):
    """Chat message schema."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatHistoryResponse(BaseModel):
    """Chat history response."""
    messages: List[ChatMessage]
