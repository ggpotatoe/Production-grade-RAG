"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    """Request model for search queries."""
    query: str = Field(..., description="The search query in natural language")
    language: str = Field(default="hu", description="Language code (hu or en)")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")

class SearchResult(BaseModel):
    """Model for a single search result."""
    score: float
    metadata: Dict[str, Any]
    content: str

class QueryResponse(BaseModel):
    """Response model for search queries."""
    answer: str = Field(..., description="The generated answer")
    sources: List[SearchResult] = Field(default_factory=list, description="Source documents used")
    language: str = Field(..., description="Language of the response")

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    qdrant_connected: bool
    collection_exists: bool

