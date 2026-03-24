"""
Script to load sample documents into the vector store.
Run this after setting up the backend.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vectorstore import VectorStoreService
from app.utils.chunking import smart_chunk


def load_sample_documents():
    """Load sample documents from data/sample_docs into vector store."""
    vector_store = VectorStoreService()

    sample_docs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_docs')

    # Get all text files
    for filename in os.listdir(sample_docs_dir):
        if filename.endswith('.txt') or filename.endswith('.md'):
            filepath = os.path.join(sample_docs_dir, filename)

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine document type
            doc_type = 'faq' if 'faq' in filename.lower() else 'policy'

            # Chunk the document
            chunks = smart_chunk(content, doc_type=doc_type)

            # Prepare data
            documents = [chunk['content'] for chunk in chunks]
            metadatas = [
                {
                    **chunk['metadata'],
                    'source': filename,
                    'category': 'support',
                    'doc_type': doc_type
                }
                for chunk in chunks
            ]

            # Add to vector store
            ids = vector_store.add_documents(documents=documents, metadatas=metadatas)

            print(f"Loaded {len(ids)} chunks from {filename}")

    print(f"\nTotal documents in store: {vector_store.get_document_count()}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Loading sample documents...")
    load_sample_documents()
    print("Done!")