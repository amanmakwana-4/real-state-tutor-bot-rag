"""
Configuration module for Real Estate Tutor Bot.
Handles environment variables and application settings.
"""

import os
from typing import Literal
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""
    pinecone_api_key: str = ""
    
    # Pinecone settings
    pinecone_host: str = ""
    pinecone_index_name: str = "real-estate-tutor"
    
    # Vector store configuration
    use_pinecone: bool = False
    
    # LLM Configuration
    llm_provider: Literal["openai", "gemini"] = "openai"
    openai_model: str = "gpt-3.5-turbo"
    gemini_model: str = "gemini-pro"
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimension: int = 1536
    
    # RAG Configuration
    rag_top_k: int = 3
    similarity_threshold: float = 0.7
    
    # FAISS Configuration
    faiss_index_path: str = "data/faiss_index"
    
    # Data paths
    property_data_path: str = "data/property_listings.csv"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
