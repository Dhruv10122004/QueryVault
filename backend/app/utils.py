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
        print(f"\n Trying {method_name}...")
        page_texts, method_used = extract_func(pdf_file)
        
        if page_texts:
            total_words = sum(len(text.split()) for text in page_texts.values())
            print(f"\n{'='*60}")
            print(f"Success with {method_name}")
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

def chunk_text(page_texts: Dict[int, str], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """
    Split text into overlapping chunks for better context preservation.
    
    Args:
        page_texts: Dict of {page_num: text}
        chunk_size: Max characters per chunk
        chunk_overlap: Characters to overlap between chunks
    
    Returns:
        List of chunks with metadata:
        [
            {
                'text': 'chunk text...',
                'page': 1,
                'chunk_index': 0,
                'char_count': 950
            },
            ...
        ]
    """
    chunks = []
    chunk_index = 0

    for page_num, page_text in page_texts.items():
        sentences = re.split(r'(?<=[.!?])\s+', page_text)
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'page': page_num,
                    'chunk_index': chunk_index,
                    'char_count': len(current_chunk.strip())
                })

                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence
        
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'page': page_num,
                'chunk_index': chunk_index,
                'char_count': len(current_chunk.strip())
            })
            chunk_index += 1
    print(f"Created {len(chunks)} chunks from {len(page_texts)}")
    return chunks

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embedding using Cohere
    Args: 
        texts: List of strings to embed
    Returns:
        List of embeddings (list of floats)
    """

    try:
        co = get_cohere_client()
        batch_size = 90 # cohere has a limit of 100 per request, using 90 to be safe
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i: i+batch_size]
            response = co.embed(
                model ="embed-english-v3.0",
                texts = batch,
                input_type="search_document"
            )

            embeddings.extend(response.embeddings)
            print(f"Total embeddings generated: {len(embeddings)}/{len(texts)}")
        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        raise

def generate_query_embedding(question: str) -> List[float]:
    """
    Generate embedding for a query using Cohere
    Args:
        question: Query string
    Returns:
        Embedding (list of floats)
    """

    try:
        co = get_cohere_client()
        response = co.embed(
            model ="embed-english-v3.0",
            texts = [question],
            input_type="search_query"
        )

        return response.embeddings[0]
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        raise

def generate_answer(question: str, context_chunks: List[Dict]) -> str:
    """
    Generate answer using Gemini based on retrieved context.
    
    Args:
        question: User's question
        context_chunks: List of retrieved chunks with 'text' and 'metadata'
    
    Returns:
        Generated answer string
    """
    try:
        model = get_gemini_model()

        # Detect content type from chunks
        has_youtube = any(chunk.get('metadata', {}).get('content_type') == 'youtube' 
                         for chunk in context_chunks)
        has_pdf = any(chunk.get('metadata', {}).get('content_type') != 'youtube' 
                     for chunk in context_chunks)
        
        # Determine source description
        if has_youtube and has_pdf:
            source_type = "PDF documents and YouTube videos"
        elif has_youtube:
            source_type = "YouTube video transcripts"
        else:
            source_type = "PDF documents"

        # Format context based on content type
        context_parts = []
        for chunk in context_chunks:
            metadata = chunk.get('metadata', {})
            content_type = metadata.get('content_type', 'pdf')
            
            if content_type == 'youtube':
                video_title = metadata.get('video_title', 'Unknown Video')
                timestamp = metadata.get('timestamp_start', 0)
                time_formatted = f"{int(timestamp) // 60}:{int(timestamp) % 60:02d}"
                context_parts.append(
                    f"Source: YouTube - '{video_title}' at {time_formatted}:\n{chunk['text']}"
                )
            else:
                page = chunk.get('page', 'N/A')
                chunk_idx = chunk.get('chunk_index', 0)
                context_parts.append(
                    f"Source: PDF - Page {page}, Chunk {chunk_idx}:\n{chunk['text']}"
                )
        
        context = "\n\n".join(context_parts)

        # Create adaptive prompt
        prompt = f"""You are a helpful assistant that answers questions based on provided content.

Context from {source_type}:
{context}

Question: {question}

Instructions:
- Answer the question based ONLY on the context provided above
- If the answer is not in the context, say "I couldn't find that information in the provided content."
- Be concise and specific
- When referencing sources, mention whether it's from a PDF (with page number) or YouTube video (with timestamp)
- Synthesize information from multiple sources if relevant

Answer:"""
        
        # Generate response
        response = model.generate_content(prompt)
        answer = response.text
        
        print(f"Generated answer ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"Error generating answer: {e}")
        return f"Sorry, I encountered an error generating the answer: {str(e)}"