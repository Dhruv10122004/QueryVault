"""
Question answering logic
Handles: question -> embedding -> similarity search -> context retrieval -> answer generation
"""

import re
from typing import List, Dict
from .utils import generate_query_embedding, generate_answer_with_history
from .db import search_vectors
from .conversation import conversation_manager

def answer_question(question: str, top_k: int = 3, session_id: str = None) -> Dict:
    """
    Answer question with follow-up support
    """
    try:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        if session_id:
            print(f"Session ID: {session_id}")
        print(f"{'='*60}\n")

        is_follow_up = detect_follow_up(question) if session_id else False
        search_query = expand_query_with_context(question, session_id) if is_follow_up else question
        
        print(f"Follow-up detected: {is_follow_up}")
        if is_follow_up:
            print(f"Expanded query for search: {search_query[:200]}...")

        query_embedding = generate_query_embedding(search_query)
        matches = search_vectors(query_embedding, top_k=top_k)

        if not matches:
            response = {
                'success': True,
                'question': question,
                'answer': "I couldn't find relevant information in the uploaded documents.",
                'sources': [],
                'is_follow_up': is_follow_up
            }
            
            if session_id:
                conversation_manager.add_message(session_id, 'user', question)
                conversation_manager.add_message(session_id, 'assistant', response['answer'])
            
            return response
        
        sources = []
        context_chunks = []
        
        for match in matches:
            metadata = match.get('metadata', {})
            content_type = metadata.get('content_type', 'pdf')
            
            if content_type == 'youtube':
                source = {
                    'type': 'youtube',
                    'text': metadata.get('text', '')[:200] + '...',
                    'score': round(match['score'], 3),
                    'video_title': metadata.get('video_title', 'N/A'),
                    'video_url': metadata.get('video_url', 'N/A'),
                    'timestamp': metadata.get('timestamp_start', 0),
                    'timestamp_formatted': f"{int(metadata.get('timestamp_start', 0)) // 60}:{int(metadata.get('timestamp_start', 0)) % 60:02d}"
                }
            else:
                source = {
                    'type': 'pdf',
                    'text': metadata.get('text', '')[:200] + '...',
                    'score': round(match['score'], 3),
                    'page': metadata.get('page', 'N/A'),
                    'filename': metadata.get('filename', 'N/A')
                }
            
            sources.append(source)
            context_chunks.append({
                'text': match['metadata'].get('text', ''),
                'metadata': match['metadata']
            })

        conversation_history = None
        if session_id:
            conversation_history = conversation_manager.get_conversation_context(session_id)

        answer = generate_answer_with_history(
            question=question,
            context_chunks=context_chunks,
            conversation_history=conversation_history,
            is_follow_up=is_follow_up
        )

        print(f"\nAnswer Generated! (Follow-up: {is_follow_up})")
        
        response = {
            'success': True,
            'question': question,
            'answer': answer,
            'sources': sources,
            'is_follow_up': is_follow_up
        }
        
        if session_id:
            conversation_manager.add_message(session_id, 'user', question)
            conversation_manager.add_message(session_id, 'assistant', answer, sources)
        
        return response
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'question': question,
            'answer': f"Error: {str(e)}",
            'sources': [],
            'is_follow_up': False
        }

def enhance_with_context(matches: List[Dict], query_embedding: List[float]) -> List[Dict]:
    """
    Enhance retrieved chunks with surrounding context from same document
    """
    by_document = {}
    for match in matches:
        metadata = match['metadata']
        filename = metadata.get('filename', 'unknown')
        page = metadata.get('page', 0)
        chunk_idx = metadata.get('chunk_index', 0)
        
        key = f"{filename}_page_{page}"
        if key not in by_document:
            by_document[key] = []
        by_document[key].append((chunk_idx, match))
    
    enhanced = []
    for matches_group in by_document.values():
        matches_group.sort(key=lambda x: x[0])  
        for chunk_idx, match in matches_group:
            enhanced.append(match)
    
    return enhanced

def detect_follow_up(question: str) -> bool:
    follow_up_patterns = [
        r'\b(it|this|that|they|them|these|those)\b',
        r'\b(what about|how about|tell me more|explain|elaborate)\b',
        r'\b(also|additionally|furthermore|moreover)\b',
        r'^(and|but|so|because|however)',
    ]
    
    question_lower = question.lower()
    return any(re.search(pattern, question_lower) for pattern in follow_up_patterns)

def expand_query_with_context(question: str, session_id: str) -> str:
    if not detect_follow_up(question):
        return question
    
    conv_context = conversation_manager.get_conversation_context(session_id)
    if not conv_context:
        return question

    expanded = f"""Given the previous conversation:
{conv_context}

Current question: {question}

Interpret this question in the context of the previous discussion."""
    
    return expanded