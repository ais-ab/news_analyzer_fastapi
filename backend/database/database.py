from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
# Default to PostgreSQL for production, with SQLite fallback for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://news_user:news_password@localhost:5432/news_analyzer")

# Create engine
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration with optimized settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        echo=os.getenv("ENVIRONMENT") == "development"  # Enable SQL logging in development
    )
else:
    # SQLite configuration (for development fallback only)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database
async def init_db():
    """Initialize database tables"""
    try:
        # Import models to ensure they are registered
        from .models import Client, Source, AnalysisSession, BusinessInterest, ClientSource
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Create initial demo user if not exists
        await create_demo_user()
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

async def create_demo_user():
    """Create a demo user for testing purposes"""
    try:
        from .models import Client
        db = SessionLocal()
        
        # Check if demo user exists
        demo_user = db.query(Client).filter(Client.client_id == "demo_user").first()
        if not demo_user:
            demo_user = Client(client_id="demo_user")
            db.add(demo_user)
            db.commit()
            print("Demo user created successfully")
        else:
            print("Demo user already exists")
            
    except Exception as e:
        print(f"Error creating demo user: {e}")
    finally:
        db.close() 