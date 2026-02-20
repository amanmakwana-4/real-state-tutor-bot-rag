"""
Pydantic schemas for request/response models.
Defines all data structures used across the application.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


class Intent(str, Enum):
    """Detected user intent categories."""
    AREA_EXPLANATION = "AREA_EXPLANATION"
    INVESTMENT_ANALYSIS = "INVESTMENT_ANALYSIS"
    PRICE_EVALUATION = "PRICE_EVALUATION"
    GENERAL_QUERY = "GENERAL_QUERY"
    PROPERTY_SEARCH = "PROPERTY_SEARCH"
    COMPARISON = "COMPARISON"


class ExplanationDepth(str, Enum):
    """User preference for explanation detail level."""
    SIMPLE = "simple"
    DETAILED = "detailed"


class ExtractedEntities(BaseModel):
    """Entities extracted from user input."""
    location: Optional[str] = None
    price: Optional[float] = None
    price_unit: Optional[str] = None  # Cr, Lakh, etc.
    area: Optional[float] = None
    area_unit: Optional[str] = None  # sq ft, sq m, etc.
    bhk: Optional[int] = None
    property_type: Optional[str] = None
    amenities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)


class IntentAnalysis(BaseModel):
    """Result of intent detection and entity extraction."""
    intent: Intent
    confidence: float = Field(ge=0, le=1)
    entities: ExtractedEntities
    enriched_query: str
    assumptions: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Incoming chat request from frontend."""
    message: str = Field(..., min_length=1, max_length=1000)
    explanation_depth: ExplanationDepth = ExplanationDepth.SIMPLE
    session_id: Optional[str] = None


class RetrievedContext(BaseModel):
    """Context retrieved from vector store."""
    content: str
    score: float
    metadata: dict = Field(default_factory=dict)


class LLMEvaluation(BaseModel):
    """Structured response from LLM evaluation."""
    score: int = Field(ge=0, le=10)
    confidence: float = Field(ge=0, le=1)
    assumptions: str
    explanation: str
    improvements: str
    context_used: bool


class ChatResponse(BaseModel):
    """Response sent back to frontend."""
    response: str
    score: Optional[int] = None
    confidence: Optional[float] = None
    assumptions: Optional[str] = None
    explanation: Optional[str] = None
    improvements: Optional[str] = None
    context_used: bool = False
    intent_detected: Intent
    entities_extracted: ExtractedEntities
    retrieved_contexts: List[RetrievedContext] = Field(default_factory=list)


class PropertyListing(BaseModel):
    """Schema for property listing data."""
    id: str
    title: str
    location: str
    locality: str
    city: str = "Mumbai"
    price: float
    price_per_sqft: float
    carpet_area: float
    built_up_area: Optional[float] = None
    bhk: int
    property_type: str
    amenities: List[str] = Field(default_factory=list)
    description: str
    possession_status: str
    age_of_property: Optional[str] = None
    floor_number: Optional[str] = None
    total_floors: Optional[int] = None


class QuickAction(BaseModel):
    """Quick action button configuration."""
    id: str
    label: str
    query: str
    icon: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    vector_store: str
    llm_provider: str
