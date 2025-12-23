import { X, Bookmark, ChevronRight } from 'lucide-react';
import { useBookmarks } from '../../contexts/BookmarkContext';
import { formatDate, truncateText } from '../../utils/formatters';

export default function BookmarksPanel({ isOpen, onClose, onNavigate }) {
  const { bookmarks, removeBookmark, clearBookmarks } = useBookmarks();

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-40 animate-fade-in"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed right-0 top-0 bottom-0 w-80 bg-light-bg dark:bg-dark-bg border-l border-current z-50 animate-slide-left flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-current">
          <div className="flex items-center gap-2">
            <Bookmark className="w-5 h-5" />
            <h2 className="text-lg font-semibold">Bookmarks</h2>
            {bookmarks.length > 0 && (
              <span className="text-sm text-light-secondary dark:text-dark-secondary">
                ({bookmarks.length})
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-light-hover dark:hover:bg-dark-hover rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Bookmarks List */}
        <div className="flex-1 overflow-y-auto p-4">
          {bookmarks.length === 0 ? (
            <div className="text-center py-12 text-light-secondary dark:text-dark-secondary">
              <Bookmark className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No bookmarks yet</p>
              <p className="text-sm mt-1">Click the bookmark icon on any response</p>
            </div>
          ) : (
            <div className="space-y-3">
              {bookmarks.map((bookmark) => (
                <div
                  key={bookmark.id}
                  className="border border-current rounded-lg p-3 hover:bg-light-hover dark:hover:bg-dark-hover transition-colors group cursor-pointer"
                  onClick={() => {
                    onNavigate(bookmark.id);
                    onClose();
                  }}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <p className="text-sm font-medium flex-1">
                      {truncateText(bookmark.question, 60)}
                    </p>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeBookmark(bookmark.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-light-bg dark:hover:bg-dark-bg rounded transition-all"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <p className="text-xs text-light-secondary dark:text-dark-secondary mb-2">
                    {truncateText(bookmark.answer, 80)}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-light-secondary dark:text-dark-secondary">
                    <span>{formatDate(bookmark.bookmarkedAt)}</span>
                    <ChevronRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {bookmarks.length > 0 && (
          <div className="p-4 border-t border-current">
            <button
              onClick={() => {
                if (confirm('Clear all bookmarks?')) {
                  clearBookmarks();
                }
              }}
              className="w-full py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            >
              Clear All Bookmarks
            </button>
          </div>
        )}
      </div>
    </>
  );
}