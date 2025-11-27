"""
Question answering logic
Handles: question -> embedding -> similarity search -> context retrieval -> answer generation
"""

from typing import List, Dict
from .utils import generate_query_embedding, generate_answer
from .db import search_vectors

def answer_question(question: str, top_k: int = 3) -> Dict:
    """
    Answer a question using RAG (Retrieval-Augmented Generation).
    
    Workflow:
    1. Generate embedding for the question
    2. Search Pinecone for similar chunks
    3. Retrieve context from matches
    4. Generate answer using Gemini with context
    5. Return answer with sources
    
    Args:
        question: User's question
        top_k: Number of similar chunks to retrieve (default: 3)
    
    Returns:
        Dictionary with answer and sources:
        {
            'success': True,
            'question': 'What is the refund policy?',
            'answer': 'According to the document...',
            'sources': [
                {
                    'text': 'chunk text...',
                    'score': 0.89,
                    'page': 5,
                    'filename': 'doc.pdf'
                },
                ...
            ]
        }
    """

    try:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n")

        print("Generating query embedding...")
        query_embedding = generate_query_embedding(question)

        print(f"\nSearching for top {top_k} similar chunks...")
        matches = search_vectors(query_embedding, top_k=top_k)

        if not matches:
            return {
                'success': True,
                'question': question,
                'answer': "I couldn't find any relevant information in the uploaded documents.",
                'sources': []
            }
        
        print("\nFormatting resources")
        
        # Prepare sources for display
        sources = []
        # Prepare context chunks for generate_answer (flatten the metadata structure)
        context_chunks = []
        
        for match in matches:
            # For displaying to user
            source = {
                'text': match['metadata'].get('text', '')[:200] + '...',
                'score': round(match['score'], 3),
                'page': match['metadata'].get('page', 'N/A'),
                'filename': match['metadata'].get('filename', 'N/A')
            }
            sources.append(source)
            print(f"Page {source['page']} (score: {source['score']})")
            
            # For passing to generate_answer (flatten structure)
            context_chunk = {
                'text': match['metadata'].get('text', ''),
                'page': match['metadata'].get('page', 'N/A'),
                'chunk_index': match['metadata'].get('chunk_index', 0),
                'filename': match['metadata'].get('filename', 'N/A')
            }
            context_chunks.append(context_chunk)

        print("\nGenerating answer with Gemini...")
        answer = generate_answer(question, context_chunks)

        print(f"\n{'='*60}")
        print(f"Answer Generated!")
        print(f"{'='*60}")
        print(f"   Question: {question}")
        print(f"   Sources used: {len(sources)}")
        print(f"   Answer length: {len(answer)} chars")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'question': question,
            'answer': answer,
            'sources': sources
        }
    
    except Exception as e:
        print(f"\nError in answering question: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'question': question,
            'answer': f"An error occurred while processing your question: {str(e)}",
            'sources': []
        }