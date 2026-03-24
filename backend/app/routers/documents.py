"""
Document management router.
"""
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import os

from app.config import settings
from app.models.schemas import (
    DocumentUpload,
    DocumentUploadResponse,
    BulkUploadResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.vectorstore import VectorStoreService
from app.utils.chunking import smart_chunk

router = APIRouter()

# Initialize services
vector_store = VectorStoreService()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(document: DocumentUpload):
    """
    Upload a single document to the knowledge base.

    This endpoint accepts document content and metadata, chunks it,
    stores it in the vector database for later retrieval.
    """
    try:
        # Chunk the document
        chunks = smart_chunk(
            document.content,
            doc_type=document.metadata.doc_type or "general"
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="Document is empty or could not be chunked")

        # Prepare data for vector store
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                **chunk['metadata'],
                'source': document.metadata.source,
                'category': document.metadata.category or 'general',
                'doc_type': document.metadata.doc_type or 'general'
            }
            for chunk in chunks
        ]

        # Generate IDs
        import uuid
        ids = [str(uuid.uuid4()) for _ in chunks]

        # Add to vector store
        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        return DocumentUploadResponse(
            id=ids[0],  # Return first chunk ID as document ID
            message="Document uploaded successfully",
            chunks_created=len(chunks)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.post("/documents/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    category: str = Form(None),
    doc_type: str = Form(None)
):
    """
    Upload a file to the knowledge base.

    Accepts text files (.txt, .md) and processes them.
    """
    # Check file extension
    allowed_extensions = ['.txt', '.md', '.json']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')

        # Chunk the document
        chunks = smart_chunk(
            text_content,
            doc_type=doc_type or "general"
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="File is empty or could not be processed")

        # Prepare data
        documents = [chunk['content'] for chunk in chunks]
        metadatas = [
            {
                **chunk['metadata'],
                'source': file.filename,
                'category': category or 'general',
                'doc_type': doc_type or 'general'
            }
            for chunk in chunks
        ]

        import uuid
        ids = [str(uuid.uuid4()) for _ in chunks]

        # Add to vector store
        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        return {
            "filename": file.filename,
            "message": "File uploaded successfully",
            "chunks_created": len(chunks)
        }

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not decode file as UTF-8 text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.post("/documents/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search the knowledge base for relevant documents.

    Returns documents similar to the query based on semantic similarity.
    """
    try:
        results = vector_store.query(
            query_text=request.query,
            n_results=request.top_k or settings.top_k_results
        )

        search_results = []
        for i in range(len(results['ids'][0])):
            search_results.append(SearchResult(
                id=results['ids'][0][i],
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i],
                score=1 - results['distances'][0][i]  # Convert distance to similarity
            ))

        return SearchResponse(
            results=search_results,
            query=request.query,
            total=len(search_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the knowledge base.
    """
    try:
        vector_store.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.delete("/documents/by-source/{source}")
async def delete_by_source(source: str):
    """
    Delete all documents from a specific source.
    """
    try:
        vector_store.delete_by_metadata("source", source)
        return {"message": f"All documents from source '{source}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")


@router.delete("/documents/clear")
async def clear_all_documents():
    """
    Clear all documents from the knowledge base.

    Warning: This action cannot be undone.
    """
    try:
        vector_store.clear_collection()
        return {"message": "All documents cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


@router.get("/documents/stats")
async def get_document_stats():
    """
    Get statistics about the knowledge base.
    """
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")