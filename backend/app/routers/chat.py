"""
Chat router for RAG-based responses.
"""
from typing import List
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

from app.config import settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SourceDocument,
)
from app.dependencies import get_vector_store, get_llm_service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Get shared service instances
vector_store = get_vector_store()
llm_service = get_llm_service()


def format_context(search_results: dict) -> str:
    """
    Format search results into context string for the LLM.
    """
    context_parts = []

    for i, doc in enumerate(search_results['documents'][0], 1):
        metadata = search_results['metadatas'][0][i-1]
        source = metadata.get('source', 'Unknown')

        context_parts.append(f"[Document {i}] (Source: {source})\n{doc}\n")

    return "\n".join(context_parts)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return a RAG-based response.

    This endpoint:
    1. Searches the knowledge base for relevant documents
    2. Formats context from retrieved documents
    3. Generates a response using LLM with the context
    """
    try:
        # Search for relevant documents
        search_results = vector_store.query(
            query_text=request.query,
            n_results=request.top_k or settings.top_k_results
        )

        # Check if we have results
        if not search_results['documents'][0]:
            return ChatResponse(
                response="I don't have any information about that topic in my knowledge base. "
                        "Please contact human support for assistance.",
                sources=[],
                conversation_id=None
            )

        # Format context
        context = format_context(search_results)

        # Generate response
        response = llm_service.generate_response(
            query=request.query,
            context=context,
            conversation_history=request.conversation_history
        )

        # Format sources
        sources = []
        for i in range(len(search_results['ids'][0])):
            sources.append(SourceDocument(
                content=search_results['documents'][0][i][:200] + "...",
                metadata=search_results['metadatas'][0][i],
                score=1 - search_results['distances'][0][i]
            ))

        return ChatResponse(
            response=response,
            sources=sources,
            conversation_id=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Process a chat message and stream the response.

    This endpoint is useful for real-time chat interfaces.
    """
    try:
        # Search for relevant documents
        search_results = vector_store.query(
            query_text=request.query,
            n_results=request.top_k or settings.top_k_results
        )

        # Check if we have results
        if not search_results['documents'][0]:
            async def no_results():
                yield f"data: {json.dumps({'content': 'No information found in knowledge base.'})}\n\n"
            return StreamingResponse(no_results(), media_type="text/event-stream")

        # Format context
        context = format_context(search_results)

        # Stream response
        async def generate():
            for chunk in llm_service.generate_streaming_response(
                query=request.query,
                context=context,
                conversation_history=request.conversation_history
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.post("/chat/quick")
async def quick_chat(query: str):
    """
    Quick chat endpoint without conversation history.

    Simplified endpoint for quick queries.
    """
    request = ChatRequest(query=query)
    return await chat(request)