import { useNavigate } from 'react-router-dom';
import { FileText, Youtube, MessageSquare, Bookmark, Zap } from 'lucide-react';
import ThemeToggle from '../components/common/ThemeToggle';
import Button from '../components/common/Button';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    {
      icon: FileText,
      title: 'PDF Support',
      description: 'Upload and chat with any PDF document up to 25MB',
    },
    {
      icon: Youtube,
      title: 'YouTube Videos',
      description: 'Process YouTube videos and ask questions about the content',
    },
    {
      icon: MessageSquare,
      title: 'Smart Answers',
      description: 'Get accurate answers with source citations from your documents',
    },
    {
      icon: Bookmark,
      title: 'Bookmarks',
      description: 'Save important responses and quickly navigate back to them',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-current">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-black dark:bg-white rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white dark:text-black" />
            </div>
            <h1 className="text-xl font-bold">QueryVault</h1>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold mb-4">
            Chat with Your Documents
          </h2>
          <p className="text-xl text-light-secondary dark:text-dark-secondary max-w-2xl mx-auto mb-8">
            Upload PDFs or YouTube videos and ask questions. 
            Get instant answers with source citations powered by AI.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Button
              onClick={() => navigate('/upload')}
              size="lg"
              className="text-lg"
            >
              Get Started
            </Button>
            <Button
              onClick={() => navigate('/upload')}
              variant="secondary"
              size="lg"
              className="text-lg"
            >
              Upload Content
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-16">
          {features.map((feature, index) => (
            <div
              key={index}
              className="border border-current rounded-lg p-6 hover:bg-light-hover dark:hover:bg-dark-hover transition-all"
            >
              <div className="w-12 h-12 bg-black dark:bg-white rounded-lg flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-white dark:text-black" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-light-secondary dark:text-dark-secondary">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* How It Works */}
        <div className="text-center mb-16">
          <h3 className="text-3xl font-bold mb-8">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="w-12 h-12 bg-black dark:bg-white text-white dark:text-black rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                1
              </div>
              <h4 className="font-semibold mb-2">Upload Content</h4>
              <p className="text-sm text-light-secondary dark:text-dark-secondary">
                Upload a PDF or paste a YouTube URL
              </p>
            </div>
            <div>
              <div className="w-12 h-12 bg-black dark:bg-white text-white dark:text-black rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                2
              </div>
              <h4 className="font-semibold mb-2">Ask Questions</h4>
              <p className="text-sm text-light-secondary dark:text-dark-secondary">
                Type your questions in natural language
              </p>
            </div>
            <div>
              <div className="w-12 h-12 bg-black dark:bg-white text-white dark:text-black rounded-full flex items-center justify-center mx-auto mb-4 text-xl font-bold">
                3
              </div>
              <h4 className="font-semibold mb-2">Get Answers</h4>
              <p className="text-sm text-light-secondary dark:text-dark-secondary">
                Receive accurate answers with source citations
              </p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center border border-current rounded-lg p-12">
          <h3 className="text-2xl font-bold mb-4">Ready to get started?</h3>
          <p className="text-light-secondary dark:text-dark-secondary mb-6">
            Start chatting with your documents in seconds
          </p>
          <Button
            onClick={() => navigate('/upload')}
            size="lg"
          >
            Upload Your First Document
          </Button>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-current mt-16">
        <div className="max-w-6xl mx-auto px-6 py-8 text-center text-sm text-light-secondary dark:text-dark-secondary">
          <p>QueryVault - RAG-based PDF and YouTube Chatbot</p>
        </div>
      </footer>
    </div>
  );
}