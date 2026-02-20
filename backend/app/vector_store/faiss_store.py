"""
FAISS Vector Store Implementation.
Local vector storage for property embeddings.
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from ..config import settings

logger = logging.getLogger(__name__)


class FAISSStore:
    """
    FAISS-based vector store for local similarity search.
    Handles storage, retrieval, and management of property embeddings.
    """

    def __init__(self):
        self.index = None
        self.metadata_store: Dict[int, Dict] = {}
        self.id_counter = 0
        self.dimension = settings.embedding_dimension
        self.index_path = settings.faiss_index_path
        self._initialized = False

    def _initialize(self):
        """Lazy initialization - load existing index or create new."""
        if self._initialized:
            return
        
        try:
            import faiss
            
            # Try to load existing index
            if self._load_index():
                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                logger.info("Created new FAISS index")
            
            self._initialized = True
            
        except ImportError:
            logger.error("FAISS not installed. Run: pip install faiss-cpu")
            self._initialized = True
        except Exception as e:
            logger.error(f"FAISS initialization failed: {e}")
            self._initialized = True

    def _load_index(self) -> bool:
        """Load index and metadata from disk."""
        try:
            import faiss
            
            index_file = f"{self.index_path}/index.faiss"
            metadata_file = f"{self.index_path}/metadata.json"
            
            if os.path.exists(index_file) and os.path.exists(metadata_file):
                self.index = faiss.read_index(index_file)
                
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    self.metadata_store = {int(k): v for k, v in data['metadata'].items()}
                    self.id_counter = data.get('id_counter', len(self.metadata_store))
                
                return True
            return False
            
        except Exception as e:
            logger.warning(f"Could not load existing index: {e}")
            return False

    def save_index(self):
        """Save index and metadata to disk."""
        try:
            import faiss
            
            os.makedirs(self.index_path, exist_ok=True)
            
            index_file = f"{self.index_path}/index.faiss"
            metadata_file = f"{self.index_path}/metadata.json"
            
            if self.index is not None:
                faiss.write_index(self.index, index_file)
            
            with open(metadata_file, 'w') as f:
                json.dump({
                    'metadata': self.metadata_store,
                    'id_counter': self.id_counter
                }, f, indent=2)
            
            logger.info(f"Saved FAISS index with {self.index.ntotal if self.index else 0} vectors")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def add_documents(
        self, 
        embeddings: List[np.ndarray], 
        metadata_list: List[Dict[str, Any]],
        contents: List[str]
    ):
        """
        Add documents with embeddings and metadata to the index.
        
        Args:
            embeddings: List of embedding vectors
            metadata_list: List of metadata dicts for each document
            contents: List of text contents
        """
        self._initialize()
        
        if self.index is None:
            logger.error("FAISS index not initialized")
            return
        
        if len(embeddings) != len(metadata_list) or len(embeddings) != len(contents):
            raise ValueError("Embeddings, metadata, and contents must have same length")
        
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings).astype('float32')
        faiss_normalize_L2 = lambda x: x / np.linalg.norm(x, axis=1, keepdims=True)
        embeddings_normalized = faiss_normalize_L2(embeddings_array)
        
        # Add to index
        start_id = self.id_counter
        self.index.add(embeddings_normalized)
        
        # Store metadata
        for i, (meta, content) in enumerate(zip(metadata_list, contents)):
            doc_id = start_id + i
            self.metadata_store[doc_id] = {
                **meta,
                'content': content,
                'id': doc_id
            }
        
        self.id_counter += len(embeddings)
        logger.info(f"Added {len(embeddings)} documents to FAISS index")

    def search(
        self, 
        query_embedding: np.ndarray, 
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matching documents with scores
        """
        self._initialize()
        
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty or not initialized")
            return []
        
        try:
            # Normalize query
            query = query_embedding.astype('float32').reshape(1, -1)
            query = query / np.linalg.norm(query)
            
            # Search more than needed if filtering
            search_k = min(top_k * 3 if filter_metadata else top_k, self.index.ntotal)
            
            scores, indices = self.index.search(query, search_k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for not found
                    continue
                
                metadata = self.metadata_store.get(int(idx), {})
                
                # Apply filters if specified
                if filter_metadata and not self._matches_filter(metadata, filter_metadata):
                    continue
                
                results.append({
                    'content': metadata.get('content', ''),
                    'score': float(score),
                    'metadata': {k: v for k, v in metadata.items() if k != 'content'}
                })
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []

    def _matches_filter(self, metadata: Dict, filters: Dict) -> bool:
        """Check if metadata matches all filters."""
        for key, value in filters.items():
            if key not in metadata:
                continue
            
            meta_value = str(metadata[key]).lower()
            filter_value = str(value).lower()
            
            # Partial match for strings
            if filter_value not in meta_value:
                return False
        
        return True

    def delete_all(self):
        """Clear the entire index."""
        self._initialize()
        
        try:
            import faiss
            
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata_store = {}
            self.id_counter = 0
            self.save_index()
            
            logger.info("FAISS index cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        self._initialize()
        
        return {
            'type': 'faiss',
            'status': 'active' if self.index is not None else 'not initialized',
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_path': self.index_path
        }


# Singleton instance
faiss_store = FAISSStore()
