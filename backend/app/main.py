"""
Real Estate Tutor Bot - Main Application Entry Point.
FastAPI application with CORS, routes, and error handling.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routes import chat_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initialize services on startup, cleanup on shutdown.
    """
    # Startup
    logger.info("=" * 50)
    logger.info("Real Estate Tutor Bot Starting...")
    logger.info("=" * 50)
    
    # Log configuration
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector Store: {'Pinecone' if settings.use_pinecone else 'FAISS'}")
    logger.info(f"RAG Top-K: {settings.rag_top_k}")
    
    # Initialize services lazily on first request
    logger.info("Services will initialize on first request")
    
    yield
    
    # Shutdown
    logger.info("Real Estate Tutor Bot Shutting Down...")


# Create FastAPI application
app = FastAPI(
    title="Real Estate Tutor Bot",
    description="""
    Smart RAG Evaluation Platform for Real Estate Education.
    
    This API provides:
    - Intent detection for short, cryptic user inputs
    - Entity extraction (location, price, area, BHK)
    - RAG-based context retrieval
    - LLM evaluation with scoring
    
    Designed to handle real-world consumer inputs like:
    - "700 sq ft Parel worth 2.1 Cr?"
    - "Carpet area meaning?"
    - "Good investment?"
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.llm_provider else "An error occurred"
        }
    )


# Include routers
app.include_router(chat_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Real Estate Tutor Bot",
        "version": "1.0.0",
        "description": "Smart RAG Evaluation Platform",
        "endpoints": {
            "chat": "/api/chat/",
            "quick_actions": "/api/chat/quick-actions",
            "health": "/api/chat/health",
            "stats": "/api/chat/stats",
            "docs": "/docs"
        }
    }


@app.get("/api/health")
async def api_health():
    """Simple health check for load balancers."""
    return {"status": "ok"}


# Run with: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
