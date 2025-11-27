"""
Test question answering pipeline with automatic PDF upload
Run: python test_query.py
"""

import sys
import os
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import UploadFile
from app.query import answer_question
from app.ingest import process_pdf
from app.db import get_index_stats, delete_all_vectors


def setup_test_data():
    """Upload a test PDF if no vectors exist"""
    
    print("\n" + "="*60)
    print(" Setup: Checking Test Data")
    print("="*60)
    
    # Check if vectors exist
    stats = get_index_stats()
    
    if stats['total_vectors'] > 0:
        print(f"   Found {stats['total_vectors']} existing vectors")
        
        user_input = input("\n   Use existing vectors? (yes/no): ")
        if user_input.lower() == 'yes':
            print("   Using existing data")
            return True
        else:
            print("   Clearing existing vectors...")
            delete_all_vectors()
    
    # Upload test PDF
    pdf_path = "test_pdfs/Resume.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"\n Test PDF not found: {pdf_path}")
        print("  Please add a PDF to test_pdfs/ folder")
        return False
    
    print(f"\n  Uploading test PDF: {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    file = UploadFile(
        filename="Resume.pdf",
        file=BytesIO(pdf_bytes)
    )
    
    result = process_pdf(file)
    
    if result['success']:
        print(f"   Uploaded successfully")
        print(f"   Chunks: {result['total_chunks']}")
        print(f"   Vectors: {result['vectors_stored']}")
        return True
    else:
        print(f"  Upload failed: {result['message']}")
        return False


def test_query():
    """Test the complete query/answer pipeline"""
    
    print("\n" + "="*60)
    print(" Testing Question Answering Pipeline")
    print("="*60)
    
    # Setup test data
    if not setup_test_data():
        return
    
    # Test questions
    test_questions = [
        "What is this document about?",
        "Who is Dhruv Khanna?",
        "What education does the person have?",
        "What skills are mentioned?",
        "Where is the person located?"
    ]
    
    print("\n" + "="*60)
    print(" Testing Questions")
    print("="*60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*60}")
        print(f"Question {i}/{len(test_questions)}: {question}")
        print(f"{'─'*60}")
        
        try:
            result = answer_question(question, top_k=3)
            
            if result['success']:
                print(f"\n Answer:")
                print(f"   {result['answer'][:200]}...")  # Truncate long answers
                
                print(f"\nSources ({len(result['sources'])} found):")
                for j, source in enumerate(result['sources'], 1):
                    print(f"\n   Source {j}:")
                    print(f"      File: {source['filename']}")
                    print(f"      Page: {source['page']}")
                    print(f"      Score: {source['score']}")
                    print(f"      Text: {source['text'][:80]}...")
            else:
                print(f"\n Failed:")
                print(f"   {result['answer']}")
        
        except Exception as e:
            print(f"\n Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(" All Tests Complete!")
    print("="*60 + "\n")


def test_single_question():
    """Quick test with a single question"""
    
    # Setup test data
    if not setup_test_data():
        return
    
    question = input("\n Enter your question: ")
    
    if not question.strip():
        print(" No question provided")
        return
    
    print("\n🔍 Processing question...\n")
    
    result = answer_question(question, top_k=3)
    
    print("\n" + "="*60)
    print(" Result")
    print("="*60)
    
    if result['success']:
        print(f"\n Answer:\n{result['answer']}")
        
        if result['sources']:
            print(f"\n Sources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"\n   {i}. Page {source['page']} (score: {source['score']})")
                print(f"      {source['text']}")
    else:
        print(f"\n Error: {result['answer']}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Interactive mode
        test_single_question()
    else:
        # Auto mode
        test_query()