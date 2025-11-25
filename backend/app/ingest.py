"""
pdf ingestion pipeline
pdf upload -> text extraction -> text chunking -> embedding generation -> vector storage in Pinecone
"""

import os
from typing import Dict
from fastapi import UploadFile
from .utils import extract_text_from_pdf, chunk_text, generate_embeddings
from .db import upsert_vectors

def process_pdf(file: UploadFile) -> Dict:
    """
    Complete Pdf processing pipeline
    workflow:
    extract text from pdf -> chunk text -> generate embeddings -> store in pinecone -> return processing summary

    Args:
        file: FastAPI UploadFile object
    Returns:
        Dict: processing results
        {
            'success': True,
            'filename': 'document.pdf',
            'total_chunks': 15,
            'vectors_stored': 15,
            'message': 'PDF processed successfully'
        }
    """

    filename = file.filename
    try:
        print(f"\n{'='*60}")
        print(f"Processing PDF: {filename}")
        print(f"{'='*60}\n")
        print("Extracting text from PDF...\n")
        page_texts = extract_text_from_pdf(file.file)

        if not page_texts:
            raise ValueError("No text extracted from PDF.\n")
        
        print("Chunking extracted text...\n")
        chunk_size = int(os.getenv("CHUNK_SIZE", 1000))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 200))

        chunks = chunk_text(page_texts, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        if not chunks:
            raise ValueError("No text chunks created from extracted text.\n")
        
        print("Generating embeddings...\n")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = generate_embeddings(chunk_texts)
        
        print("Preparing vectors for storage in pinecone...\n")  
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector = {
                'id': f"{filename}_chunk_{i}",
                'values': embedding,
                'metadata': {
                    'filename': filename,
                    'text': chunk['text'],
                    'page': chunk['page'],
                    'chunk_index': chunk['chunk_index'],
                    'char_count': chunk['char_count']
                }
            }
            vectors.append(vector)

        print("Storing vectors in pincone...\n")
        vectors_stored = upsert_vectors(vectors)

        print(f"\n{'='*60}")
        print(f"PDF Processing Complete!")
        print(f"{'='*60}")
        print(f"   Filename: {filename}")
        print(f"   Pages processed: {len(page_texts)}")
        print(f"   Chunks created: {len(chunks)}")
        print(f"   Vectors stored: {vectors_stored}")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'filename': filename,
            'total_chunks': len(chunks),
            'vectors_stored': vectors_stored,
            'message': f'Successfully processed {filename}'
        }
    
    except Exception as e:
        print(f"Error processing PDF {filename}: {e}\n")
        return {
            'success': False,
            'filename': filename,
            'total_chunks': 0,
            'vectors_stored': 0,
            'message': f'Error processing {filename}: {e}'
        }