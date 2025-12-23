import { useState, useRef, useEffect } from 'react';
import { GripVertical } from 'lucide-react';

export default function SplitView({ 
  leftPanel, 
  rightPanel, 
  defaultLeftWidth = 50,
  minWidth = 30,
  maxWidth = 70 
}) {
  const [leftWidth, setLeftWidth] = useState(defaultLeftWidth);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging || !containerRef.current) return;

      const container = containerRef.current;
      const containerRect = container.getBoundingClientRect();
      const newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;

      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setLeftWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, minWidth, maxWidth]);

  return (
    <div ref={containerRef} className="flex h-full relative select-none">
      {/* Left Panel */}
      <div style={{ width: `${leftWidth}%` }} className="overflow-hidden">
        {leftPanel}
      </div>

      {/* Resizer */}
      <div
        className="w-1 hover:w-2 bg-light-border dark:bg-dark-border hover:bg-black dark:hover:bg-white transition-all cursor-col-resize relative group flex items-center justify-center"
        onMouseDown={() => setIsDragging(true)}
      >
        <div className="absolute opacity-0 group-hover:opacity-100 transition-opacity">
          <GripVertical className="w-4 h-4" />
        </div>
      </div>

      {/* Right Panel */}
      <div style={{ width: `${100 - leftWidth}%` }} className="overflow-hidden">
        {rightPanel}
      </div>
    </div>
  );
}