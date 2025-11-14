"""
Test API keys for Cohere (embeddings), Pinecone (vector DB), and Gemini (LLM).
Run: python test_keys.py
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("API Keys Validation Test")
print("="*60 + "\n")

# ==================== COHERE (Embeddings) ====================
print("Testing Cohere (Embeddings)")
print("-" * 60)

cohere_key = os.getenv("COHERE_API_KEY")
if not cohere_key:
    print(" SKIP: COHERE_API_KEY not found in .env\n")
else:
    try:
        import cohere
        co = cohere.Client(cohere_key)
        
        # Test embedding
        sample_texts = ["This is a test document for PDF chatbot."]
        response = co.embed(
            model="embed-english-v3.0",  # Latest model
            texts=sample_texts,
            input_type="search_document"  # For storing in vector DB
        )
        
        embeddings = response.embeddings[0]
        print(f" Cohere working!")
        print(f"   Model: embed-english-v3.0")
        print(f"   Embedding dimensions: {len(embeddings)}")
        print(f"   Sample values: {embeddings[:3]}")
        
    except Exception as e:
        print(f" Cohere error: {e}")

print()

# ==================== PINECONE (Vector DB) ====================
print(" Testing Pinecone (Vector Database)")
print("-" * 60)

pine_key = os.getenv("PINECONE_API_KEY")
pine_index = os.getenv("PINECONE_INDEX_NAME")

if not pine_key:
    print("SKIP: PINECONE_API_KEY not found in .env\n")
else:
    try:
        from pinecone import Pinecone, ServerlessSpec
        
        pc = Pinecone(api_key=pine_key)
        
        # List indexes
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]
        
        print(f"Pinecone connected!")
        print(f"   Available indexes: {index_names}")
        
        if pine_index:
            if pine_index in index_names:
                # Connect to index
                index = pc.Index(pine_index)
                
                # Get index stats
                stats = index.describe_index_stats()
                
                print(f" Index '{pine_index}' is accessible!")
                print(f"   Total vectors: {stats.total_vector_count}")
                print(f"   Dimension: {stats.dimension}")
                print(f"   Index fullness: {stats.index_fullness}")
                
            else:
                print(f" Index '{pine_index}' not found in your account.")
                print(f"   Create it at: https://app.pinecone.io")
                print(f"   Required settings:")
                print(f"     - Name: {pine_index}")
                print(f"     - Dimensions: 4096 (for Cohere embed-english-v3.0)")
                print(f"     - Metric: cosine")
        
    except Exception as e:
        print(f" Pinecone error: {e}")

print()

# ==================== GEMINI (LLM) ====================
print("  Testing Gemini (Language Model)")
print("-" * 60)

gemini_key = os.getenv("GEMINI_API_KEY")

if not gemini_key:
    print(" SKIP: GEMINI_API_KEY not found in .env")
    print("   Get one at: https://aistudio.google.com/app/apikey\n")
else:
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        
        # List available models (helpful for debugging)
        print(" Available Gemini models:")
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                print(f"   - {model.name}")
        
        print()
        
        # Test generation with correct model name
        model = genai.GenerativeModel('gemini-2.5-flash')  # Latest fast model
        
        prompt = "In one sentence, what is a RAG-based PDF chatbot?"
        response = model.generate_content(prompt)
        
        print(f" Gemini working!")
        print(f"   Model: gemini-2.5-flash")
        print(f"   Test response:")
        print(f"   {response.text}")
        
    except ImportError:
        print(" google-generativeai package not installed")
        print("   Install: pip install google-generativeai")
    except Exception as e:
        print(f" Gemini error: {e}")
        print("\n Common issues:")
        print("   - API key invalid: Get new one at https://aistudio.google.com/app/apikey")
        print("   - Model name wrong: Use 'gemini-1.5-flash' or 'gemini-1.5-pro'")
        print("   - Rate limit: Wait a moment and try again")

print()
print("="*60)
print(" Test Complete!")
print("="*60 + "\n")

# Summary
print(" Summary:")
if cohere_key:
    print("   Cohere: Configured")
else:
    print("   Cohere:  Missing")

if pine_key:
    print("   Pinecone: Configured")
else:
    print("   Pinecone:  Missing")

if gemini_key:
    print("   Gemini: Configured")
else:
    print("   Gemini:  Missing")

print()