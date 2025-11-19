"""Utility functions for pdf processing, text chunking, and embeddings.
Core building blocks used by ingest.py and query.py"""

import os
import re
from typing import List, Dict, BinaryIO, Tuple
from pypdf import PdfReader
import cohere
import google.generativeai as genai
from dotenv import load_dotenv
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes

load_dotenv()

_cohere_client = None
_gemini_model = None

def get_cohere_client():
    """Get or create cohere client"""
    global _cohere_client

    if _cohere_client is None:
        apikey = os.getenv("COHERE_API_KEY")
        if not apikey:
            raise ValueError("COHERE_API_KEY not found in environment")
        
        _cohere_client = cohere.Client(apikey)
        print("Cohere client initialized")
    return _cohere_client

def get_gemini_model():
    global _gemini_model

    if _gemini_model is None:
        apikey = os.getenv("GEMINI_API_KEY")
        if not apikey:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=apikey)
        _gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        print("Gemini model initialized")
    return _gemini_model

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text) # Replace multiple whitespace with single space
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\"\'\/]', '', text) # Remove special characters except common punctuation
    return text.strip()

def is_text_meaningful(text: str, min_words: int = 50) -> bool:
    if not text:
        return False
    words = text.split()

    if len(words) < min_words:
        return False

    short_words = [w for w in words if len(w) <= 2]
    if len(short_words) / len(words) > 0.7: # More than 70% short words
        return False
    return True        

def extract_with_pypdf(pdf_file: BinaryIO) -> Tuple[Dict[int, str], str]:
    """Extract text using pypdf (fast, works for digital PDFs).
    returns a dict of page number to text and method used string"""

    try:
        pdf_file.seek(0)
        reader = PdfReader(pdf_file)
        page_texts = {}

        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            text = clean_text(text)

            if text:
                page_texts[page_num] = text
        
        total_text = " ".join(page_texts.values())

        if is_text_meaningful(total_text):
            print(f"PyPDF: Extracted {len(page_texts)} pages, {len(total_text.split())} words.")
            return page_texts, "pypdf"
        else:
            print(f"PyPDF: Insufficient text extracted ({len(total_text.split())} words).")
            return {}, "pypdf"
    
    except Exception as e:
        print(f"PyPDF extraction error: {e}")
        return {}, "pypdf"
    
def extract_with_pdfplumber(pdf_file: BinaryIO) -> Tuple[Dict[int, str], str]:
    """Layer 2:  
        Extract text using pdfplumber (better layout/ tables)
        Returns:
        (page_texts dict, method_used string)
        """
    try:
        pdf_file.seek(0)
        page_texts = {}
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()

                tables = page.extract_tables()
                if tables:
                    for table in tables:
                       table_text = "\n".join([" | ".join([str(cell) for cell in row if cell]) for row in table])
                       text = text + "\n" + table_text if text else table_text
                 
                text = clean_text(text)
        total_text = " ".join(page_texts.values())

        if is_text_meaningful(total_text):
            print(f"pdfplumber: Extracted {len(page_texts)} pages, {len(total_text.split())} words")
            return page_texts, "pdfplumber"
        else:
            print(f"pdfplumber: Insufficient text extracted ({len(total_text.split())} words)")
            return {}, "pdfplumber_failed"
            
    except Exception as e:
        print("pdfplumber extraction error: {e}")
        return {}, "pdfplumber_error"
    
def extract_with_ocr(pdf_file: BinaryIO) -> Tuple[Dict[int, str], str]:
    """
    Layer 3: Extract text using ocr (for scanned pdfs / images)
    returns:
    (page_texts dict, method_used string)
    """
    try:
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()

        print("Converting PDF to images for OCR (this may take a moment)...")

        #convert pdf pages to images
        images = convert_from_bytes(
            pdf_bytes,
            dpi=300,
            fmt='jpeg'
        )
        page_texts = {}

        for page_num, image in enumerate(images, start=1):
            print(f"Ocr processing page {page_num}/{len(images)}")
            #perform ocr
            text = pytesseract.image_to_string(image, lang='eng')
            text = clean_text(text)

            if text:
                page_texts[page_num] = text
        
        total_text = " ".join(page_texts.values())

        if is_text_meaningful(total_text):
            print(f"OCR: Extracted {len(page_texts)} pages, {len(total_text.split())} words.")
            return page_texts, "ocr"
        else:
            print(f"OCR: Insufficient text extracted ({len(total_text.split())} words).")
            return {}, "ocr_failed"
    
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return {}, "ocr_error"
    
def extract_text_from_pdf(pdf_file: BinaryIO) -> Dict[int, str]:
    """
    Multi-layered PDF text extraction:
    1. Try pypdf
    2. If insufficient, try pdfplumber
    3. If still insufficient, try OCR
    4. If all fail, raise error with helpful message

    Args:
        pdf_file: Binary file object (from FastAPI's UploadFile)
    
    Returns:
        Dictionary mapping page number to text content
        {1: "page 1 text...", 2: "page 2 text...", ...}
    
    Raises:
        ValueError: If no text could be extracted by any method
    """
    print("\n" + "="*60)
    print("Starting PDF Text Extraction")
    print("="*60)

    extraction_methods = [
        ("PyPDF (Digital PDFs)", extract_with_pypdf),
        ("pdfplumber (Layout/Tables)", extract_with_pdfplumber),
        ("OCR (Scanned PDFs)", extract_with_ocr)
    ]

    for method_name, extract_func in extraction_methods:
        print(f"\n🔍 Trying {method_name}...")
        page_texts, method_used = extract_func(pdf_file)
        
        if page_texts:
            total_words = sum(len(text.split()) for text in page_texts.values())
            print(f"\n{'='*60}")
            print(f"✅ Success with {method_name}")
            print(f"{'='*60}")
            print(f"   Pages extracted: {len(page_texts)}")
            print(f"   Total words: {total_words}")
            print(f"   Method used: {method_used}")
            print(f"{'='*60}\n")
            return page_texts
    

    error_msg = """
Failed to extract meaningful text from PDF using all available methods:
1. PyPDF (for digital/text-based PDFs)
2. pdfplumber (for PDFs with complex layouts/tables)
3. OCR with Tesseract (for scanned/image-based PDFs)

Possible reasons:
- PDF is password protected
- PDF contains only images with no text
- OCR dependencies not installed (Tesseract)
- PDF is corrupted

Please try:
- A different PDF file
- Ensure Tesseract is installed: sudo apt-get install tesseract-ocr
- Check if PDF can be opened normally in a PDF reader
"""
    
    print(f"\n{'='*60}")
    print("All extraction methods failed")
    print(f"{'='*60}\n")
    
    raise ValueError(error_msg.strip())
