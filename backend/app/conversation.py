from typing import List, Dict, Optional
from datetime import datetime, timedelta

class ConversationManager:
    def __init__(self, max_history: int = 5, ttl_minutes: int = 30):
        self.conversations: Dict[str, Dict] = {}
        self.max_history = max_history
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def add_message(self, session_id: str, role: str, content: str, sources: List[Dict] = None):
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                'messages': [],
                'last_updated': datetime.utcnow(),
                'context_chunks': []
            }
        
        conv = self.conversations[session_id]
        conv['messages'].append({
            'role': role,
            'content': content,
            'sources': sources or [],
            'timestamp': datetime.now()
        })

        conv['messages'] = conv['messages'][-self.max_history:]
        conv['last_updated'] = datetime.now()

        if sources:
            conv['context_chunks'].extend([s.get('text', '') for s in sources])
            conv['context_chunks'] = conv['context_chunks'][-10:]

    def get_conversation_context(self, session_id: str) -> str:
        if session_id not in self.conversations:
            return ""
        
        conv = self.conversations[session_id]

        if datetime.now() - conv['last_updated'] > self.ttl:
            del self.conversations[session_id]
            return ""
        
        context_parts = []
        for msg in conv['messages'][-3:]:
            context_parts.append(f"{msg['role'].title()}: {msg['content']}")

        return "\n".join(context_parts)
    
    def get_previous_sources(self, session_id: str) -> List[str]:
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id].get('context_chunks', [])
    
    def clear_conversation(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]

conversation_manager = ConversationManager()