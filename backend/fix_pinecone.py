from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "pdf-chatbot-index"

# Delete old index
print("  Deleting old index...")
pc.delete_index(index_name)

import time
time.sleep(5)  # Wait for deletion

# Create new index with CORRECT dimensions
print(" Creating new index with 1024 dimensions...")
pc.create_index(
    name=index_name,
    dimension=1024,  # Match Cohere output
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

print(" Done! Index created with 1024 dimensions")