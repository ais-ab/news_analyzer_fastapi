from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Client, BusinessInterest, AnalysisSession
from api.schemas import NewsAnalysisRequest, NewsAnalysisResponse, Article, StatusResponse
from api.routes.auth import get_current_client
import json
import sys
import os
from datetime import datetime
from typing import List

# Import utils from backend directory
from utils.llm_functions import get_news_async

router = APIRouter()

@router.post("/analyze", response_model=NewsAnalysisResponse)
async def analyze_news(
    request: NewsAnalysisRequest,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Analyze news based on business interest and sources"""
    
    # Save business interest
    business_interest = BusinessInterest(
        client_id=current_client.client_id,
        interest_text=request.business_interest
    )
    db.add(business_interest)
    db.commit()
    db.refresh(business_interest)
    
    try:
        # Get news analysis using existing function
        news_result = await get_news_async(
            business_interest=request.business_interest,
            sources=request.sources
        )
        
        # Parse the summary result to extract articles
        articles = []
        if news_result:
            # The news_result is a markdown summary, we need to parse it to extract articles
            lines = news_result.split('\n')
            current_article = None
            collecting_summary = False
            summary_lines = []
            
            for line in lines:
                line = line.strip()
                
                # Look for article headers (## 📄 Article X)
                if line.startswith('## 📄 Article'):
                    if current_article:
                        # Save the collected summary to the previous article
                        if summary_lines:
                            current_article['content'] = ' '.join(summary_lines)
                        articles.append(Article(**current_article))
                    
                    current_article = {
                        'title': '',
                        'content': '',
                        'url': '',
                        'source': 'Multiple Sources',
                        'published_date': datetime.now().isoformat(),
                        'relevance_score': 1.0
                    }
                    collecting_summary = False
                    summary_lines = []
                
                # Extract title
                elif line.startswith('**Title:**') and current_article:
                    current_article['title'] = line.replace('**Title:**', '').strip()
                
                # Extract source URL
                elif line.startswith('**Source:**') and current_article:
                    url = line.replace('**Source:**', '').strip()
                    if url != 'N/A':
                        current_article['url'] = url
                        # Extract domain as source
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            current_article['source'] = parsed.netloc.replace('www.', '')
                        except:
                            pass
                
                # Extract publish date
                elif line.startswith('**Published:**') and current_article:
                    date_str = line.replace('**Published:**', '').strip()
                    if date_str and date_str != 'N/A':
                        current_article['published_date'] = date_str
                
                # Start collecting summary content
                elif line.startswith('**Summary:**') and current_article:
                    collecting_summary = True
                    summary_lines = []
                
                # Collect summary content
                elif collecting_summary and line and not line.startswith('**') and not line.startswith('---') and not line.startswith('#'):
                    summary_lines.append(line)
            
            # Add the last article if exists
            if current_article:
                if summary_lines:
                    current_article['content'] = ' '.join(summary_lines)
                articles.append(Article(**current_article))
        
        # If no articles were parsed from the summary, create a fallback
        if not articles and news_result:
            articles.append(Article(
                title="News Analysis Summary",
                content=news_result,
                url="",
                source="Multiple Sources",
                published_date=datetime.now().isoformat(),
                relevance_score=1.0
            ))
        
        # Save analysis session
        analysis_session = AnalysisSession(
            client_id=current_client.client_id,
            business_interest_id=business_interest.id,
            sources=json.dumps(request.sources),
            results=json.dumps([article.dict() for article in articles])
        )
        db.add(analysis_session)
        db.commit()
        db.refresh(analysis_session)
        
        return NewsAnalysisResponse(
            session_id=analysis_session.id,
            articles=articles,
            summary=None,  # You can add summary generation here
            total_articles=len(articles),
            relevant_articles=len(articles),
            analysis_date=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing news: {str(e)}"
        )

@router.get("/sessions", response_model=List[dict])
async def get_analysis_sessions(
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get all analysis sessions for the current client"""
    sessions = db.query(AnalysisSession).filter(
        AnalysisSession.client_id == current_client.client_id
    ).order_by(AnalysisSession.created_at.desc()).all()
    
    return [
        {
            "id": session.id,
            "business_interest_id": session.business_interest_id,
            "sources": json.loads(session.sources) if session.sources else [],
            "created_at": session.created_at.isoformat(),
            "has_results": bool(session.results)
        }
        for session in sessions
    ]

@router.get("/sessions/{session_id}", response_model=NewsAnalysisResponse)
async def get_analysis_session(
    session_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Get a specific analysis session"""
    session = db.query(AnalysisSession).filter(
        AnalysisSession.id == session_id,
        AnalysisSession.client_id == current_client.client_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis session not found"
        )
    
    if not session.results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis results not available"
        )
    
    # Parse results
    articles_data = json.loads(session.results)
    articles = [Article(**article_data) for article_data in articles_data]
    
    return NewsAnalysisResponse(
        session_id=session.id,
        articles=articles,
        summary=None,
        total_articles=len(articles),
        relevant_articles=len(articles),
        analysis_date=session.created_at
    )

@router.delete("/sessions/{session_id}", response_model=StatusResponse)
async def delete_analysis_session(
    session_id: int,
    current_client: Client = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Delete an analysis session"""
    session = db.query(AnalysisSession).filter(
        AnalysisSession.id == session_id,
        AnalysisSession.client_id == current_client.client_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return StatusResponse(
        status="success",
        message="Analysis session deleted successfully",
        timestamp=datetime.now()
    ) 