"""
YouTube video processing module -> extracts transcripts and processes them like PDFs.
"""

import os 
import re
import tempfile
from typing import Dict, List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import yt_dlp
# import whisper
from .config import Config
from .utils import generate_embeddings
from .db import upsert_vectors

_whisper_model = None
ytt_api = YouTubeTranscriptApi()

def get_whisper_model():
    """Lazy loading whisper model."""
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model... This may take a moment on first run.")
        # _whisper_model = whisper.load_model("base")
    return _whisper_model

def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError(
        "Invalid YouTube URL. Please provide a valid URL like:\n"
        "  - https://www.youtube.com/watch?v=VIDEO_ID\n"
        "  - https://youtu.be/VIDEO_ID"
    )

def get_video_info(video_id: str) -> Dict:
    """Get video metadata using yt-dlp"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return {
                'video_id': video_id,
                'title': info.get('title', 'Unknown'),
                'channel': info.get('channel', 'Unknown'),  # Fixed: was 'duration'
                'duration': info.get('duration', 0),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        raise ValueError(f"Error fetching video info: {str(e)}")

def fetch_existing_transcript(video_id: str) -> Optional[List[Dict]]:
    """Fetch transcripts using the correct API method"""
    try:
        # Use fetch directly for English
        try:
            print("Attempting to fetch English transcript...")
            transcript = ytt_api.fetch(video_id, languages=['en'])
            print(f"✓ Found English transcript ({len(transcript)} segments)")
            return transcript
        except NoTranscriptFound:
            print("No English transcript found, trying other languages...")
            pass
        
        # Try to get any available transcript
        try:
            # Get list of available transcripts
            transcript_list = ytt_api().list_transcripts(video_id)
            
            # Try to find a manually created transcript first
            for transcript in transcript_list:
                if not transcript.is_generated:
                    print(f"Found manual transcript in {transcript.language}")
                    if transcript.language_code != 'en':
                        print(f"Translating {transcript.language_code} -> English...")
                        translated = transcript.translate('en')
                        result = translated.fetch()
                    else:
                        result = transcript.fetch()
                    print(f"✓ Retrieved {len(result)} segments")
                    return result
            
            # If no manual transcript, use auto-generated
            for transcript in transcript_list:
                if transcript.is_generated:
                    print(f"Found auto-generated transcript in {transcript.language}")
                    if transcript.language_code != 'en':
                        print(f"Translating {transcript.language_code} -> English...")
                        translated = transcript.translate('en')
                        result = translated.fetch()
                    else:
                        result = transcript.fetch()
                    print(f"✓ Retrieved {len(result)} segments")
                    return result
                    
        except Exception as e:
            print(f"Error accessing transcript list: {e}")
            pass
            
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        print(f"No transcripts available: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching transcript: {e}")
        return None
    
    return None

def download_audio(video_id: str, output_path: str) -> str:
    """Download audio from youtube video"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        return output_path + ".mp3"
    except Exception as e:
        raise ValueError(f"Failed to download audio: {str(e)}")

def transcribe_with_whisper(video_id: str) -> List[Dict]:
    """Generate transcript using Whisper (fallback method)"""
    print("Generating transcript from audio using Whisper...")
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio")

    try:
        print("Downloading audio...")
        audio_file = download_audio(video_id, audio_path)

        print("Transcribing audio with Whisper...")
        model = get_whisper_model()
        
        if model is None:
            raise ValueError("Failed to load Whisper model")
            
        result = model.transcribe(audio_file, language='en', verbose=False)

        transcript = []
        for segment in result['segments']:
            transcript.append({
                'text': segment.text.strip(),
                'start': segment.start,
                'duration': segment.end - segment.start
            })

        print(f"✓ Transcription complete ({len(transcript)} segments)")
        return transcript
    finally:
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            os.rmdir(temp_dir)
        except Exception as e:
            pass

def FETCH(video_id: str) -> List[Dict]:
    """Get transcript - try YouTube API first, fallback to Whisper if enabled"""
    transcript = fetch_existing_transcript(video_id)
    
    if transcript:
        return transcript
    
    if Config.USE_WHISPER_FALLBACK:
        print("\n  No captions available - will generate transcript locally using Whisper")
        print("  This requires Whisper to be installed and may take several minutes")
        print(" Set USE_WHISPER_FALLBACK=False in config.py to disable this\n")
        return transcribe_with_whisper(video_id)
    else:
        raise ValueError(
            "This video has no captions/transcript available.\n"
            "Enable USE_WHISPER_FALLBACK in config.py to generate transcript using Whisper model."
        )
    
def chunk_transcript_by_time(
    transcript: List[Dict],
    video_info: Dict,
    chunk_duration: int = Config.VIDEO_CHUNK_DURATION,
    overlap: int = Config.VIDEO_CHUNK_OVERLAP
) -> List[Dict]:
    """Split transcript into time-based chunks"""
    chunks = []
    current_time = 0
    video_duration = video_info['duration']

    while current_time < video_duration:
        chunk_end = min(current_time + chunk_duration, video_duration)
        chunk_texts = []
        
        for segment in transcript:
            segment_start = segment.start
            segment_end = segment.start + segment.duration

            # Include segment if it overlaps with current chunk
            if segment_start < chunk_end and segment_end > current_time:
                chunk_texts.append(segment.text)
        
        if chunk_texts:
            chunks.append({
                'text': ' '.join(chunk_texts),
                'timestamp_start': int(current_time),
                'timestamp_end': int(chunk_end),
                'video_id': video_info['video_id'],
                'video_title': video_info['title'],
                'video_url': f"{video_info['url']}&t={int(current_time)}s",
                'channel': video_info['channel'],
                'char_count': len(' '.join(chunk_texts))
            })

        current_time += chunk_duration - overlap
        
    print(f"✓ Created {len(chunks)} time-based chunks from transcript")
    return chunks

def process_youtube(url: str) -> Dict:
    """Main function to process a YouTube video"""
    try:
        print(f"\n{'='*60}")
        print(f"Processing YouTube Video")
        print(f"{'='*60}\n")

        print("Extracting video ID...")
        video_id = extract_video_id(url)
        print(f"✓ Video ID: {video_id}\n")

        print("Fetching video info...")
        video_info = get_video_info(video_id)
        print(f" Title: {video_info['title']}")
        print(f"Channel: {video_info['channel']}")
        print(f"Duration: {video_info['duration']//60}m {video_info['duration']%60}s\n")

        if video_info['duration'] > Config.MAX_VIDEO_DURATION_SECONDS:
            raise ValueError(
                f"Video too long ({video_info['duration']//60}m). "
                f"Maximum allowed: {Config.MAX_VIDEO_DURATION_HOURS}h"
            )
        
        print("Getting transcript...")
        transcript = FETCH(video_id)
        total_words = sum(len(seg.text.split()) for seg in transcript)
        print(f" Transcript: {len(transcript)} segments, {total_words} words\n")

        print("Chunking transcript by time segments...")
        chunks = chunk_transcript_by_time(transcript, video_info)

        print("Generating embeddings...")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = generate_embeddings(chunk_texts)

        print("Preparing vectors for storage...")
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector = {
                'id': f"{video_id}_chunk_{i}",
                'values': embedding,
                'metadata': {
                    'content_type': 'youtube',
                    'video_id': video_info['video_id'],
                    'video_title': video_info['title'],
                    'video_url': chunk['video_url'],
                    'channel': video_info['channel'],
                    'text': chunk['text'],
                    'timestamp_start': chunk['timestamp_start'],
                    'timestamp_end': chunk['timestamp_end'],
                    'chunk_index': i,
                    'char_count': chunk['char_count']
                }
            }
            vectors.append(vector)
        
        print("Storing vectors in Pinecone...")
        vectors_stored = upsert_vectors(vectors)

        print(f"\n{'='*60}")
        print(f"✓ YouTube Processing Complete!")
        print(f"{'='*60}")
        print(f"   Title: {video_info['title']}")
        print(f"   Duration: {video_info['duration']//60}m {video_info['duration']%60}s")
        print(f"   Chunks created: {len(chunks)}")
        print(f"   Vectors stored: {vectors_stored}")
        print(f"{'='*60}\n")

        return {
            'success': True,
            'video_id': video_id,
            'video_title': video_info['title'],
            'video_url': video_info['url'],
            'duration': video_info['duration'],
            'total_chunks': len(chunks),
            'vectors_stored': vectors_stored,
            'message': f"Successfully processed: {video_info['title']}"
        }
    
    except Exception as e:
        print(f"\n Error processing YouTube video: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'video_id': None,
            'video_title': None,
            'video_url': url,
            'duration': 0,
            'total_chunks': 0,
            'vectors_stored': 0,
            'message': f'Error: {str(e)}'
        }