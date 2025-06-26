from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Client, BusinessInterest, AnalysisSession
from api.schemas import BusinessInterestCreate, BusinessInterestResponse, StatusResponse
from api.routes.auth import get_current_client
from datetime import datetime, timedelta
from typing import List

router = APIRouter()

@router.post("/business-interest", response_model=BusinessInterestResponse)
async def create_business_interest(
    interest_data: BusinessInterestCreate,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Create a new business interest"""
    business_interest = BusinessInterest(
        client_id=current_client.client_id,
        interest_text=interest_data.interest_text
    )
    db.add(business_interest)
    db.commit()
    db.refresh(business_interest)
    
    return BusinessInterestResponse.from_orm(business_interest)

@router.get("/business-interest", response_model=List[BusinessInterestResponse])
async def get_business_interests(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get all business interests for the current client"""
    interests = db.query(BusinessInterest).filter(
        BusinessInterest.client_id == current_client.client_id
    ).order_by(BusinessInterest.created_at.desc()).all()
    
    return [BusinessInterestResponse.from_orm(interest) for interest in interests]

@router.get("/business-interest/{interest_id}", response_model=BusinessInterestResponse)
async def get_business_interest(
    interest_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get a specific business interest"""
    interest = db.query(BusinessInterest).filter(
        BusinessInterest.id == interest_id,
        BusinessInterest.client_id == current_client.client_id
    ).first()
    
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business interest not found"
        )
    
    return BusinessInterestResponse.from_orm(interest)

@router.delete("/business-interest/{interest_id}", response_model=StatusResponse)
async def delete_business_interest(
    interest_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Delete a business interest"""
    interest = db.query(BusinessInterest).filter(
        BusinessInterest.id == interest_id,
        BusinessInterest.client_id == current_client.client_id
    ).first()
    
    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business interest not found"
        )
    
    db.delete(interest)
    db.commit()
    
    return StatusResponse(
        status="success",
        message="Business interest deleted successfully",
        timestamp=datetime.now()
    )

@router.get("/statistics", response_model=dict)
async def get_statistics(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    # Get counts
    total_interests = db.query(BusinessInterest).filter(
        BusinessInterest.client_id == current_client.client_id
    ).count()
    
    total_sessions = db.query(AnalysisSession).filter(
        AnalysisSession.client_id == current_client.client_id
    ).count()
    
    # Get recent activity
    recent_sessions = db.query(AnalysisSession).filter(
        AnalysisSession.client_id == current_client.client_id,
        AnalysisSession.created_at >= datetime.now() - timedelta(days=7)
    ).count()
    
    # Get most recent business interest
    latest_interest = db.query(BusinessInterest).filter(
        BusinessInterest.client_id == current_client.client_id
    ).order_by(BusinessInterest.created_at.desc()).first()
    
    return {
        "total_business_interests": total_interests,
        "total_analysis_sessions": total_sessions,
        "sessions_last_7_days": recent_sessions,
        "latest_interest": latest_interest.interest_text if latest_interest else None,
        "account_created": current_client.created_at.isoformat()
    }

@router.get("/dashboard", response_model=dict)
async def get_dashboard_data(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get dashboard data for the frontend"""
    # Recent sessions
    recent_sessions = db.query(AnalysisSession).filter(
        AnalysisSession.client_id == current_client.client_id
    ).order_by(AnalysisSession.created_at.desc()).limit(5).all()
    
    # Recent business interests
    recent_interests = db.query(BusinessInterest).filter(
        BusinessInterest.client_id == current_client.client_id
    ).order_by(BusinessInterest.created_at.desc()).limit(3).all()
    
    return {
        "recent_sessions": [
            {
                "id": session.id,
                "created_at": session.created_at.isoformat(),
                "has_results": bool(session.results)
            }
            for session in recent_sessions
        ],
        "recent_interests": [
            {
                "id": interest.id,
                "interest_text": interest.interest_text,
                "created_at": interest.created_at.isoformat()
            }
            for interest in recent_interests
        ]
    } 