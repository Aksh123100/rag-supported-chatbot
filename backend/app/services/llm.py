"""
LLM service for generating responses using OpenAI.
"""
from typing import List, Optional
from openai import OpenAI
from app.config import settings
from app.models.schemas import Message


class LLMService:
    """Service for interacting with OpenAI LLM."""

    def __init__(self):
        """Initialize LLM service."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

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
        """Format messages for OpenAI API."""
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
        """
        Generate a response using OpenAI.

        Args:
            query: User query.
            context: Retrieved context from vector store.
            conversation_history: Previous conversation messages.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated response string.
        """
        system_prompt = self._build_system_prompt(context)
        messages = self._format_messages(system_prompt, conversation_history)

        # Add current query
        messages.append({"role": "user", "content": query})

        response = self.client.chat.completions.create(
            model=self.model,
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
        """
        Generate a streaming response using OpenAI.

        Args:
            query: User query.
            context: Retrieved context from vector store.
            conversation_history: Previous conversation messages.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.

        Yields:
            Response chunks.
        """
        system_prompt = self._build_system_prompt(context)
        messages = self._format_messages(system_prompt, conversation_history)
        messages.append({"role": "user", "content": query})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content