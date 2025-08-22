import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI, Body, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import httpx
import shutil

from .rag import retrieve, get_collection_info, clear_collection
from .ingest import ingest_folder, ingest_single_file, get_ingestion_stats
from .settings_store import (
    load_settings, save_settings, update_settings, 
    reset_settings, export_settings, import_settings
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")  # "openai" or "ollama"
GEN_MODEL = os.getenv("GEN_MODEL", "gpt-4o-mini")  # or e.g. "llama3"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="A customizable RAG chatbot API for embedding in websites",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the widget
app.mount("/widget", StaticFiles(directory="./widget"), name="widget")

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("./uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User's question")
    session_id: Optional[str] = Field(None, description="Optional session identifier")

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    context_used: int
    response_time: float

class SettingsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    subtitle: Optional[str] = Field(None, max_length=200)
    logo: Optional[str] = Field(None, description="Logo URL")
    accent: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    footer: Optional[str] = Field(None, max_length=100)
    suggested: Optional[List[str]] = Field(None, max_items=4)

    secondaryColor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Secondary color")
    backgroundColor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Background color")
    textColor: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Text color")
    # Chat settings
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature for response creativity (0.0-2.0)")
    max_tokens: Optional[int] = Field(None, ge=50, le=1000, description="Maximum response length in tokens")
    max_context_length: Optional[int] = Field(None, ge=1000, le=10000, description="Maximum context length in tokens")
    # Chat icon
    chatIcon: Optional[str] = Field(None, description="Chat icon image URL")
    chatIconText: Optional[str] = Field(None, max_length=100, description="Chat icon text")

class IngestRequest(BaseModel):
    input_path: str = Field(..., description="Path to file or directory")
    source_tag: str = Field("local", description="Source identifier")
    chunk_size: int = Field(600, ge=100, le=2000, description="Tokens per chunk")
    overlap: int = Field(80, ge=0, le=500, description="Overlapping tokens")

# LLM calling functions
async def call_openai(prompt: str, temperature: float = 0.2, max_tokens: int = 140) -> str:
    """Call OpenAI API for text generation."""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": GEN_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "You are a friendly Vision Flows Agency teammate.\n\nRULES\n- Use ONLY the provided Context. If missing, say what's missing and ask 1 targeted question.\n- Keep answers short: 60–100 words total. Max 4 bullets. No intro phrases or summaries.\n- Format lists with \"• \"; one idea per line; no tables unless asked.\n- If asked about pricing/timeline/scope: ask 1 scoping question, then give a clear next step (book call, custom quote, or starter package).\n- Do not repeat yourself or restate the question.\n- End every reply with the token: <END>\n\nEXAMPLES:\nUser: Do you build Shopify stores? What's the cost?\nAssistant:\n• Yes—Shopify setup, payments, products, and basic design\n• Typical range: $1,500–$3,500; varies by catalog size and integrations\n• Share product count + must-have apps, and I'll confirm a package or custom quote\n<END>\n\nUser: Can you add a website chatbot?\nAssistant:\n• We install a site + Instagram chatbot for FAQs, leads, and simple booking\n• Setup: $500–$1,500; ongoing from $150–$300/mo based on features\n• Do you want lead qualification, calendar booking, or handoff to a human?\n<END>\n\nCONTEXT\n{{context}}"
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "frequency_penalty": 0.4,
        "presence_penalty": 0.0,
        "stop": ["<END>"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions", 
                json=payload, 
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenAI API error: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e.response.text}")
    except Exception as e:
        logger.error(f"Error calling OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI: {str(e)}")

async def call_ollama(prompt: str, temperature: float = 0.2, max_tokens: int = 140) -> str:
    """Call local Ollama API for text generation."""
    payload = {
        "model": GEN_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "You are a friendly Vision Flows Agency teammate.\n\nRULES\n- Use ONLY the provided Context. If missing, say what's missing and ask 1 targeted question.\n- Keep answers short: 60–100 words total. Max 4 bullets. No intro phrases or summaries.\n- Format lists with \"• \"; one idea per line; no tables unless asked.\n- If asked about pricing/timeline/scope: ask 1 scoping question, then give a clear next step (book call, custom quote, or starter package).\n- Do not repeat yourself or restate the question.\n- End every reply with the token: <END>\n\nEXAMPLES:\nUser: Do you build Shopify stores? What's the cost?\nAssistant:\n• Yes—Shopify setup, payments, products, and basic design\n• Typical range: $1,500–$3,500; varies by catalog size and integration\n• Share product count + must-have apps, and I'll confirm a package or custom quote\n<END>\n\nUser: Can you add a website chatbot?\nAssistant:\n• We install a site + Instagram chatbot for FAQs, leads, and simple booking\n• Setup: $500–$1,500; ongoing from $150–$300/mo based on features\n• Do you want lead qualification, calendar booking, or handoff to a human?\n<END>\n\nCONTEXT\n{{context}}"
            },
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "num_ctx": 4096
        },
        "stop": ["<END>"]
    }
    
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama API error: {e.response.text}")
        raise HTTPException(status_code=500, detail=f"Ollama API error: {e.response.text}")
    except Exception as e:
        logger.error(f"Error calling Ollama: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calling Ollama: {str(e)}")

def make_prompt(user_msg: str, contexts: List[Dict[str, Any]]) -> str:
    """Create a prompt with retrieved context for the LLM."""
    if not contexts:
        return f"Question: {user_msg}\n\nContext: No relevant documents found.\n\nAnswer: I don't have enough information to answer your question. Please provide more context or ask about something else."
    
    # Format context with short, titled chunks (following GPT's recommendation)
    context_chunks = []
    for context in contexts:
        # Extract section title if available, otherwise use source
        source = context.get("metadata", {}).get("source", "document")
        section_title = context.get("metadata", {}).get("section_title", "")
        
        if section_title:
            context_chunks.append(f"{section_title}:\n{context['text']}")
        else:
            context_chunks.append(f"{source}:\n{context['text']}")
    
    context_blob = "\n\n".join(context_chunks)
    
    return f"Question: {user_msg}\n\nContext:\n{context_blob}\n\nAnswer:"

# API endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "settings": "/settings",
            "suggested": "/suggested",
            "ingest": "/ingest",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model_provider": MODEL_PROVIDER,
        "llm_model": GEN_MODEL
    }

@app.get("/settings")
async def get_settings():
    """Get current chatbot settings."""
    return load_settings()

@app.post("/settings")
async def update_settings_endpoint(settings: SettingsUpdate):
    """Update chatbot settings."""
    try:
        # Convert to dict and remove None values
        updates = {k: v for k, v in settings.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid settings provided")
        
        result = update_settings(updates)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {"success": True, "settings": result, "message": "Settings updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/settings/reset")
async def reset_settings_endpoint():
    """Reset settings to defaults."""
    try:
        success = reset_settings()
        if success:
            return {"success": True, "message": "Settings reset to defaults"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset settings")
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggested")
async def get_suggested_questions():
    """Get suggested questions for quick access."""
    settings = load_settings()
    return {"suggested": settings.get("suggested", [])}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Main chat endpoint with RAG processing."""
    start_time = datetime.now()
    
    try:
        # Load current settings for LLM parameters
        settings = load_settings()
        chat_settings = settings.get("chat_settings", {})
        
        # Get LLM parameters from settings with sensible defaults
        temperature = chat_settings.get("temperature", 0.2)
        max_tokens = chat_settings.get("max_tokens", 140)  # Reduced default for conciseness
        
        # Step 1: Retrieve relevant documents (reduced to top 3-5 as recommended)
        hits = retrieve(request.message, k=5)[:3]  # Top 3 after reranking
        
        # Step 2: Create prompt with context
        prompt = make_prompt(request.message, hits)
        
        # Step 3: Generate response using LLM with user settings
        if MODEL_PROVIDER == "ollama":
            text = await call_ollama(prompt, temperature, max_tokens)
        else:
            text = await call_openai(prompt, temperature, max_tokens)
        
        # Step 4: Clean up response (remove <END> token if present)
        if text.endswith("<END>"):
            text = text[:-5].strip()
        
        # Step 5: Prepare response with citations
        response_time = (datetime.now() - start_time).total_seconds()
        
        citations = []
        for i, hit in enumerate(hits):
            citations.append({
                "index": i + 1,
                "source": hit.get("metadata", {}).get("source", "document"),
                "page": hit.get("metadata", {}).get("page_number"),
                "score": hit.get("rerank_score", 0),
                "text_preview": hit.get("text", "")[:100] + "..."
            })
        
        return ChatResponse(
            answer=text,
            citations=citations,
            context_used=len(hits),
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    """Ingest documents into the vector store."""
    try:
        input_path = request.input_path
        
        if os.path.isfile(input_path):
            # Single file ingestion
            result = ingest_single_file(
                input_path, 
                request.source_tag, 
                request.chunk_size, 
                request.overlap
            )
        elif os.path.isdir(input_path):
            # Directory ingestion
            result = ingest_folder(
                input_path, 
                request.source_tag, 
                request.chunk_size, 
                request.overlap
            )
        else:
            raise HTTPException(status_code=400, detail=f"Path does not exist: {input_path}")
        
        if result > 0:
            return {
                "success": True,
                "chunks_created": result,
                "message": f"Successfully ingested {result} chunks"
            }
        else:
            raise HTTPException(status_code=400, detail="No documents were ingested")
            
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingest/stats")
async def get_ingestion_statistics():
    """Get statistics about the vector store."""
    return get_ingestion_stats()

@app.get("/collection/info")
async def get_vector_collection_info():
    """Get information about the current vector collection."""
    return get_collection_info()

@app.post("/collection/clear")
async def clear_vector_collection():
    """Clear all documents from the vector collection."""
    try:
        result = clear_collection()
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    except Exception as e:
        logger.error(f"Error clearing collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/widget/embed.js")
async def get_embed_script():
    """Serve the embed script for Framer integration."""
    return FileResponse("../widget/embed.js", media_type="application/javascript")

@app.get("/widget/chat.html")
async def get_chat_interface():
    """Serve the chat interface HTML."""
    return FileResponse("../widget/chat.html", media_type="text/html")

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file for the chatbot."""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 5MB)
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"chatbot_icon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        file_path = UPLOADS_DIR / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return file info
        return JSONResponse({
            "success": True,
            "filename": filename,
            "url": f"/uploads/{filename}",
            "message": "Image uploaded successfully"
        })
        
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    """Serve uploaded images."""
    file_path = UPLOADS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": request.url.path}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting RAG Chatbot API...")
    logger.info(f"Model provider: {MODEL_PROVIDER}")
    logger.info(f"LLM model: {GEN_MODEL}")
    
    if MODEL_PROVIDER == "openai" and not OPENAI_API_KEY:
        logger.warning("OpenAI API key not set - chat functionality will not work")
    elif MODEL_PROVIDER == "ollama":
        logger.info(f"Ollama base URL: {OLLAMA_BASE_URL}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down RAG Chatbot API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
