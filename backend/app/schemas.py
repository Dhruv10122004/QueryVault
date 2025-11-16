# using pydantic : validates data, serialize /convert data, it automatically checks whether incoming data is of correct type or not and produces appropriate error messages, preventing the breakage of API
from pydantic import BaseModel, Field
from typing import List, Optional

class UploadResponse(BaseModel):
    # Response after uploading a PDF
    success: bool
    filename: str
    total_chunks: int
    vectors_stored: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example" : {
                "success": True,
                "filename": "document.pdf",
                "total_chunks": 15,
                "vectors_stored": 15,
                "message": "PDF uploaded and processed successfully."
            }
        }

class QueryRequest(BaseModel):
    # Request to ask a question about uploaded PDFs
    question: str = Field(..., min_length=3, max_length=500)
    top_k: Optional[int] = Field(default=3, ge=1, le=10)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of the document?",
                "top_k": 3
            }
        }

class QueryResponse(BaseModel):
    # Response with answer to user's question
    success: bool
    question: str
    answer: str
    sources: List[dict]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "question": "What is the main topic of the document?",
                "answer": "The main topic of the document is machine learning.",
                "sources": [
                    {
                        "page_number": 2,
                        "text_snippet": "Machine learning is a field of artificial intelligence that focuses on..."
                    },
                    {
                        "page_number": 5,
                        "text_snippet": "Various algorithms are used in machine learning, including supervised and unsupervised learning..."
                    }
                ]
            }
        }

class HealthResponse(BaseModel):
    # Health check response
    status: str
    services: dict