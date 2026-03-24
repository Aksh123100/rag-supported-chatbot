"""
Pydantic models for request/response schemas.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., min_length=1, max_length=4000, description="User query")
    conversation_history: Optional[List[Message]] = Field(
        default=None,
        description="Previous conversation messages for context"
    )
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")


class SourceDocument(BaseModel):
    """Source document reference in response."""
    content: str = Field(..., description="Relevant content snippet")
    metadata: dict = Field(..., description="Document metadata")
    score: float = Field(..., description="Similarity score")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Assistant response")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for follow-up")


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    source: str = Field(..., description="Document source/filename")
    category: Optional[str] = Field(None, description="Document category")
    doc_type: Optional[str] = Field(None, description="Document type: faq, policy, guide, etc.")


class DocumentUpload(BaseModel):
    """Document upload request."""
    content: str = Field(..., min_length=1, description="Document content")
    metadata: DocumentMetadata = Field(..., description="Document metadata")


class DocumentUploadResponse(BaseModel):
    """Document upload response."""
    id: str = Field(..., description="Document ID")
    message: str = Field(..., description="Status message")
    chunks_created: int = Field(..., description="Number of chunks created")


class BulkUploadResponse(BaseModel):
    """Bulk upload response."""
    total_documents: int = Field(..., description="Total documents processed")
    total_chunks: int = Field(..., description="Total chunks created")
    failed: List[str] = Field(default_factory=list, description="Failed document IDs")


class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of results")


class SearchResult(BaseModel):
    """Search result model."""
    id: str = Field(..., description="Chunk ID")
    content: str = Field(..., description="Content snippet")
    metadata: dict = Field(..., description="Metadata")
    score: float = Field(..., description="Similarity score")


class SearchResponse(BaseModel):
    """Search response model."""
    results: List[SearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original query")
    total: int = Field(..., description="Total results found")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")