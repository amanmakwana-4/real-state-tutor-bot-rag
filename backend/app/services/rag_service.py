"""
RAG (Retrieval-Augmented Generation) Service.
Handles context retrieval from vector stores.
"""

import logging
from typing import List, Optional

from ..config import settings
from ..models.schemas import (
    RetrievedContext, 
    IntentAnalysis,
    Intent
)
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class RAGService:
    """
    Service for retrieving relevant context using RAG.
    Supports both FAISS (local) and Pinecone (cloud) backends.
    """

    def __init__(self):
        self.vector_store = None
        self.top_k = settings.rag_top_k
        self.similarity_threshold = settings.similarity_threshold
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of vector store."""
        if self._initialized:
            return
        
        try:
            if settings.use_pinecone and settings.pinecone_api_key:
                from ..vector_store.pinecone_store import pinecone_store
                self.vector_store = pinecone_store
                logger.info("Using Pinecone vector store")
            else:
                from ..vector_store.faiss_store import faiss_store
                self.vector_store = faiss_store
                logger.info("Using FAISS vector store")
            
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            # Don't raise - allow fallback operation
            self._initialized = True

    def build_search_query(self, analysis: IntentAnalysis) -> str:
        """
        Build an optimized search query based on intent analysis.
        """
        parts = []
        entities = analysis.entities
        
        # Add intent-specific context
        if analysis.intent == Intent.PRICE_EVALUATION:
            parts.append("property price valuation")
        elif analysis.intent == Intent.INVESTMENT_ANALYSIS:
            parts.append("investment potential ROI")
        elif analysis.intent == Intent.AREA_EXPLANATION:
            parts.append("carpet area built-up area measurement")
        
        # Add location
        if entities.location:
            parts.append(f"location {entities.location}")
        
        # Add price context
        if entities.price:
            parts.append(f"price {entities.price} {entities.price_unit or 'Cr'}")
        
        # Add area context
        if entities.area:
            parts.append(f"area {entities.area} {entities.area_unit or 'sq ft'}")
        
        # Add BHK
        if entities.bhk:
            parts.append(f"{entities.bhk} BHK")
        
        # Add keywords
        if entities.keywords:
            parts.extend(entities.keywords[:5])
        
        return ' '.join(parts)

    def retrieve(
        self, 
        query: str, 
        analysis: Optional[IntentAnalysis] = None,
        top_k: Optional[int] = None
    ) -> List[RetrievedContext]:
        """
        Retrieve relevant context from vector store.
        
        Args:
            query: Search query
            analysis: Optional intent analysis for smart filtering
            top_k: Number of results to return
            
        Returns:
            List of retrieved context items
        """
        self._initialize()
        
        k = top_k or self.top_k
        
        try:
            # Generate query embedding
            query_embedding = embedding_service.embed_text(query)
            
            if query_embedding is None:
                logger.warning("Failed to generate query embedding")
                return []
            
            # Search vector store
            if self.vector_store:
                results = self.vector_store.search(
                    query_embedding=query_embedding,
                    top_k=k,
                    filter_metadata=self._build_filter(analysis)
                )
            else:
                results = []
            
            # Filter by similarity threshold
            filtered_results = [
                RetrievedContext(
                    content=r.get('content', ''),
                    score=r.get('score', 0.0),
                    metadata=r.get('metadata', {})
                )
                for r in results
                if r.get('score', 0) >= self.similarity_threshold
            ]
            
            logger.info(f"Retrieved {len(filtered_results)} contexts for query")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []

    def _build_filter(self, analysis: Optional[IntentAnalysis]) -> Optional[dict]:
        """
        Build metadata filter based on intent analysis.
        """
        if not analysis or not analysis.entities:
            return None
        
        filters = {}
        entities = analysis.entities
        
        # Location filter
        if entities.location:
            filters['locality'] = entities.location.lower()
        
        # BHK filter
        if entities.bhk:
            filters['bhk'] = entities.bhk
        
        # Price range filter (approximate)
        if entities.price and entities.price_unit:
            if entities.price_unit == 'Cr':
                filters['price_range'] = f"{entities.price}cr"
            elif entities.price_unit == 'Lakh':
                filters['price_range'] = f"{entities.price}lakh"
        
        return filters if filters else None

    def format_context_for_prompt(
        self, 
        contexts: List[RetrievedContext]
    ) -> str:
        """
        Format retrieved contexts for inclusion in LLM prompt.
        """
        if not contexts:
            return "No specific property data found. Providing general evaluation."
        
        formatted_parts = ["### Relevant Property Data ###"]
        
        for i, ctx in enumerate(contexts, 1):
            formatted_parts.append(f"\n**Property {i}:**")
            formatted_parts.append(ctx.content)
            
            if ctx.metadata:
                meta_str = ", ".join(
                    f"{k}: {v}" for k, v in ctx.metadata.items()
                    if k not in ['embedding', 'id']
                )
                if meta_str:
                    formatted_parts.append(f"Metadata: {meta_str}")
        
        return "\n".join(formatted_parts)

    def get_store_stats(self) -> dict:
        """Get statistics about the vector store."""
        self._initialize()
        
        if self.vector_store:
            return self.vector_store.get_stats()
        
        return {"status": "not initialized", "count": 0}


# Singleton instance
rag_service = RAGService()
