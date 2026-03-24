"""
Document chunking utilities.
"""
from typing import List, Generator
import re
from app.config import settings


def chunk_text(
    text: str,
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of characters to overlap between chunks.

    Returns:
        List of text chunks.
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    if len(text) <= chunk_size:
        return [text.strip()]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to find a good break point
        if end < len(text):
            # Look for paragraph break
            paragraph_break = text.rfind('\n\n', start, end)
            if paragraph_break > start + chunk_size // 2:
                end = paragraph_break
            else:
                # Look for sentence break
                sentence_break = text.rfind('. ', start, end)
                if sentence_break > start + chunk_size // 2:
                    end = sentence_break + 1
                else:
                    # Look for word break
                    word_break = text.rfind(' ', start, end)
                    if word_break > start:
                        end = word_break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap
        if start < 0:
            start = 0

    return chunks


def chunk_by_sections(
    text: str,
    section_markers: List[str] = None
) -> List[dict]:
    """
    Split text by sections (e.g., FAQ Q&A pairs).

    Args:
        text: Text to chunk.
        section_markers: List of markers that indicate new sections.

    Returns:
        List of section dictionaries with title and content.
    """
    if section_markers is None:
        section_markers = ['Q:', 'Question:', 'FAQ:', '###']

    sections = []
    current_section = ""
    current_title = "Introduction"

    lines = text.split('\n')

    for line in lines:
        is_new_section = any(line.strip().startswith(marker) for marker in section_markers)

        if is_new_section:
            if current_section.strip():
                sections.append({
                    'title': current_title,
                    'content': current_section.strip()
                })
            current_title = line.strip()
            current_section = line + '\n'
        else:
            current_section += line + '\n'

    # Don't forget the last section
    if current_section.strip():
        sections.append({
            'title': current_title,
            'content': current_section.strip()
        })

    return sections


def smart_chunk(
    text: str,
    doc_type: str = "general",
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[dict]:
    """
    Intelligently chunk text based on document type.

    Args:
        text: Text to chunk.
        doc_type: Type of document (faq, policy, guide, general).
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between chunks.

    Returns:
        List of chunk dictionaries with content and metadata.
    """
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    if doc_type == "faq":
        # For FAQs, try to keep Q&A pairs together
        sections = chunk_by_sections(text, ['Q:', 'Question:'])
        chunks = []
        for section in sections:
            if len(section['content']) <= chunk_size:
                chunks.append({
                    'content': section['content'],
                    'metadata': {'title': section['title'], 'type': 'qa_pair'}
                })
            else:
                # Split large sections
                sub_chunks = chunk_text(section['content'], chunk_size, chunk_overlap)
                for sub in sub_chunks:
                    chunks.append({
                        'content': sub,
                        'metadata': {'title': section['title'], 'type': 'qa_pair'}
                    })
        return chunks

    else:
        # General chunking
        text_chunks = chunk_text(text, chunk_size, chunk_overlap)
        return [
            {
                'content': chunk,
                'metadata': {'type': 'text_chunk', 'chunk_index': i}
            }
            for i, chunk in enumerate(text_chunks)
        ]