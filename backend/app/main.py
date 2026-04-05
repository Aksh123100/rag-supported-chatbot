"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

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

# Auto-load documents on startup
@app.on_event("startup")
async def load_initial_documents():
    """Load sample documents into vector store on startup."""
    from app.dependencies import get_vector_store
    from app.utils.chunking import smart_chunk
    import uuid
    
    vs = get_vector_store()
    
    # Only load if vector store is empty
    if vs.get_document_count() == 0:
        print("📚 Loading sample documents...")
        sample_docs_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs")
        
        if os.path.exists(sample_docs_dir):
            for filename in os.listdir(sample_docs_dir):
                if filename.endswith('.txt'):
                    filepath = os.path.join(sample_docs_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Determine category and doc_type
                        if 'faq' in filename.lower():
                            category, doc_type = 'support', 'faq'
                        elif 'policy' in filename.lower() or 'policies' in filename.lower():
                            category, doc_type = 'policies', 'policy'
                        else:
                            category, doc_type = 'general', 'general'
                        
                        # Chunk and add documents
                        chunks = smart_chunk(content, doc_type=doc_type)
                        documents = [chunk['content'] for chunk in chunks]
                        metadatas = [
                            {
                                **chunk['metadata'],
                                'source': filename,
                                'category': category,
                                'doc_type': doc_type
                            }
                            for chunk in chunks
                        ]
                        ids = [str(uuid.uuid4()) for _ in chunks]
                        
                        vs.add_documents(documents=documents, metadatas=metadatas, ids=ids)
                        print(f"  ✓ Loaded {filename}: {len(chunks)} chunks")
                        
                    except Exception as e:
                        print(f"  ✗ Error loading {filename}: {e}")
            
            doc_count = vs.get_document_count()
            print(f"✅ Total documents loaded: {doc_count}")
        else:
            print(f"⚠️  Sample docs directory not found: {sample_docs_dir}")
    else:
        print(f"ℹ️  Vector store already has {vs.get_document_count()} documents")

# Configure CORS - production friendly
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
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
    from app.dependencies import get_vector_store
    
    try:
        vs = get_vector_store()
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