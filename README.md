# RAG Support Chatbot

A production-ready RAG (Retrieval-Augmented Generation) customer support chatbot with a FastAPI backend and React frontend. Deployed on Vercel + Render for 24/7 availability.

🌐 **Live Demo:** https://rag-supported-chatbot.vercel.app

![RAG Architecture](https://img.shields.io/badge/RAG-Architecture-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![React](https://img.shields.io/badge/React-TypeScript-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 What is RAG?

Traditional chatbots only know what they were trained on. RAG makes them smarter:

1. **Retrieve** — Search a knowledge base for relevant documents using semantic similarity
2. **Augment** — Add that context to the user's question
3. **Generate** — LLM creates an accurate, grounded answer with source citations

Result: Answers based on **your data**, not hallucinations.

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Client  │────▶│  FastAPI Backend │────▶│    Groq LLM     │
│  (TypeScript)   │     │   (Port 8000)    │     │  (Llama 3.3 70B)│
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
           ┌─────────────────┐       ┌─────────────────┐
           │  FAISS Vector   │       │   Voyage AI      │
           │  Store (Local)  │       │  (Embeddings)    │
           └─────────────────┘       └─────────────────┘
```

**Stack:**
- **LLM:** Groq API — Llama 3.3 70B (free tier, ultra-fast inference)
- **Embeddings:** Voyage AI — voyage-3-lite (free tier, 512-dim vectors)
- **Vector Store:** FAISS (local, CPU-compatible, no external DB needed)
- **Backend:** FastAPI + Uvicorn
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Deployment:** Vercel (frontend) + Render (backend) + Docker

---

## ✅ Features

- **RAG Pipeline** — Retrieves relevant documents before every response
- **Semantic Search** — Voyage AI embeddings for accurate similarity matching
- **Fast Inference** — Groq's LPU delivers sub-second response times
- **Source Citations** — Every answer shows which documents were used
- **Conversation History** — Maintains context across multi-turn chats
- **Streaming Responses** — Real-time token streaming to the UI
- **Document Management** — Upload, search, and delete knowledge base docs via API
- **Rate Limiting** — Built-in protection (20 req/min via SlowAPI)
- **Docker Support** — One-command local deployment

---

## 📁 Project Structure

```
rag-support-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & env vars
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   └── documents.py     # Document management endpoints
│   │   ├── services/
│   │   │   ├── embedding.py     # Voyage AI embeddings
│   │   │   ├── vectorstore.py   # FAISS vector store operations
│   │   │   └── llm.py           # Groq LLM (+ Gemini/Ollama/OpenAI support)
│   │   └── utils/
│   │       └── chunking.py      # Document chunking logic
│   ├── data/
│   │   └── sample_docs/         # Knowledge base documents (12+ files)
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

---

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Groq API Key](https://console.groq.com/keys) (free)
- [Voyage AI Key](https://dash.voyageai.com/) (free)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your API keys:
# GROQ_API_KEY=your-groq-key
# VOYAGE_API_KEY=your-voyage-key

# Load sample documents into FAISS
python -c "
from app.services.vectorstore import VectorStoreService
from app.utils.chunking import chunk_text
import os
vs = VectorStoreService()
for f in os.listdir('data/sample_docs'):
    if f.endswith('.txt'):
        text = open(f'data/sample_docs/{f}').read()
        chunks = chunk_text(text, 500, 50)
        vs.add_documents(chunks, [{'source': f}] * len(chunks))
print(f'Loaded {vs.get_document_count()} chunks')
"

# Run backend
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Access the App

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## 🔧 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# LLM - Groq (required)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
USE_GROQ=true

# Embeddings - Voyage AI (required)
VOYAGE_API_KEY=your-voyage-api-key

# Optional alternative LLMs (set USE_GROQ=false to switch)
# OPENAI_API_KEY=your-openai-key
# GEMINI_API_KEY=your-gemini-key
# OLLAMA_BASE_URL=http://localhost:11434
```

---

## 📡 API Endpoints

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat` | Send a message (with history) |
| POST | `/api/v1/chat/stream` | Streaming chat response |
| POST | `/api/v1/chat/quick` | Single-turn quick chat |

### Documents

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/documents/upload` | Upload text document |
| POST | `/api/v1/documents/upload-file` | Upload file |
| POST | `/api/v1/documents/search` | Semantic search |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| DELETE | `/api/v1/documents/clear` | Clear all documents |
| GET | `/api/v1/documents/stats` | Knowledge base stats |

---

## 🐳 Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Testing

```bash
cd backend
pytest
pytest --cov=app tests/   # with coverage
```

---

## 🔒 Security Notes

- Never commit `.env` files — they are in `.gitignore`
- Always store API keys as environment variables, never in source code
- Rate limiting is enabled by default (20 req/min)
- Add authentication (JWT/API keys) before exposing to public traffic

---

## 📈 Scaling for Production

- Replace FAISS with **Pinecone** or **Weaviate** for multi-instance deployments
- Add **Redis** caching for frequent queries
- Add **JWT authentication** for user-specific sessions
- Use **async document processing** for large file uploads
- Monitor with **Prometheus + Grafana**

---

## 📝 License

MIT License
