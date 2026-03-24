import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface SourceDocument {
  content: string;
  metadata: Record<string, unknown>;
  score: number;
}

export interface ChatRequest {
  query: string;
  conversation_history?: Message[];
  top_k?: number;
}

export interface ChatResponse {
  response: string;
  sources: SourceDocument[];
  conversation_id?: string;
}

export interface DocumentUpload {
  content: string;
  metadata: {
    source: string;
    category?: string;
    doc_type?: string;
  };
}

export interface DocumentUploadResponse {
  id: string;
  message: string;
  chunks_created: number;
}

export interface SearchResult {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total: number;
}

export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },

  quickChat: async (query: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>(`/chat/quick?query=${encodeURIComponent(query)}`);
    return response.data;
  },
};

export const documentsApi = {
  upload: async (document: DocumentUpload): Promise<DocumentUploadResponse> => {
    const response = await api.post<DocumentUploadResponse>('/documents/upload', document);
    return response.data;
  },

  uploadFile: async (file: File, category?: string, docType?: string): Promise<{ filename: string; message: string; chunks_created: number }> => {
    const formData = new FormData();
    formData.append('file', file);
    if (category) formData.append('category', category);
    if (docType) formData.append('doc_type', docType);

    const response = await api.post('/documents/upload-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  search: async (query: string, topK: number = 5): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/documents/search', {
      query,
      top_k: topK,
    });
    return response.data;
  },

  getStats: async (): Promise<{ collection_name: string; document_count: number; persist_directory: string }> => {
    const response = await api.get('/documents/stats');
    return response.data;
  },

  deleteBySource: async (source: string): Promise<{ message: string }> => {
    const response = await api.delete(`/documents/by-source/${encodeURIComponent(source)}`);
    return response.data;
  },

  clearAll: async (): Promise<{ message: string }> => {
    const response = await api.delete('/documents/clear');
    return response.data;
  },
};

export default api;