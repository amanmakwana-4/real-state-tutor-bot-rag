"""
Pinecone Vector Store Implementation.
Cloud-based vector storage for property embeddings.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np

from ..config import settings

logger = logging.getLogger(__name__)


class PineconeStore:
    """
    Pinecone-based vector store for cloud similarity search.
    Provides scalable, managed vector storage.
    """

    def __init__(self):
        self.index = None
        self.dimension = settings.embedding_dimension
        self.index_name = settings.pinecone_index_name
        self._initialized = False

    def _initialize(self):
        """Lazy initialization - connect to Pinecone."""
        if self._initialized:
            return
        
        if not settings.pinecone_api_key:
            logger.warning("Pinecone API key not configured")
            self._initialized = True
            return
        
        try:
            from pinecone import Pinecone
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Connect to existing index using host if provided
            if settings.pinecone_host:
                self.index = pc.Index(host=settings.pinecone_host)
            else:
                self.index = pc.Index(self.index_name)
            
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
            self._initialized = True
            
        except ImportError:
            logger.error("Pinecone client not installed. Run: pip install pinecone-client")
            self._initialized = True
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
            self._initialized = True

    def add_documents(
        self, 
        embeddings: List[np.ndarray], 
        metadata_list: List[Dict[str, Any]],
        contents: List[str],
        ids: Optional[List[str]] = None
    ):
        """
        Add documents with embeddings and metadata to Pinecone.
        
        Args:
            embeddings: List of embedding vectors
            metadata_list: List of metadata dicts for each document
            contents: List of text contents
            ids: Optional list of document IDs
        """
        self._initialize()
        
        if self.index is None:
            logger.error("Pinecone index not available")
            return
        
        try:
            # Prepare vectors for upsert
            vectors = []
            for i, (embedding, metadata, content) in enumerate(zip(embeddings, metadata_list, contents)):
                doc_id = ids[i] if ids else f"doc_{i}"
                
                # Add content to metadata (Pinecone stores metadata)
                full_metadata = {
                    **metadata,
                    'content': content[:40000]  # Pinecone metadata limit
                }
                
                # Convert numpy to list if needed
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                
                vectors.append({
                    'id': doc_id,
                    'values': embedding,
                    'metadata': full_metadata
                })
            
            # Batch upsert (Pinecone limit is 100 per batch)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Upserted {len(vectors)} documents to Pinecone")
            
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")

    def search(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in Pinecone.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matching documents with scores
        """
        self._initialize()
        
        if self.index is None:
            logger.warning("Pinecone index not available")
            return []
        
        try:
            # Convert numpy to list
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Build Pinecone filter
            pc_filter = self._build_pinecone_filter(filter_metadata)
            
            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=pc_filter
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                metadata = match.metadata or {}
                content = metadata.pop('content', '')
                
                formatted_results.append({
                    'content': content,
                    'score': float(match.score),
                    'metadata': metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return []

    def _build_pinecone_filter(self, filter_metadata: Optional[Dict]) -> Optional[Dict]:
        """Build Pinecone-compatible filter from metadata dict."""
        if not filter_metadata:
            return None
        
        # Pinecone uses specific filter syntax
        filters = {}
        for key, value in filter_metadata.items():
            if isinstance(value, (int, float, bool)):
                filters[key] = {"$eq": value}
            else:
                # String match (case-sensitive in Pinecone)
                filters[key] = {"$eq": str(value).lower()}
        
        return filters if filters else None

    def delete_all(self):
        """Delete all vectors from the index."""
        self._initialize()
        
        if self.index is None:
            return
        
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared all vectors from Pinecone index")
        except Exception as e:
            logger.error(f"Failed to clear Pinecone index: {e}")

    def delete_by_ids(self, ids: List[str]):
        """Delete specific vectors by ID."""
        self._initialize()
        
        if self.index is None:
            return
        
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} vectors from Pinecone")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        self._initialize()
        
        if self.index is None:
            return {
                'type': 'pinecone',
                'status': 'not initialized',
                'total_vectors': 0
            }
        
        try:
            stats = self.index.describe_index_stats()
            return {
                'type': 'pinecone',
                'status': 'active',
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_name': self.index_name
            }
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            return {
                'type': 'pinecone',
                'status': 'error',
                'error': str(e)
            }


# Singleton instance
pinecone_store = PineconeStore()
