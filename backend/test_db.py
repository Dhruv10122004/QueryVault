"""
Test Pinecone database operations from db.py
Run: python test_db.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import (
    get_pinecone_client,
    get_pinecone_index,
    upsert_vectors,
    search_vectors,
    delete_all_vectors,
    get_index_stats
)


def test_pinecone():
    """Test all Pinecone operations"""
    
    print("\n" + "="*60)
    print("Testing Pinecone Database Operations")
    print("="*60)
    
    # Test 1: Client connection
    print("\n Testing Pinecone Client Connection...")
    try:
        client = get_pinecone_client()
        print(" Client connected successfully")
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Test 2: Index connection
    print("\nTesting Index Connection...")
    try:
        index = get_pinecone_index()
        print(" Index connected successfully")
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Test 3: Get index stats (before inserting)
    print("\nTesting Index Stats (Before)...")
    try:
        stats = get_index_stats()
        print(f" Total vectors: {stats['total_vectors']}")
        print(f" Dimension: {stats['dimension']}")
        print(f" Index fullness: {stats['index_fullness']}")
    except Exception as e:
        print(f"  Error: {e}")
        return
    
    # Test 4: Upsert test vectors
    print("\nTesting Vector Upsert...")
    try:
        # Create dummy vectors (1024 dimensions for Cohere)
        import random
        test_vectors = []
        
        for i in range(5):
            test_vectors.append({
                'id': f'test_vector_{i}',
                'values': [random.random() for _ in range(1024)],
                'metadata': {
                    'text': f'This is test chunk {i}',
                    'filename': 'test.pdf',
                    'page': 1,
                    'chunk_index': i
                }
            })
        
        count = upsert_vectors(test_vectors)
        print(f"  Upserted {count} test vectors")
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Test 5: Get index stats (after inserting)
    print("\n Testing Index Stats (After Upsert)...")
    try:
        stats = get_index_stats()
        print(f"   Total vectors: {stats['total_vectors']}")
        print(f"   Dimension: {stats['dimension']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 6: Search vectors
    print("\nTesting Vector Search...")
    try:
        # Create a random query vector
        query_vector = [random.random() for _ in range(1024)]
        
        results = search_vectors(query_vector, top_k=3)
        print(f" Found {len(results)} matches")
        
        for i, match in enumerate(results, 1):
            print(f"\n   Match {i}:")
            print(f"      ID: {match['id']}")
            print(f"      Score: {match['score']:.4f}")
            print(f"      Text: {match['metadata'].get('text', 'N/A')}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test 7: Clean up (delete test vectors)
    print("\nTesting Vector Deletion...")
    try:
        print("  This will delete ALL vectors from the index!")
        user_input = input("   Continue? (yes/no): ")
        
        if user_input.lower() == 'yes':
            delete_all_vectors()
            print("  All vectors deleted")
            
            # Verify deletion
            stats = get_index_stats()
            print(f" Remaining vectors: {stats['total_vectors']}")
        else:
            print("  Skipped deletion")
    except Exception as e:
        print(f" Error: {e}")
    
    print("\n" + "="*60)
    print("All Tests Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_pinecone()