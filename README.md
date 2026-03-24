# RAG Support Chatbot

A production-ready RAG (Retrieval-Augmented Generation) customer support chatbot built with FastAPI backend and React frontend.

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Client  │────▶│  FastAPI Backend │────▶│   OpenAI API    │
│   (Port 5173)   │     │   (Port 8000)    │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    ChromaDB     │
                        │  (Vector Store) │
                        └─────────────────┘
```

## 📁 Project Structure

```
rag-support-chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Configuration settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   └── documents.py     # Document management
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── embedding.py     # OpenAI embeddings
│   │   │   ├── vectorstore.py   # ChromaDB operations
│   │   │   └── llm.py           # OpenAI LLM
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── chunking.py      # Document chunking
│   ├── data/
│   │   └── sample_docs/         # Sample knowledge base
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
└── docker-compose.yml
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your-api-key-here

# Run the backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### 3. Load Sample Data

```bash
# Use the API to load sample documents
# Or use Python to load documents programmatically

# See scripts/load_data.py for example
```

### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model to use | `gpt-4-turbo-preview` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `CHROMA_PERSIST_DIRECTORY` | Vector DB path | `./data/chroma_db` |
| `CHROMA_COLLECTION_NAME` | Collection name | `support_docs` |

## 📡 API Endpoints

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send a chat message |
| POST | `/api/v1/chat/stream` | Stream chat response |
| POST | `/api/v1/chat/quick` | Quick chat (no history) |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/documents/upload` | Upload document |
| POST | `/api/v1/documents/upload-file` | Upload file |
| POST | `/api/v1/documents/search` | Search documents |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| DELETE | `/api/v1/documents/clear` | Clear all documents |
| GET | `/api/v1/documents/stats` | Get statistics |

## 🧪 Testing

```bash
# Run tests
cd backend
pytest

# Run with coverage
pytest --cov=app tests/
```

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📊 Key Features

- **RAG Architecture**: Retrieve relevant documents before generating responses
- **Vector Search**: Semantic search using OpenAI embeddings
- **Conversation History**: Maintains context across messages
- **Source Citations**: Shows which documents were used for responses
- **Document Management**: Upload, search, and delete documents
- **Streaming Responses**: Real-time response streaming
- **Modern UI**: Clean React frontend with Tailwind CSS

## 🔒 Security Notes

- Never commit `.env` files with API keys
- Use environment variables for sensitive data
- Consider rate limiting for production
- Add authentication for production use

## 📈 Scaling for Production

1. **Replace ChromaDB** with Pinecone or Weaviate for large scale
2. **Add caching** with Redis for frequently asked questions
3. **Implement rate limiting** to prevent abuse
4. **Add authentication** (JWT, API keys)
5. **Use async processing** for document uploads
6. **Monitor with Prometheus/Grafana**
7. **Deploy with Kubernetes** for horizontal scaling

## 📝 License

MIT License