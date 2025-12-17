"""
YouTube video processing module -> extracts transcripts and processes them like PDFs.
"""

import os 
import re
import tempfile
from typing import Dict, List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import yt_dlp
import whisper
from .config import Config
from .utils import generate_embeddings
from .db import upsert_vectors

_whisper_model = None

def get_whisper_model():
    """Lazy loading whisper model."""
    global _whisper_model
    if _whisper_model is None:
        print("Loading Whisper model... This may take a moment on first run.")
        _whisper_model = whisper.load_model("base")
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
                'channel': info.get('duration', 'Unknown'),
                'duration': info.get('duration', 0),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
    except Exception as e:
        raise ValueError(f"Error fetching video info: {str(e)}")

def fetch_existing_transript(videoid: str) -> Optional[List[Dict]]:
    """for fetching transcripts"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(videoid)
        # trying to find english transcript first
        try:
            transcript = transcript_list.find_transcript(['en'])
            print(f"Found english transcript ({len(transcript.fetch())} segments)")
            return transcript.fetch()
        except:
            pass

        # get any available transcript and translate to english
        try:
            transcript = transcript_list.find_transcript(['hi', 'es', 'fr', 'de', 'ja', 'ko', 'zh'])
            original_lang = transcript.language_code
            print(f"No english transcript found. Found {original_lang} transcript")
            print(f"Translating {original_lang} --> English..")

            #Translating to english
            translated = transcript.translate('en')
            result = translated.fetch()

            print(f"translated {len((result))} segments to english")
            return result
        except:
            print(f"Translation failed, using original {original_lang} transcript")
            return transcript.fetch()
        
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        print(f"No transcripts available: {e}")
        return None
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def download_audio(videoid: str, output_path: str) -> str:
    """download audio from youtube video"""
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
            ydl.download([f"https://www.youtube.com/watch?v={videoid}"])

        return output_path + ".mp3"
    except Exception as e:
        raise ValueError(f"failed to download audio: {str(e)}")

def transcribe_with_whisper(videoid: str) -> List[Dict]:
    print("generating transcript from the audio")
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio")

    try:
        print("Downloading audio...")
        audio_file = download_audio(videoid, audio_path)

        print("transcribing audio")
        model = get_whisper_model()
        result = model.transcribe(audio_file, language='en', verbose=False)

        transcript = []
        for segment in result['segments']:
            transcript.append({
                'text': segment['text'].strip(),
                'start': segment['start'],
                'duration': segment['end'] - segment['start']
            })

        print(f"transcription complete ({len(transcript)}) segments")
        return transcript
    finally:
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            os.rmdir(temp_dir)
        except Exception as e:
            pass

def get_transcript(videoid: str) -> List[Dict]:
    transcript = fetch_existing_transript(videoid)
    if transcript:
        return transcript
    
    if Config.USE_WHISPER_FALLBACK:
        print("no captions available - will generate transcript locally")
        return transcribe_with_whisper(videoid)
    else:
        raise ValueError("This video has no captions/transcript available\n" \
        "Enable USE_WHISPER_FALLBACK in config to generate transcript using Whisper model.")
    
def chunk_transcript_by_time(
    transcript: List[Dict],
    video_info: Dict,
    chunk_duration: int = Config.VIDEO_CHUNK_DURATION,
    overlap: int = Config.VIDEO_CHUNK_OVERLAP
) -> List[Dict]:
    chunks = []
    current_time = 0
    video_duration = video_info['duration']

    while current_time < video_duration:
        chunk_end = min(current_time + chunk_duration, video_duration)
        chunk_texts = []
        for segment in transcript:
            segment_start = segment['start']
            segment_end = segment['start'] + segment['duration']

            if segment_start < chunk_end and segment_end > current_time:
                chunk_texts.append(segment['text'])
        
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
    print(f"Created {len(chunks)} time-based chunks from transcript")
    return chunks

def process_youtube(url: str) -> Dict:
    try:
        print(f"\n{'='*60}")
        print(f"Processing YouTube Video")
        print(f"{'='*60}\n")

        print("extracting video id")
        videoid = extract_video_id(url)
        print(f"video id: {videoid}")

        print("fetching video info")
        videoinfo = get_video_info(videoid)
        print(f" Title: {videoinfo['title']}")
        print(f" Channel: {videoinfo['channel']}")
        print(f" Duration: {videoinfo['duration']//60}m {videoinfo['duration']%60}s\n")

        if videoinfo['duration'] > Config.MAX_VIDEO_DURATION_SECONDS:
            raise ValueError(f"video too long")
        
        print("getting transcript")
        transcript = get_transcript(videoid)
        totalwords = sum(len(seg['text'].split()) for seg in transcript)
        print(f"transcript: {len(transcript)} segments, -{totalwords} words\n")

        print("Chunking transcript by time segments...")
        chunks = chunk_transcript_by_time(transcript, videoinfo)

        print("Generating embeddings...\n")
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = generate_embeddings(chunk_texts)

        print("preparing vectors for storage...")
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector = {
                'id': f"{videoid}_chunk_{i}",
                'values': embedding,
                'metadata': {
                    'content_type': 'youtube',
                    'video_id': videoinfo['video_id'],
                    'video_title': videoinfo['title'],
                    'video_url': chunk['video_url'],
                    'channel': videoinfo['channel'],
                    'text': chunk['text'],
                    'timestamp_start': chunk['timestamp_start'],
                    'timestamp_end': chunk['timestamp_end'],
                    'chunk_index': i,
                    'char_count': chunk['char_count']
                }
            }
            vectors.append(vector)
        
        print("storing vectors in pinecone...")
        vectors_stored = upsert_vectors(vectors)

        print(f"\n{'='*60}")
        print(f"YouTube Processing Complete!")
        print(f"{'='*60}")
        print(f"   Title: {videoinfo['title']}")
        print(f"   Duration: {videoinfo['duration']//60}m {videoinfo['duration']%60}s")
        print(f"   Chunks created: {len(chunks)}")
        print(f"   Vectors stored: {vectors_stored}")
        print(f"{'='*60}\n")

        return {
            'success': True,
            'video_id': videoid,
            'video_title': videoinfo['title'],
            'video_url': videoinfo['url'],
            'duration': videoinfo['duration'],
            'total_chunks': len(chunks),
            'vectors_stored': vectors_stored,
            'message': f"Successfully processed: {videoinfo['title']}"
        }
    
    except Exception as e:
        print(f"Error processing YouTube video: {e}")
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