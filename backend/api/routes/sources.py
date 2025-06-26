from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Source, Client, ClientSource
from api.schemas import SourceCreate, SourceResponse, SourceListResponse, StatusResponse
from api.routes.auth import get_current_client
import requests
from urllib.parse import urlparse
from datetime import datetime

router = APIRouter()

def check_url(url: str) -> bool:
    """Validate URL accessibility"""
    url = url.strip()
    
    if not url.startswith(('http://', 'https://')):
        url = "https://" + url
    
    parsed = urlparse(url)
    if not parsed.netloc:
        return False
    
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code < 400 or response.status_code in [401, 403]:
            return True
    except requests.RequestException:
        pass
    
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        if response.status_code < 400 or response.status_code in [401, 403]:
            return True
    except requests.RequestException:
        pass
    
    return False

@router.get("/", response_model=SourceListResponse)
async def get_sources(current_client: Client = Depends(get_current_client), db: Session = Depends(get_db)):
    """Get all sources for the current client"""
    # Get sources associated with the client
    client_sources = db.query(ClientSource).filter(ClientSource.client_id == current_client.client_id).all()
    source_ids = [cs.source_id for cs in client_sources]
    
    sources = db.query(Source).filter(Source.source_id.in_(source_ids)).all()
    
    return SourceListResponse(
        sources=[SourceResponse.from_orm(source) for source in sources],
        total_count=len(sources)
    )

@router.post("/", response_model=SourceResponse)
async def add_source(
    source_data: SourceCreate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Add a new source"""
    source_url = str(source_data.source_url)
    
    # Validate URL
    if not check_url(source_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or inaccessible URL"
        )
    
    # Check if source already exists
    existing_source = db.query(Source).filter(Source.source_url == source_url).first()
    
    if existing_source:
        # Check if client already has this source
        existing_client_source = db.query(ClientSource).filter(
            ClientSource.client_id == current_client.client_id,
            ClientSource.source_id == existing_source.source_id
        ).first()
        
        if existing_client_source:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Source already exists for this client"
            )
        
        # Add source to client
        client_source = ClientSource(
            client_id=current_client.client_id,
            source_id=existing_source.source_id
        )
        db.add(client_source)
        db.commit()
        
        return SourceResponse.from_orm(existing_source)
    
    # Create new source
    new_source = Source(source_url=source_url)
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    
    # Add source to client
    client_source = ClientSource(
        client_id=current_client.client_id,
        source_id=new_source.source_id
    )
    db.add(client_source)
    db.commit()
    
    return SourceResponse.from_orm(new_source)

@router.delete("/{source_id}", response_model=StatusResponse)
async def remove_source(
    source_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Remove a source from client's list"""
    # Check if client has this source
    client_source = db.query(ClientSource).filter(
        ClientSource.client_id == current_client.client_id,
        ClientSource.source_id == source_id
    ).first()
    
    if not client_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found for this client"
        )
    
    # Remove the association
    db.delete(client_source)
    db.commit()
    
    return StatusResponse(
        status="success",
        message="Source removed successfully",
        timestamp=datetime.now()
    )

@router.get("/popular", response_model=dict)
async def get_popular_sources():
    """Get popular news sources by category"""
    return {
        "Market Data": [
            "https://marketwatch.com",
            "https://finance.yahoo.com",
            "https://investing.com"
        ],
        "Business News": [
            "https://reuters.com",
            "https://bloomberg.com",
            "https://cnbc.com"
        ],
        "Stock Analysis": [
            "https://seekingalpha.com",
            "https://investors.com",
            "https://barrons.com"
        ]
    } 