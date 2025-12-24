# QueryVault - RAG-based PDF and YouTube Chatbot

A full-stack application that enables users to upload PDF documents or YouTube videos and interact with them through natural language questions. Built using Retrieval-Augmented Generation (RAG) architecture with vector similarity search.

## Overview

QueryVault processes documents and videos into searchable embeddings, stores them in a vector database, and uses large language models to generate accurate answers with source citations. The application features a split-view interface showing the original content alongside an interactive chat.

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Vector Database**: Pinecone
- **Embeddings**: Cohere (embed-english-v3.0)
- **LLM**: Google Gemini 2.5 Flash
- **PDF Processing**: PyPDF, pdfplumber, Tesseract OCR
- **Video Processing**: youtube-transcript-api, yt-dlp

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **PDF Viewer**: react-pdf
- **Video Player**: YouTube IFrame API
- **HTTP Client**: Axios
- **Routing**: React Router

## Features

### Content Processing
- PDF upload with multi-layer text extraction (digital, layout-aware, OCR fallback)
- YouTube video transcript extraction with automatic translation support
- Smart text chunking with configurable overlap
- Automatic embedding generation and vector storage

### Interactive Chat
- Natural language question answering
- Source citations with relevance scores
- PDF page navigation from chat sources
- YouTube timestamp navigation from chat sources
- Bookmark important responses
- Split-view interface with resizable panels

### User Experience
- Dark/light theme support
- Responsive design
- Real-time upload progress
- Error handling with helpful messages
- Auto-navigation to chat after successful upload

## Project Structure
```
QueryVault/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Application configuration
│   │   ├── db.py                # Pinecone vector database operations
│   │   ├── utils.py             # PDF processing, embeddings, LLM
│   │   ├── ingest.py            # PDF ingestion pipeline
│   │   ├── query.py             # Question answering logic
│   │   ├── youtube.py           # YouTube video processing
│   │   └── schemas.py           # Pydantic data models
│   ├── requirements.txt
│   └── .env                     # API keys (not in repo)
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── chat/            # Chat interface components
    │   │   ├── common/          # Reusable UI components
    │   │   ├── layout/          # Layout components
    │   │   └── viewers/         # PDF and YouTube viewers
    │   ├── contexts/            # React context providers
    │   ├── pages/               # Page components
    │   ├── services/            # API service layer
    │   ├── utils/               # Helper functions
    │   └── App.jsx
    ├── package.json
    └── .env                     # API URL configuration
```

## RAG Pipeline

### Ingestion Flow
1. Content extraction (PDF text or YouTube transcript)
2. Text chunking with overlap for context preservation
3. Embedding generation using Cohere
4. Vector storage in Pinecone with metadata

### Query Flow
1. Question embedding generation
2. Vector similarity search in Pinecone
3. Context retrieval from top-k matches
4. Answer generation using Gemini with retrieved context
5. Response with citations and source information

## PDF Processing

The application uses a three-layer extraction strategy:
1. **PyPDF**: Fast extraction for digital PDFs
2. **pdfplumber**: Enhanced extraction with table support
3. **Tesseract OCR**: Fallback for scanned/image-based PDFs