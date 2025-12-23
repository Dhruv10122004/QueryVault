import { createContext, useContext, useState, useCallback } from "react";
const BookmarkContext = createContext();

export function BookmarkProvider({ children }) {
    const [bookmarks, setBookmarks] = useState([]);
    
    const addBookmark = useCallback((message) => {
        setBookmarks(prev => {
            if(prev.some(b => b.id === message.id)) return prev;
            return [...prev, { ...message, bookmarkedAt: Date.now()}];
        });
    }, []);

    const removeBookmark = useCallback((messageId) => {
        setBookmarks(prev => prev.filter(b => b.id !== messageId));
    }, []);

    const isBookmarked = useCallback((messageId) => {
        return bookmarks.some(b => b.id === messageId);
    }, [bookmarks]);

    const clearBookmarks = useCallback(() => {
        setBookmarks([]);
    }, []);

    return (
        <BookmarkContext.Provider
        value={{
            bookmarks,
            addBookmark,
            removeBookmark,
            isBookmarked,
            clearBookmarks
        }}
        >
            {children}
        </BookmarkContext.Provider>
    );
}

export function useBookmarks() {
    const context = useContext(BookmarkContext);
    if(!context) {
        throw new Error('useBookmarks must be used within BookmarkProvider');
    }
    return context;
}