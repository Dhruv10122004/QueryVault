import { Bookmark } from 'lucide-react';
import { useBookmarks } from '../../contexts/BookmarkContext';

export default function BookmarkButton({ message, className = '' }) {
  const { isBookmarked, addBookmark, removeBookmark } = useBookmarks();
  const bookmarked = isBookmarked(message.id);

  const handleClick = () => {
    if (bookmarked) {
      removeBookmark(message.id);
    } else {
      addBookmark(message);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`p-2 rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover transition-all focus-ring group ${className}`}
      aria-label={bookmarked ? 'Remove bookmark' : 'Add bookmark'}
      title={bookmarked ? 'Remove bookmark' : 'Bookmark this response'}
    >
      <Bookmark 
        className={`w-5 h-5 transition-all ${
          bookmarked 
            ? 'fill-current' 
            : 'group-hover:fill-current group-hover:opacity-50'
        }`}
      />
    </button>
  );
}