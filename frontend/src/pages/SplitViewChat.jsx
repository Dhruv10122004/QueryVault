import { useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import SplitView from '../components/layout/SplitView';
import PDFViewer from '../components/viewers/PDFViewer';
import YouTubePlayer from '../components/viewers/YouTubePlayer';
import ChatContainer from '../components/chat/ChatContainer';
import { SPLIT_VIEW_MODES } from '../utils/constants';
import { ArrowLeft, FileText, Youtube } from 'lucide-react';

export default function SplitViewChat() {
  const location = useLocation();
  const navigate = useNavigate();
  const { file, videoId, mode } = location.state || {};
  
  const [currentPage, setCurrentPage] = useState(1);
  const [currentTimestamp, setCurrentTimestamp] = useState(0);
  const youtubePlayerRef = useRef(null);

  const handleSourceNavigate = (source) => {
    if (source.type === 'pdf' && mode === SPLIT_VIEW_MODES.PDF) {
      setCurrentPage(source.page);
    } else if (source.type === 'youtube' && mode === SPLIT_VIEW_MODES.YOUTUBE) {
      if (youtubePlayerRef.current?.seekTo) {
        youtubePlayerRef.current.seekTo(source.timestamp);
      }
    }
  };

  if (!file && !videoId) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg mb-4">No document loaded</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-black dark:bg-white text-white dark:text-black rounded-lg hover:opacity-80"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  const renderViewer = () => {
    if (mode === SPLIT_VIEW_MODES.PDF && file) {
      return (
        <PDFViewer
          file={file}
          initialPage={currentPage}
          onPageChange={setCurrentPage}
        />
      );
    } else if (mode === SPLIT_VIEW_MODES.YOUTUBE && videoId) {
      return (
        <YouTubePlayer
          videoId={videoId}
          initialTimestamp={currentTimestamp}
          onTimeUpdate={(player) => {
            youtubePlayerRef.current = player;
          }}
        />
      );
    }
    return null;
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-current">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-light-hover dark:hover:bg-dark-hover rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          <div className="flex items-center gap-2">
            {mode === SPLIT_VIEW_MODES.PDF ? (
              <>
                <FileText className="w-5 h-5" />
                <span className="font-medium">PDF Viewer</span>
              </>
            ) : (
              <>
                <Youtube className="w-5 h-5" />
                <span className="font-medium">YouTube Viewer</span>
              </>
            )}
          </div>
        </div>

        <div className="text-sm text-light-secondary dark:text-dark-secondary">
          QueryVault
        </div>
      </header>

      {/* Split View */}
      <div className="flex-1 overflow-hidden">
        <SplitView
          leftPanel={renderViewer()}
          rightPanel={
            <ChatContainer onSourceNavigate={handleSourceNavigate} />
          }
          defaultLeftWidth={50}
          minWidth={30}
          maxWidth={70}
        />
      </div>
    </div>
  );
}