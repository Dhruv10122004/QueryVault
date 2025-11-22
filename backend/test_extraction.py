"""
Test PDF extraction functions from utils.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import (
    extract_text_from_pdf,
    extract_with_pypdf,
    extract_with_pdfplumber,
    extract_with_ocr,
    chunk_text
)

def test_pdf(pdf_path: str):
    print("\n" + "="*60)
    print(f"Testing PDF: {pdf_path}")
    print("="*60)
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return
    
    with open(pdf_path, "rb") as pdf_file:
        print("\nTesting PyPDF")
        try:
            page_texts, method = extract_with_pypdf(pdf_file)
            if page_texts:
                words = sum(len(t.split()) for t in page_texts.values())
                print(f"Pages: {len(page_texts)}, Words: {words}")
            else:
                print("No text extracted")
        except Exception as e:
            print(f"Error during PyPDF extraction: {e}")


        print("\nTesting pdfplumber...")
        try:
            page_texts, method = extract_with_pdfplumber(pdf_file)
            if page_texts:
                words = sum(len(t.split()) for t in page_texts.values())
                print(f"Pages: {len(page_texts)}, Words: {words}")
            else:
                print(" No text extracted")
        except Exception as e:
            print(f"Error: {e}")


        print("\n" + "-"*70)
        print("Testing OCR (this may take a moment)...")
        print("-"*70)
        try:
            page_texts, method = extract_with_ocr(pdf_file)
            if page_texts:
                total_words = sum(len(t.split()) for t in page_texts.values())
                print(f" Pages: {len(page_texts)}, Words: {total_words}")
                print(f" Sample (first 200 chars):")
                sample = list(page_texts.values())[0][:200]
                print(f"   {sample}...")
            else:
                print(f"No meaningful text extracted")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "-"*70)
        print("4️⃣  Testing Main Extraction (with auto-fallback)...")
        print("-"*70)
        try:
            page_texts = extract_text_from_pdf(pdf_file)
            total_words = sum(len(t.split()) for t in page_texts.values())
            print(f"Final Result: {len(page_texts)} pages, {total_words} words")
            
            # Test chunking
            print("\n" + "-"*70)
            print("Testing Chunking...")
            print("-"*70)
            chunks = chunk_text(page_texts, chunk_size=1000, chunk_overlap=200)
            print(f" Created {len(chunks)} chunks")
            print(f" Chunk sizes: min={min(c['char_count'] for c in chunks)}, max={max(c['char_count'] for c in chunks)}")
            
        except Exception as e:
            print(f" Error: {e}")

    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python test_extraction.py <path-to-pdf>")
        print("\nExample:")
        print("  python test_extraction.py sample.pdf")
        print("  python test_extraction.py /home/user/documents/test.pdf")
        print()
    else:
        test_pdf(sys.argv[1])