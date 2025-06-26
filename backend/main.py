from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from database.database import engine
from database.models import Base

# Import routers
from api.routes import auth, sources, news, analysis
from database.database import init_db

# Load environment variables
load_dotenv()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting News Analyzer API...")
    await init_db()
    print("Database initialized")
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    print("Shutting down News Analyzer API...")

# Create FastAPI app
app = FastAPI(
    title="News Analyzer API",
    description="A modern news analysis platform with AI-powered filtering and summarization",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for AWS deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "News Analyzer API is running"}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])

@app.get("/")
async def root():
    return {
        "message": "News Analyzer API",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 