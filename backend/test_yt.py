"""
Test YouTube video processing pipeline
Run: python test_youtube.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.youtube import process_youtube
from app.query import answer_question
from app.db import get_index_stats, delete_all_vectors


def setup_test_data():
    """Process a test YouTube video if no vectors exist"""
    
    print("\n" + "="*60)
    print("Setup: Checking Test Data")
    print("="*60)
    
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
    
    test_url = input("\n   Enter YouTube URL to test: ")
    
    if not test_url.strip():
        print("   No URL provided")
        return False
    
    print(f"\n   Processing YouTube video...")
    
    result = process_youtube(test_url)
    
    if result['success']:
        print(f"   Processed successfully")
        print(f"   Title: {result['video_title']}")
        print(f"   Chunks: {result['total_chunks']}")
        print(f"   Vectors: {result['vectors_stored']}")
        return True
    else:
        print(f"   Processing failed: {result['message']}")
        return False


def test_youtube_processing():
    """Test YouTube video processing"""
    
    print("\n" + "="*60)
    print("Testing YouTube Processing Pipeline")
    print("="*60)
    
    test_url = input("\nEnter YouTube URL: ")
    
    if not test_url.strip():
        print("No URL provided")
        return
    
    print("\nProcessing video...\n")
    
    result = process_youtube(test_url)
    
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    if result['success']:
        print("Status: SUCCESS")
        print(f"Video ID: {result['video_id']}")
        print(f"Title: {result['video_title']}")
        print(f"Duration: {result['duration']//60}m {result['duration']%60}s")
        print(f"Chunks created: {result['total_chunks']}")
        print(f"Vectors stored: {result['vectors_stored']}")
        print(f"Message: {result['message']}")
    else:
        print("Status: FAILED")
        print(f"Message: {result['message']}")
    
    print("="*60 + "\n")


def test_youtube_query():
    """Test question answering on YouTube content"""
    
    print("\n" + "="*60)
    print("Testing YouTube Question Answering")
    print("="*60)
    
    if not setup_test_data():
        return
    
    test_questions = [
        "What is the main topic of this video?",
        "Summarize the key points discussed",
        "What are the important takeaways?"
    ]
    
    print("\n" + "="*60)
    print("Testing Questions")
    print("="*60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*60}")
        print(f"Question {i}/{len(test_questions)}: {question}")
        print(f"{'─'*60}")
        
        try:
            result = answer_question(question, top_k=3)
            
            if result['success']:
                print(f"\nAnswer:")
                print(f"   {result['answer'][:200]}...")
                
                print(f"\nSources ({len(result['sources'])} found):")
                for j, source in enumerate(result['sources'], 1):
                    if source.get('type') == 'youtube':
                        print(f"\n   Source {j}:")
                        print(f"      Video: {source['video_title']}")
                        print(f"      Timestamp: {source['timestamp_formatted']}")
                        print(f"      URL: {source['video_url']}")
                        print(f"      Score: {source['score']}")
                        print(f"      Text: {source['text'][:80]}...")
            else:
                print(f"\nFailed:")
                print(f"   {result['answer']}")
        
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("All Tests Complete!")
    print("="*60 + "\n")


def test_interactive():
    """Interactive test mode"""
    
    if not setup_test_data():
        return
    
    question = input("\nEnter your question: ")
    
    if not question.strip():
        print("No question provided")
        return
    
    print("\nProcessing question...\n")
    
    result = answer_question(question, top_k=3)
    
    print("\n" + "="*60)
    print("Result")
    print("="*60)
    
    if result['success']:
        print(f"\nAnswer:\n{result['answer']}")
        
        if result['sources']:
            print(f"\nSources:")
            for i, source in enumerate(result['sources'], 1):
                if source.get('type') == 'youtube':
                    print(f"\n   {i}. {source['video_title']}")
                    print(f"      Time: {source['timestamp_formatted']}")
                    print(f"      Score: {source['score']}")
                    print(f"      URL: {source['video_url']}")
                    print(f"      Text: {source['text']}")
    else:
        print(f"\nError: {result['answer']}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--process":
            test_youtube_processing()
        elif sys.argv[1] == "--query":
            test_youtube_query()
        elif sys.argv[1] == "--interactive":
            test_interactive()
        else:
            print("\nUsage:")
            print("  python test_youtube.py --process      # Test video processing")
            print("  python test_youtube.py --query        # Test Q&A with preset questions")
            print("  python test_youtube.py --interactive  # Interactive Q&A mode")
    else:
        print("\nYouTube Pipeline Test")
        print("="*60)
        print("\nOptions:")
        print("  1. Test video processing")
        print("  2. Test question answering")
        print("  3. Interactive mode")
        
        choice = input("\nSelect option (1-3): ")
        
        if choice == "1":
            test_youtube_processing()
        elif choice == "2":
            test_youtube_query()
        elif choice == "3":
            test_interactive()
        else:
            print("Invalid option")