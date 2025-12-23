import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { BookmarkProvider } from './contexts/BookmarkContext';
import Home from './pages/Home';
import Upload from './pages/Upload';
import SplitViewChat from './pages/SplitViewChat';

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <BookmarkProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/chat" element={<SplitViewChat />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BookmarkProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4">404</h1>
        <p className="text-xl mb-4">Page not found</p>
        <a
          href="/"
          className="text-black dark:text-white hover:underline"
        >
          Go back home
        </a>
      </div>
    </div>
  );
}