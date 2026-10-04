from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata_info: Dict[str, Any]

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    content_summary: Optional[str] = None
    uploaded_by_id: Optional[str] = None
    created_at: datetime
    chunks_count: Optional[int] = 0

    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    raw_text: Optional[str] = None
    chunks: List[DocumentChunkResponse] = []


class DocumentQuestionRequest(BaseModel):
    question: str
    document_id: Optional[str] = None  # None means search all docs


class DocumentAnswerResponse(BaseModel):
    question: str
    answer: str
    relevant_chunks: List[str]
    source_documents: List[str]
