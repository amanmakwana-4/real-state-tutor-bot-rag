"""
FAISS Index Builder Script.
Converts property_listings.csv into embeddings and builds FAISS index.

Usage:
    python scripts/build_faiss_index.py
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.config import settings
from app.services.embedding_service import embedding_service
from app.vector_store.faiss_store import faiss_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_property_text(row: pd.Series) -> str:
    """
    Build searchable text representation of a property listing.
    Optimized for semantic search.
    """
    amenities = row.get('amenities', '')
    if pd.notna(amenities):
        amenities_list = amenities.replace('"', '').split(',')
        amenities_str = ', '.join(amenities_list[:5])
    else:
        amenities_str = 'Standard amenities'
    
    text = f"""
Property: {row['title']}
Location: {row['locality']}, {row['location']}, {row['city']}
Price: ₹{row['price_cr']} Crore ({row['price_per_sqft']}/sq ft)
Configuration: {row['bhk']} BHK {row['property_type']}
Carpet Area: {row['carpet_area_sqft']} sq ft
Built-up Area: {row['built_up_area_sqft']} sq ft
Status: {row['possession_status']}
Age: {row.get('age_of_property', 'Unknown')}
Floor: {row.get('floor_number', 'N/A')}/{row.get('total_floors', 'N/A')}
Amenities: {amenities_str}
Description: {row['description']}
    """.strip()
    
    return text


def build_metadata(row: pd.Series) -> dict:
    """Extract metadata for filtering and display."""
    return {
        'id': str(row['id']),
        'title': row['title'],
        'location': row['location'].lower(),
        'locality': row['locality'].lower(),
        'price_cr': float(row['price_cr']),
        'price_per_sqft': int(row['price_per_sqft']),
        'carpet_area': int(row['carpet_area_sqft']),
        'bhk': int(row['bhk']),
        'property_type': row['property_type'],
        'possession_status': row['possession_status']
    }


def main():
    """Main function to build FAISS index."""
    logger.info("=" * 50)
    logger.info("FAISS Index Builder")
    logger.info("=" * 50)
    
    # Load property data
    data_path = Path(__file__).parent.parent / settings.property_data_path
    
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        logger.info("Creating from default location...")
        data_path = Path(__file__).parent.parent / "data" / "property_listings.csv"
    
    logger.info(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} properties")
    
    # Build text representations
    logger.info("Building text representations...")
    texts = []
    metadata_list = []
    
    for _, row in df.iterrows():
        text = build_property_text(row)
        metadata = build_metadata(row)
        texts.append(text)
        metadata_list.append(metadata)
    
    logger.info(f"Built {len(texts)} property documents")
    
    # Generate embeddings
    logger.info("Generating embeddings (this may take a moment)...")
    embeddings = embedding_service.embed_texts(texts)
    logger.info(f"Generated {len(embeddings)} embeddings")
    
    # Clear existing index
    logger.info("Clearing existing index...")
    faiss_store.delete_all()
    
    # Add documents to FAISS
    logger.info("Adding documents to FAISS index...")
    faiss_store.add_documents(
        embeddings=embeddings,
        metadata_list=metadata_list,
        contents=texts
    )
    
    # Save index
    logger.info("Saving index to disk...")
    faiss_store.save_index()
    
    # Verify
    stats = faiss_store.get_stats()
    logger.info(f"Index built successfully!")
    logger.info(f"Total vectors: {stats['total_vectors']}")
    logger.info(f"Index path: {stats['index_path']}")
    
    # Test search
    logger.info("\nTesting search...")
    test_query = "2BHK apartment in Parel around 2 crore"
    query_embedding = embedding_service.embed_text(test_query)
    results = faiss_store.search(query_embedding, top_k=3)
    
    logger.info(f"\nTest query: '{test_query}'")
    logger.info("Top 3 results:")
    for i, result in enumerate(results, 1):
        logger.info(f"\n{i}. Score: {result['score']:.4f}")
        logger.info(f"   Title: {result['metadata'].get('title', 'N/A')}")
        logger.info(f"   Location: {result['metadata'].get('locality', 'N/A')}")
        logger.info(f"   Price: ₹{result['metadata'].get('price_cr', 'N/A')} Cr")
    
    logger.info("\n" + "=" * 50)
    logger.info("Index build complete!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
