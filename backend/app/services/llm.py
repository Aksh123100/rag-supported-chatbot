"""
LLM service for generating responses using OpenAI, Ollama, Gemini, or Groq.
"""
from typing import List, Optional
import requests
from app.config import settings
from app.models.schemas import Message


class LLMService:
    """Service for interacting with LLM."""

    def __init__(self):
        """Initialize LLM service."""
        self.use_ollama = settings.use_ollama
        self.use_gemini = settings.use_gemini
        self.use_groq = settings.use_groq
        
        if self.use_groq:
            from groq import Groq
            self.client = Groq(api_key=settings.groq_api_key)
            self.model_name = settings.groq_model
        elif self.use_gemini:
            from google import genai
            self.client = genai.Client(api_key=settings.gemini_api_key)
            self.model_name = settings.gemini_model
        elif self.use_ollama:
            self.ollama_url = f"{settings.ollama_base_url}/api/chat"
            self.model_name = settings.ollama_model
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model_name = settings.openai_model

    def _build_system_prompt(self, context: str) -> str:
        """Build system prompt with context."""
        return f"""You are a helpful customer support assistant for an e-commerce platform.
Your role is to provide accurate, helpful, and friendly responses to customer inquiries.

Use ONLY the provided context to answer questions. If the answer is not in the context,
politely say that you don't have that information and suggest contacting human support.

Be concise but thorough. Maintain a professional and helpful tone.

CONTEXT:
{context}

Remember:
- If you don't know something, say so honestly
- Don't make up information not in the context
- Be helpful and guide customers to the right resources
- If a customer is frustrated, be empathetic"""

    def _format_messages(
        self,
        system_prompt: str,
        conversation_history: Optional[List[Message]] = None
    ) -> List[dict]:
        """Format messages for API."""
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return messages

    def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate a response using LLM."""
        system_prompt = self._build_system_prompt(context)
        
        if self.use_groq:
            messages = self._format_messages(system_prompt, conversation_history)
            messages.append({"role": "user", "content": query})
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        elif self.use_gemini:
            full_prompt = f"{system_prompt}\n\nUser question: {query}"
            if conversation_history:
                history_text = "\n".join([f"{m.role}: {m.content}" for m in conversation_history])
                full_prompt = f"{system_prompt}\n\nConversation history:\n{history_text}\n\nUser question: {query}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            )
            return response.text
        elif self.use_ollama:
            messages = self._format_messages(system_prompt, conversation_history)
            messages.append({"role": "user", "content": query})
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        else:
            messages = self._format_messages(system_prompt, conversation_history)
            messages.append({"role": "user", "content": query})
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

    def generate_streaming_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Message]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Generate a streaming response using LLM."""
        system_prompt = self._build_system_prompt(context)
        messages = self._format_messages(system_prompt, conversation_history)
        messages.append({"role": "user", "content": query})
        
        if self.use_groq:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        elif self.use_gemini:
            full_prompt = f"{system_prompt}\n\nUser question: {query}"
            if conversation_history:
                history_text = "\n".join([f"{m.role}: {m.content}" for m in conversation_history])
                full_prompt = f"{system_prompt}\n\nConversation history:\n{history_text}\n\nUser question: {query}"
            
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=full_prompt,
                config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }
            ):
                if chunk.text:
                    yield chunk.text
        elif self.use_ollama:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                stream=True
            )
            response.raise_for_status()
            
            import json
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        yield data["message"]["content"]
        else:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content