"""
Test PDF ingestion pipeline
Run: python test_ingest.py
"""

import sys
import os
import asyncio
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import UploadFile
from app.ingest import process_pdf


async def test_ingestion():
    """Test the complete ingestion pipeline"""
    
    print("\n" + "="*60)
    print("Testing PDF Ingestion Pipeline")
    print("="*60)
    
    # Load a test PDF
    pdf_path = "test_pdfs/Resume.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Test PDF not found: {pdf_path}")
        print("   Please add a PDF to test_pdfs/ folder")
        return
    
    # Read PDF into bytes
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    # Create FastAPI UploadFile object
    file = UploadFile(
        filename="Resume.pdf",
        file=BytesIO(pdf_bytes)
    )
    
    # Process the PDF
    print("\nStarting processing...\n")
    result = process_pdf(file)
    
    # Check results
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    if result['success']:
        print("Status: SUCCESS")
        print(f"Filename: {result['filename']}")
        print(f"Chunks created: {result['total_chunks']}")
        print(f"Vectors stored: {result['vectors_stored']}")
        print(f"Message: {result['message']}")
    else:
        print("Status: FAILED")
        print(f"Message: {result['message']}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run async function
    asyncio.run(test_ingestion())