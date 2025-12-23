import { useState } from 'react';
import { Send, Loader } from 'lucide-react';

export default function ChatInput({ onSend, disabled = false, loading = false }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-current p-4 bg-light-bg dark:bg-dark-bg">
      <div className="max-w-4xl mx-auto">
        <div className="relative flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            disabled={disabled || loading}
            rows={1}
            className="flex-1 resize-none rounded-lg border border-current bg-transparent px-4 py-3 pr-12 focus-ring disabled:opacity-50 disabled:cursor-not-allowed max-h-32 overflow-y-auto"
            style={{
              minHeight: '3rem',
              height: 'auto',
            }}
            onInput={(e) => {
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px';
            }}
          />

          <button
            type="submit"
            disabled={!input.trim() || disabled || loading}
            className="absolute right-3 bottom-3 p-2 rounded-lg bg-black dark:bg-white text-white dark:text-black hover:opacity-80 disabled:opacity-30 disabled:cursor-not-allowed transition-all focus-ring"
          >
            {loading ? (
              <Loader className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        <p className="text-xs text-light-secondary dark:text-dark-secondary mt-2 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </form>
  );
}