"""
Chat API Routes.
Handles all chat-related endpoints for the Real Estate Tutor Bot.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models.schemas import (
    ChatRequest, 
    ChatResponse, 
    QuickAction,
    HealthResponse
)
from ..services.evaluation_service import evaluation_service
from ..services.rag_service import rag_service
from ..services.llm_service import llm_service
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def process_chat(request: ChatRequest):
    """
    Process a chat message and return evaluation response.
    
    This endpoint:
    1. Detects user intent from short/incomplete inputs
    2. Extracts entities (location, price, area, etc.)
    3. Enriches query with inferred context
    4. Retrieves relevant property data via RAG
    5. Evaluates and scores the query using LLM
    
    Args:
        request: ChatRequest with message and preferences
        
    Returns:
        ChatResponse with evaluation, score, and suggestions
    """
    try:
        print(f"\n[CHAT ROUTE] Received request: {request.message}")
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        response = await evaluation_service.process_query(request)
        
        print(f"[CHAT ROUTE] Response generated - Intent: {response.intent_detected}, Score: {response.score}")
        logger.info(f"Processed query - Intent: {response.intent_detected}, Score: {response.score}")
        
        return response
        
    except Exception as e:
        print(f"[CHAT ROUTE] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat: {str(e)}"
        )


@router.get("/quick-actions", response_model=List[QuickAction])
async def get_quick_actions():
    """
    Get predefined quick action buttons.
    
    Returns:
        List of quick actions for common queries
    """
    actions = evaluation_service.get_quick_actions()
    return [QuickAction(**action) for action in actions]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint with service status.
    
    Returns:
        Service health status including vector store and LLM info
    """
    try:
        # Get vector store status
        vector_stats = rag_service.get_store_stats()
        
        # Get LLM status
        llm_status = llm_service.get_status()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            vector_store=f"{vector_stats.get('type', 'unknown')} ({vector_stats.get('total_vectors', 0)} vectors)",
            llm_provider=f"{llm_status.get('provider', 'unknown')} - {llm_status.get('status', 'unknown')}"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="degraded",
            version="1.0.0",
            vector_store="error",
            llm_provider="error"
        )


@router.post("/feedback")
async def submit_feedback(
    message_id: str,
    helpful: bool,
    comment: str = ""
):
    """
    Submit feedback for a chat response.
    
    Args:
        message_id: ID of the message being rated
        helpful: Whether the response was helpful
        comment: Optional feedback comment
        
    Returns:
        Acknowledgment
    """
    # In production, this would store feedback for model improvement
    logger.info(f"Feedback received for {message_id}: helpful={helpful}")
    
    return {"status": "received", "message_id": message_id}


@router.get("/stats")
async def get_stats():
    """
    Get system statistics.
    
    Returns:
        Current system statistics
    """
    vector_stats = rag_service.get_store_stats()
    llm_status = llm_service.get_status()
    
    return {
        "vector_store": vector_stats,
        "llm": llm_status,
        "config": {
            "rag_top_k": settings.rag_top_k,
            "similarity_threshold": settings.similarity_threshold,
            "use_pinecone": settings.use_pinecone
        }
    }
