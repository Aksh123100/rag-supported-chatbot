"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import chat, documents

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A RAG-based customer support chatbot API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - production friendly
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(chat.router, prefix=settings.api_prefix, tags=["Chat"])
app.include_router(documents.router, prefix=settings.api_prefix, tags=["Documents"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    from app.services.vectorstore import VectorStoreService
    
    try:
        vs = VectorStoreService()
        doc_count = vs.get_document_count()
        return {
            "status": "healthy",
            "service": settings.app_name,
            "documents_loaded": doc_count,
            "vector_db": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }