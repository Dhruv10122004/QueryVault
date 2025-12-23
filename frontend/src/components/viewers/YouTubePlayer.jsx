import { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';

export default function YouTubePlayer({ videoId, initialTimestamp = 0, onTimeUpdate }) {
  const [player, setPlayer] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const playerRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    // Load YouTube IFrame API
    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }

    // Initialize player when API is ready
    const initPlayer = () => {
      const newPlayer = new window.YT.Player(playerRef.current, {
        videoId: videoId,
        playerVars: {
          start: initialTimestamp,
          autoplay: 0,
          controls: 1,
          modestbranding: 1,
          rel: 0,
        },
        events: {
          onReady: (event) => {
            setPlayer(event.target);
            if (initialTimestamp > 0) {
              event.target.seekTo(initialTimestamp);
            }
          },
          onStateChange: (event) => {
            setIsPlaying(event.data === window.YT.PlayerState.PLAYING);
          },
        },
      });
    };

    if (window.YT && window.YT.Player) {
      initPlayer();
    } else {
      window.onYouTubeIframeAPIReady = initPlayer;
    }

    // Cleanup
    return () => {
      if (player) {
        player.destroy();
      }
    };
  }, [videoId, initialTimestamp]);

  const togglePlay = () => {
    if (!player) return;
    if (isPlaying) {
      player.pauseVideo();
    } else {
      player.playVideo();
    }
  };

  const toggleMute = () => {
    if (!player) return;
    if (isMuted) {
      player.unMute();
    } else {
      player.mute();
    }
    setIsMuted(!isMuted);
  };

  const seekTo = (timestamp) => {
    if (!player) return;
    player.seekTo(timestamp);
    player.playVideo();
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      containerRef.current.requestFullscreen();
    }
  };

  // Expose seekTo method to parent
  useEffect(() => {
    if (onTimeUpdate && player) {
      onTimeUpdate({ seekTo });
    }
  }, [player, onTimeUpdate]);

  return (
    <div 
      ref={containerRef}
      className="h-full flex flex-col bg-black"
    >
      {/* Video Container */}
      <div className="flex-1 relative">
        <div 
          ref={playerRef}
          className="absolute inset-0 w-full h-full"
        />
      </div>

      {/* Custom Controls Overlay (optional minimal controls) */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 opacity-0 hover:opacity-100 transition-opacity">
        <div className="flex items-center justify-between text-white">
          <div className="flex items-center gap-2">
            <button
              onClick={togglePlay}
              className="p-2 hover:bg-white/20 rounded transition-colors"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            </button>

            <button
              onClick={toggleMute}
              className="p-2 hover:bg-white/20 rounded transition-colors"
            >
              {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
            </button>
          </div>

          <button
            onClick={toggleFullscreen}
            className="p-2 hover:bg-white/20 rounded transition-colors"
          >
            <Maximize className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}