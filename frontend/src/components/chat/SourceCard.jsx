import { FileText, Youtube, ExternalLink } from 'lucide-react';
import { SOURCE_TYPES } from '../../utils/constants';
import { formatTimestamp } from '../../utils/formatters';

export default function SourceCard({ source, onNavigate }) {
  const isPDF = source.type === SOURCE_TYPES.PDF;
  const isYouTube = source.type === SOURCE_TYPES.YOUTUBE;

  const handleClick = () => {
    if (isPDF) {
      onNavigate?.({ type: 'pdf', page: source.page, filename: source.filename });
    } else if (isYouTube) {
      onNavigate?.({ 
        type: 'youtube', 
        timestamp: source.timestamp,
        videoUrl: source.video_url 
      });
    }
  };

  return (
    <div
      onClick={handleClick}
      className="border border-current rounded-lg p-3 hover:bg-light-hover dark:hover:bg-dark-hover transition-colors cursor-pointer group"
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="p-2 rounded bg-light-hover dark:bg-dark-hover">
          {isPDF ? (
            <FileText className="w-4 h-4" />
          ) : (
            <Youtube className="w-4 h-4" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div className="flex-1">
              {isPDF ? (
                <>
                  <p className="text-sm font-medium truncate">{source.filename}</p>
                  <p className="text-xs text-light-secondary dark:text-dark-secondary">
                    Page {source.page}
                  </p>
                </>
              ) : (
                <>
                  <p className="text-sm font-medium truncate">{source.video_title}</p>
                  <p className="text-xs text-light-secondary dark:text-dark-secondary">
                    {source.timestamp_formatted || formatTimestamp(source.timestamp)}
                  </p>
                </>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-light-secondary dark:text-dark-secondary">
                {Math.round(source.score * 100)}%
              </span>
              <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </div>

          <p className="text-xs text-light-secondary dark:text-dark-secondary line-clamp-2">
            {source.text}
          </p>
        </div>
      </div>
    </div>
  );
}