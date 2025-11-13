from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="PDF Chatbot API",
    description="Upload PDFs and ask questions",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "PDF Chatbot API is running! Visit /docs for API documentation"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}