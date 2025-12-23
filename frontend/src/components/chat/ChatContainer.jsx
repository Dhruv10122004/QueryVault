import { useState, useRef, useEffect } from 'react';
import { Bookmark } from 'lucide-react';
import Message from './Message';
import ChatInput from './ChatInput';
import BookmarksPanel from './BookmarksPanel';
import { queryDocuments } from '../../services/api';

export default function ChatContainer({ onSourceNavigate, className = '' }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [bookmarksPanelOpen, setBookmarksPanelOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToMessage = (messageId) => {
    const element = document.getElementById(`message-${messageId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Highlight effect
      element.classList.add('ring-2', 'ring-black', 'dark:ring-white', 'rounded-lg');
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-black', 'dark:ring-white', 'rounded-lg');
      }, 2000);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (question) => {
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: question,
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await queryDocuments(question, 3);
      
      const botMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.answer,
        question: question,
        sources: response.sources || [],
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        sources: [],
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-current">
        <div>
          <h2 className="text-lg font-semibold">Chat</h2>
          <p className="text-sm text-light-secondary dark:text-dark-secondary">
            Ask questions about your documents
          </p>
        </div>
        
        <button
          onClick={() => setBookmarksPanelOpen(true)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover transition-colors"
        >
          <Bookmark className="w-5 h-5" />
          <span className="text-sm">Bookmarks</span>
        </button>
      </div>

      {/* Messages */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-6"
      >
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center">
            <div>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-light-hover dark:bg-dark-hover flex items-center justify-center">
                <svg 
                  className="w-8 h-8" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
                  />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
              <p className="text-sm text-light-secondary dark:text-dark-secondary max-w-md">
                Upload a PDF or YouTube video, then ask any question about the content.
                I'll search through the documents and provide answers with sources.
              </p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              message={message}
              onSourceNavigate={onSourceNavigate}
            />
          ))
        )}
        
        {loading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-black dark:bg-white flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-white dark:text-black animate-spin" viewBox="0 0 24 24">
                <circle 
                  className="opacity-25" 
                  cx="12" 
                  cy="12" 
                  r="10" 
                  stroke="currentColor" 
                  strokeWidth="4"
                  fill="none"
                />
                <path 
                  className="opacity-75" 
                  fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <div className="bg-light-hover dark:bg-dark-hover rounded-lg p-4">
                <p className="text-light-secondary dark:text-dark-secondary">Thinking...</p>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSend} loading={loading} />

      {/* Bookmarks Panel */}
      <BookmarksPanel
        isOpen={bookmarksPanelOpen}
        onClose={() => setBookmarksPanelOpen(false)}
        onNavigate={scrollToMessage}
      />
    </div>
  );
}