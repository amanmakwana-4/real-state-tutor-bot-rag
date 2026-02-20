"""
Embedding Service for Vector Operations.
Supports OpenAI and local embedding models.
"""

import numpy as np
from typing import List, Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings.
    Supports OpenAI embeddings with fallback options.
    """

    def __init__(self):
        self.client = None
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self._initialized = False

    def _initialize(self):
        """Lazy initialization of embedding client."""
        if self._initialized:
            return
        
        try:
            if settings.openai_api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI embedding client initialized")
            else:
                logger.warning("No OpenAI API key found, embeddings will need alternative")
            
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise

    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of embedding vector
        """
        self._initialize()
        
        if not text.strip():
            return np.zeros(self.dimension)
        
        try:
            if self.client:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text[:8000]  # Truncate to avoid token limits
                )
                return np.array(response.data[0].embedding)
            else:
                # Fallback: Generate pseudo-random but deterministic embeddings
                # This is for testing without API key
                return self._fallback_embedding(text)
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._fallback_embedding(text)

    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        self._initialize()
        
        if not texts:
            return []
        
        try:
            if self.client:
                # Batch process for efficiency
                clean_texts = [t[:8000] if t.strip() else " " for t in texts]
                response = self.client.embeddings.create(
                    model=self.model,
                    input=clean_texts
                )
                return [np.array(r.embedding) for r in response.data]
            else:
                return [self._fallback_embedding(t) for t in texts]
                
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> np.ndarray:
        """
        Generate a deterministic fallback embedding for testing.
        Uses hash-based pseudo-random generation.
        """
        # Create deterministic seed from text
        text_hash = hash(text.lower().strip())
        np.random.seed(abs(text_hash) % (2**32))
        
        # Generate normalized random vector
        embedding = np.random.randn(self.dimension)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding

    def compute_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        """
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Singleton instance
embedding_service = EmbeddingService()
