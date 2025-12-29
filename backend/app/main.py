# Right now all functions are synchronous. For scaling purposes in future we can make them async.
# Async functions would be useful while scaling because we can handle multiple requests concurrently.
import uuid
from .conversation import ConversationManager

"""
FastAPI application entry point.
Defines all API endpoints and handles HTTP requests.                       
"""

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .schemas import UploadResponse, QueryRequest, QueryResponse, HealthResponse, YouTubeUploadResponse, YouTubeUploadRequest, ConversationClearRequest                                                                   
from .ingest import process_pdf
from .query import answer_question
from .db import get_index_stats, delete_all_vectors
           
load_dotenv()

app = FastAPI(
    title="PDF Chatbot API",
    description="RAG-based PDF chatbot using Cohere, Pinecone, and Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # right now, allowing every origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "PDF Chatbot API is running! ",
        "docs": "Visit /docs for interactive API documentation",
        "endpoints": {
            "upload_pdf": "POST /upload - Upload a PDF",
            "upload_youtube": "POST /upload/youtube - Process YouTube video",
            "query": "POST /query - Ask questions",
            "health": "GET /health - Service health check"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Verifies all services are accessible.
    """
    try:
        stats = get_index_stats()

        services = {
            "cohere": bool(os.getenv("COHERE_API_KEY")),
            "pinecone": bool(os.getenv("PINECONE_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),  
            "pinecone_vectors": stats['total_vectors']                         
        }

        all_healthy = all([
            services['cohere'],
            services['pinecone'],
            services['gemini']
        ])

        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": services
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "services": {"error": str(e)}
        }
    
@app.post("/upload", response_model=UploadResponse, tags=["PDF Processing"])
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    
    Process:
    1. Validates file is a PDF
    2. Extracts text from all pages
    3. Splits text into overlapping chunks
    4. Generates embeddings using Cohere
    5. Stores vectors in Pinecone
    
    Returns processing summary with chunk count.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed. Please upload a .pdf file"
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = 25 * 1024 * 1024  # 10 MB limit
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum allowed size is 10MB, got {file_size / 1024 / 1024:.1f}MB"
        )
    
    try:
        delete_all_vectors()
    except Exception as e:
        print(f"Warning: Could not clear databse: {e}")
    
    result = process_pdf(file)

    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=result['message']
        )
    
    return result

@app.post("/query", response_model=QueryResponse, tags=["Question Answering"])
async def query_pdf(request: QueryRequest):
    """
    Ask a question about uploaded PDFs.
    
    Uses RAG (Retrieval-Augmented Generation):
    1. Converts question to embedding
    2. Searches Pinecone for similar chunks
    3. Generates answer using Gemini with context
    
    Returns answer with source citations.
    """

    session_id = request.session_id or str(uuid.uuid4())
    
    result = answer_question(
        question=request.question,
        top_k=request.top_k,
        session_id=session_id
    )

    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=result.get('message', 'An error occurred while processing your question')
        )
    result['session_id'] = session_id
    return result

@app.delete("/clear", tags=["Maintenance"])
async def clear_database():
    """
    Clear all vectors from Pinecone database.
    
    Warning: This will delete all uploaded PDF data!
    """
    try:
        from .db import delete_all_vectors
        delete_all_vectors()
        return {
            "success": True,
            "message": "All vectors deleted from Pinecone"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing database: {str(e)}"
        )
    
@app.post("/upload/youtube", response_model=YouTubeUploadResponse, tags=["PDF Processing"])
async def upload_youtube(request: YouTubeUploadRequest):
    from .youtube import process_youtube
    try:
        delete_all_vectors()
    except Exception as e:
        print(f"Warning: Could not clear databse: {e}")

    result = process_youtube(request.url)
    if not result['success']:
        raise HTTPException(
            status_code=500,
            detail=result['message']
        )
    return result

@app.post("/conversation/clear", tags=["Conversation"])
async def clear_conversation(request: ConversationClearRequest):
    """Clear conversation history for a session"""
    try:
        ConversationManager.clear_conversation(request.session_id)
        return {
            "success": True,
            "message": "Conversation cleared",
            "session_id": request.session_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/conversation/{session_id}", tags=["Conversation"])
async def get_conversation(session_id: str):
    """Get conversation history"""
    try:
        context = ConversationManager.get_conversation_context(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "context": context
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)