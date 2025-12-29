import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import BookmarkButton from '../common/BookmarkButton';
import SourceCard from './SourceCard';

export default function Message({ message, onSourceNavigate }) {
  const isUser = message.role === 'user';

  return (
    <div
      id={`message-${message.id}`}
      className="scroll-mt-20 animate-slide-up"
    >
      <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-black dark:bg-white flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-white dark:text-black" />
          </div>
        )}

        <div className={`flex-1 max-w-3xl ${isUser ? 'flex justify-end' : ''}`}>
          <div className={`${isUser ? 'max-w-xl' : 'w-full'}`}>
            {/* Message Content */}
            <div
              className={`rounded-lg p-4 ${
                isUser
                  ? 'bg-black dark:bg-white text-white dark:text-black'
                  : 'bg-light-hover dark:bg-dark-hover'
              }`}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap">{message.content}</p>
              ) : (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown
                    components={{
                      // Customize rendering of markdown elements
                      p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                      strong: ({node, ...props}) => <strong className="font-semibold" {...props} />,
                      em: ({node, ...props}) => <em className="italic" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-2" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                      li: ({node, ...props}) => <li className="mb-1" {...props} />,
                      code: ({node, inline, ...props}) => 
                        inline ? (
                          <code className="bg-light-bg dark:bg-dark-bg px-1 py-0.5 rounded text-sm" {...props} />
                        ) : (
                          <code className="block bg-light-bg dark:bg-dark-bg p-2 rounded text-sm overflow-x-auto" {...props} />
                        ),
                      h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-2" {...props} />,
                      h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-2" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-base font-bold mb-2" {...props} />,
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>

            {/* Sources (only for bot responses) */}
            {!isUser && message.sources && message.sources.length > 0 && (
              <div className="mt-3 space-y-2">
                <p className="text-xs font-medium text-light-secondary dark:text-dark-secondary px-1">
                  Sources ({message.sources.length})
                </p>
                {message.sources.map((source, idx) => (
                  <SourceCard
                    key={idx}
                    source={source}
                    onNavigate={onSourceNavigate}
                  />
                ))}
              </div>
            )}

            {/* Bookmark Button (only for bot responses) */}
            {!isUser && (
              <div className="flex justify-end mt-2">
                <BookmarkButton 
                  message={{
                    id: message.id,
                    question: message.question,
                    answer: message.content,
                    sources: message.sources,
                  }} 
                />
              </div>
            )}
          </div>
        </div>

        {isUser && (
          <div className="w-8 h-8 rounded-full bg-black dark:bg-white flex items-center justify-center flex-shrink-0">
            <User className="w-5 h-5 text-white dark:text-black" />
          </div>
        )}
      </div>
    </div>
  );
}