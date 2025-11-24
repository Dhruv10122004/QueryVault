"""
Pinecone vector database operations.
Handles connections, upserting vectors and similarity search
"""

import os
from typing import List, Dict
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

_pinecone_client = None
_pinecone_index = None

def get_pinecone_client():
    global _pinecone_client

    if _pinecone_client is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment")
        _pinecone_client = Pinecone(api_key=api_key)
        print("Pinecone client initialized")
    return _pinecone_client

def get_pinecone_index():
    global _pinecone_index

    if _pinecone_index is None:
        client  = get_pinecone_client()
        index_name = os.getenv("PINECONE_INDEX_NAME", "pdf-chatbot-index")
        
        available_indexes = [ind.name for ind in client.list_indexes()]
        if index_name not in available_indexes:
            raise ValueError(f"Pinecone index '{index_name}' not found. Available indexes: {available_indexes}")
        _pinecone_index = client.Index(index_name)
        print(f"Pinecone index '{index_name}' connected")
    return _pinecone_index

def upsert_vectors(vectors: List[Dict]):
    try:
        index = get_pinecone_index()
        batch_size = 100
        totalupserted = 0

        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            totalupserted += len(batch)
            print(f"Upserted batch {i//batch_size + 1}: {len(batch)} vectors")

        print(f"Total vectors upserted: {totalupserted}")
        return totalupserted
    except Exception as e:
        print(f"Error upserting vectors: {e}")
        raise

def search_vectors(query_embedding: List[float], top_k: int = 3) -> List[Dict]:
    """
    Search for similar vectors in Pinecone.
    
    Args:
        query_embedding: The question's embedding vector
        top_k: Number of similar results to return
    
    Returns:
        List of matches with metadata and scores:
        [
            {
                'id': 'doc_1_chunk_0',
                'score': 0.89,
                'metadata': {'text': '...', 'filename': '...', 'page': 1}
            },
            ...
        ]
    """
    try:
        index = get_pinecone_index()

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )

        matches = []

        for match in results['matches']:
            matches.append({
                'id': match['id'],
                'score': match['score'],
                'metadata': match.get('metadata', {})
            })
        
        print(f"Found {len(matches)} similar chunks")
        return matches
    except Exception as e:
        print(f"Error searching vectors: {e}")
        raise

def delete_all_vectors():

    try:
        index = get_pinecone_index()
        index.delete(delete_all=True)
        print("All vectors deleted from Pinecone index")
    except Exception as e:
        print(f"Error deleting vectors: {e}")
        raise

def get_index_stats():
    try:
        index = get_pinecone_index()
        stats = index.describe_index_stats()
        return {
            'total_vectors': stats.total_vector_count,
            'dimension': stats.dimension,
            'index_fullness': stats.index_fullness
        }
    except Exception as e:
        print(f"Error getting index stats: {e}")
        raise
    