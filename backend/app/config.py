"""Configuration settings for the application."""

import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    MAX_PDF_SIZE_MB = 25
    MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024

    MAX_VIDEO_DURATION_HOURS = 3
    MAX_VIDEO_DURATION_SECONDS = MAX_VIDEO_DURATION_HOURS * 3600

    USE_WHISPER_FALLBACK = False

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 2000)) 
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 400)) 

    VIDEO_CHUNK_DURATION = 120
    VIDEO_CHUNK_OVERLAP = 30

    DEFAULT_TOP_K = 5 
    MAX_TOP_K = 10