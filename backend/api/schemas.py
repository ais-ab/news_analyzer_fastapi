from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    client_id: Optional[str] = None

# Business Interest schemas
class BusinessInterestCreate(BaseModel):
    interest_text: str

class BusinessInterestResponse(BaseModel):
    id: int
    client_id: str
    interest_text: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Source schemas
class SourceCreate(BaseModel):
    source_url: HttpUrl

class SourceResponse(BaseModel):
    source_id: int
    source_url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SourceListResponse(BaseModel):
    sources: List[SourceResponse]
    total_count: int

# News Analysis schemas
class NewsAnalysisRequest(BaseModel):
    business_interest: str
    sources: List[str]

class Article(BaseModel):
    title: str
    content: str
    url: str
    source: str
    published_date: Optional[str] = None
    relevance_score: Optional[float] = None

class NewsAnalysisResponse(BaseModel):
    session_id: int
    articles: List[Article]
    summary: Optional[str] = None
    total_articles: int
    relevant_articles: int
    analysis_date: datetime
    
    class Config:
        from_attributes = True

# Analysis Session schemas
class AnalysisSessionResponse(BaseModel):
    id: int
    client_id: str
    business_interest_id: int
    sources: str  # JSON string
    results: Optional[str] = None  # JSON string
    created_at: datetime
    
    class Config:
        from_attributes = True

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# Status schemas
class StatusResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime

class ClientInfoResponse(BaseModel):
    client_id: str
    status: str
    message: str
    timestamp: datetime 