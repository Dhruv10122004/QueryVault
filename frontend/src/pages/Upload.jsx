import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Youtube, Upload as UploadIcon, Loader, CheckCircle, XCircle } from 'lucide-react';
import Button from '../components/common/Button';
import { uploadPDF, uploadYouTube } from '../services/api';
import { MAX_PDF_SIZE_MB, SPLIT_VIEW_MODES } from '../utils/constants';
import { formatFileSize } from '../utils/formatters';

export default function Upload() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('pdf');
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handlePDFUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > MAX_PDF_SIZE_MB * 1024 * 1024) {
      setError(`File too large. Maximum size is ${MAX_PDF_SIZE_MB}MB`);
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadPDF(file, (percent) => {
        setProgress(percent);
      });

      setResult({
        success: true,
        message: response.message,
        filename: response.filename,
        chunks: response.total_chunks,
      });

      // Auto-navigate to split view after 2 seconds
      setTimeout(() => {
        navigate('/chat', {
          state: {
            file: file,
            mode: SPLIT_VIEW_MODES.PDF,
          },
        });
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleYouTubeUpload = async (e) => {
    e.preventDefault();
    const form = e.target;
    const url = form.url.value.trim();

    if (!url) return;

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadYouTube(url);

      setResult({
        success: true,
        message: response.message,
        videoTitle: response.video_title,
        chunks: response.total_chunks,
      });

      // Auto-navigate to split view after 2 seconds
      setTimeout(() => {
        navigate('/chat', {
          state: {
            videoId: response.video_id,
            mode: SPLIT_VIEW_MODES.YOUTUBE,
          },
        });
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Upload Content</h1>
          <p className="text-light-secondary dark:text-dark-secondary">
            Upload a PDF or paste a YouTube URL to get started
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('pdf')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border transition-all ${
              activeTab === 'pdf'
                ? 'bg-black dark:bg-white text-white dark:text-black border-transparent'
                : 'border-current hover:bg-light-hover dark:hover:bg-dark-hover'
            }`}
          >
            <FileText className="w-5 h-5" />
            <span className="font-medium">PDF</span>
          </button>
          <button
            onClick={() => setActiveTab('youtube')}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg border transition-all ${
              activeTab === 'youtube'
                ? 'bg-black dark:bg-white text-white dark:text-black border-transparent'
                : 'border-current hover:bg-light-hover dark:hover:bg-dark-hover'
            }`}
          >
            <Youtube className="w-5 h-5" />
            <span className="font-medium">YouTube</span>
          </button>
        </div>

        {/* Upload Area */}
        <div className="border border-current rounded-lg p-8">
          {activeTab === 'pdf' ? (
            <div className="text-center">
              <label className="cursor-pointer block">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handlePDFUpload}
                  disabled={uploading}
                  className="hidden"
                />
                <div className="p-12 border-2 border-dashed border-current rounded-lg hover:bg-light-hover dark:hover:bg-dark-hover transition-all">
                  <UploadIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">
                    {uploading ? 'Uploading...' : 'Click to upload PDF'}
                  </p>
                  <p className="text-sm text-light-secondary dark:text-dark-secondary">
                    Maximum file size: {MAX_PDF_SIZE_MB}MB
                  </p>
                </div>
              </label>
            </div>
          ) : (
            <form onSubmit={handleYouTubeUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  YouTube URL
                </label>
                <input
                  type="url"
                  name="url"
                  placeholder="https://www.youtube.com/watch?v=..."
                  disabled={uploading}
                  className="w-full px-4 py-3 border border-current rounded-lg bg-transparent focus-ring disabled:opacity-50"
                  required
                />
              </div>
              <Button
                type="submit"
                disabled={uploading}
                loading={uploading}
                className="w-full"
              >
                Process Video
              </Button>
            </form>
          )}

          {/* Progress */}
          {uploading && progress > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between text-sm mb-2">
                <span>Uploading...</span>
                <span>{progress}%</span>
              </div>
              <div className="h-2 bg-light-hover dark:bg-dark-hover rounded-full overflow-hidden">
                <div
                  className="h-full bg-black dark:bg-white transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="mt-6 p-4 border border-current rounded-lg bg-light-hover dark:bg-dark-hover animate-fade-in">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium mb-1">Success!</p>
                  <p className="text-sm text-light-secondary dark:text-dark-secondary">
                    {result.message}
                  </p>
                  <p className="text-xs text-light-secondary dark:text-dark-secondary mt-2">
                    Redirecting to chat...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-6 p-4 border border-red-600 rounded-lg bg-red-50 dark:bg-red-900/20 animate-fade-in">
              <div className="flex items-start gap-3">
                <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-red-600 mb-1">Error</p>
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="text-center mt-6">
          <button
            onClick={() => navigate('/')}
            className="text-sm text-light-secondary dark:text-dark-secondary hover:text-light-text dark:hover:text-dark-text transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}