import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, record_audit_log
from app.models.user import User, UserRole
from app.models.document import Document, DocumentChunk
from app.schemas.document import (
    DocumentResponse,
    DocumentDetailResponse,
    DocumentQuestionRequest,
    DocumentAnswerResponse
)
from app.services.document_service import document_service
from app.services.llm_service import llm_service

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all indexed business documents."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    results = []
    for d in docs:
        resp = DocumentResponse(
            id=d.id,
            filename=d.filename,
            file_type=d.file_type,
            file_size=d.file_size,
            content_summary=d.content_summary,
            uploaded_by_id=d.uploaded_by_id,
            created_at=d.created_at,
            chunks_count=len(d.chunks)
        )
        results.append(resp)
    return results


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and index a business document (PDF, TXT, DOCX).
    Automatically extracts text, computes chunks, and registers embeddings.
    """
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"
    if ext not in ["txt", "pdf", "docx", "md", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type .{ext}. Allowed: pdf, docx, txt, md, csv"
        )

    file_id = str(uuid.uuid4())
    stored_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # Extract text content
    extracted_text = document_service.extract_text(file_path, ext)
    if not extracted_text:
        extracted_text = f"Empty or unreadable document: {file.filename}"

    # Generate document summary
    summary_prompt = f"Summarize the key operational policies and facts from this document ({file.filename}):\n\n{extracted_text[:2000]}"
    summary = await llm_service.generate_text(summary_prompt)

    # Persist Document
    doc = Document(
        id=file_id,
        filename=file.filename,
        file_type=ext,
        file_size=file_size,
        file_path=file_path,
        content_summary=summary[:500] if summary else "Indexed document.",
        raw_text=extracted_text,
        uploaded_by_id=current_user.id
    )
    db.add(doc)

    # Chunk and embed
    chunks = document_service.chunk_text(extracted_text, chunk_size=300, overlap=40)
    for idx, chunk_text in enumerate(chunks):
        embedding_vec = document_service.compute_embedding(chunk_text)
        chunk_obj = DocumentChunk(
            document_id=doc.id,
            chunk_index=idx,
            content=chunk_text,
            embedding=embedding_vec,
            metadata_info={"filename": file.filename, "chunk_index": idx}
        )
        db.add(chunk_obj)

    db.commit()
    db.refresh(doc)

    record_audit_log(
        db,
        action="DOCUMENT_UPLOADED",
        user_id=current_user.id,
        details={"document_id": doc.id, "filename": doc.filename, "chunks_count": len(chunks)}
    )

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        content_summary=doc.content_summary,
        uploaded_by_id=doc.uploaded_by_id,
        created_at=doc.created_at,
        chunks_count=len(chunks)
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve document details and chunk breakdown."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.post("/query", response_model=DocumentAnswerResponse)
async def query_documents_rag(
    request: DocumentQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    RAG-powered conversational Q&A endpoint.
    Retrieves most relevant document chunks and generates grounded answers.
    """
    query = db.query(DocumentChunk)
    if request.document_id:
        query = query.filter(DocumentChunk.document_id == request.document_id)
    all_chunks = query.all()

    if not all_chunks:
        return DocumentAnswerResponse(
            question=request.question,
            answer="No relevant documents found in knowledge base.",
            relevant_chunks=[],
            source_documents=[]
        )

    chunk_dicts = [
        {
            "id": c.id,
            "document_id": c.document_id,
            "content": c.content,
            "embedding": c.embedding,
            "filename": c.metadata_info.get("filename", "Doc")
        }
        for c in all_chunks
    ]

    top_matches = document_service.retrieve_relevant_chunks(request.question, chunk_dicts, top_k=3)
    context = "\n\n".join([f"Excerpt from {m[0]['filename']}:\n{m[0]['content']}" for m in top_matches])
    source_docs = list(set([m[0]["filename"] for m in top_matches]))

    prompt = (
        f"You are the Document Analysis Agent. Answer the user question accurately based ONLY on the provided context.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {request.question}\n\n"
        f"Answer:"
    )

    answer = await llm_service.generate_text(prompt)

    return DocumentAnswerResponse(
        question=request.question,
        answer=answer,
        relevant_chunks=[m[0]["content"] for m in top_matches],
        source_documents=source_docs
    )


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document and its indexed vector chunks."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if current_user.role == "employee" and doc.uploaded_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete other users' documents.")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()

    record_audit_log(db, action="DOCUMENT_DELETED", user_id=current_user.id, details={"document_id": document_id})
    return {"message": "Document deleted successfully"}
