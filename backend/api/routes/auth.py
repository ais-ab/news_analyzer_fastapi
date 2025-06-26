from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Client
from api.schemas import Token, TokenData, StatusResponse, ClientInfoResponse
import os
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

def get_current_client(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current client from token"""
    client_id = credentials.credentials
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return client

@router.post("/login", response_model=Token)
async def login(db: Session = Depends(get_db)):
    """Login endpoint - creates or retrieves client"""
    # Use demo_user as the default client ID for testing
    client_id = os.getenv("CLIENT_ID", "demo_user")
    
    # Check if client exists, create if not
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        client = Client(client_id=client_id)
        db.add(client)
        db.commit()
        db.refresh(client)
    
    return Token(
        access_token=client_id,
        token_type="bearer"
    )

@router.get("/me", response_model=ClientInfoResponse)
async def get_current_user(current_client: Client = Depends(get_current_client)):
    """Get current client information"""
    return ClientInfoResponse(
        client_id=current_client.client_id,
        status="success",
        message=f"Authenticated as {current_client.client_id}",
        timestamp=datetime.now()
    )

@router.post("/logout", response_model=StatusResponse)
async def logout():
    """Logout endpoint"""
    return StatusResponse(
        status="success",
        message="Successfully logged out",
        timestamp=datetime.now()
    ) 