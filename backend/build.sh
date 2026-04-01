#!/usr/bin/env bash
# Build script for Render

set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Load sample documents into vector store
python -c "
from app.services.vectorstore import VectorStoreService
from app.utils.chunking import chunk_text
import os

print('Loading sample documents into vector store...')
vs = VectorStoreService()

docs_path = 'data/sample_docs'
if os.path.exists(docs_path):
    for filename in os.listdir(docs_path):
        if filename.endswith('.txt'):
            filepath = os.path.join(docs_path, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            chunks = chunk_text(content, chunk_size=500, chunk_overlap=50)
            vs.add_documents(chunks, metadatas=[{'source': filename} for _ in chunks])
            print(f'Loaded {len(chunks)} chunks from {filename}')

print(f'Total documents loaded: {vs.get_document_count()}')
"

echo "Build completed successfully!"
