#!/usr/bin/env python3
"""
Reset PostgreSQL database with correct schema
This script drops all existing tables and recreates them with the current model definitions.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reset_database():
    """Reset the PostgreSQL database with correct schema"""
    database_url = os.getenv("DATABASE_URL", "postgresql://news_user:news_password@localhost:5432/news_analyzer")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        print("🔄 Resetting PostgreSQL database...")
        
        # Drop all existing tables
        with engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("SET session_replication_role = replica;"))
            
            # Drop tables in correct order (respecting foreign key constraints)
            tables_to_drop = [
                "analysis_session",
                "business_interest", 
                "client_source",
                "source",
                "client"
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
                    print(f"   - Dropped table: {table}")
                except Exception as e:
                    print(f"   - Warning: Could not drop {table}: {e}")
            
            # Re-enable foreign key checks
            conn.execute(text("SET session_replication_role = DEFAULT;"))
            conn.commit()
        
        print("✅ All tables dropped successfully")
        
        # Import models and create tables
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        print("✅ All tables recreated with correct schema")
        
        # Create demo user
        from database.database import create_demo_user
        import asyncio
        asyncio.run(create_demo_user())
        
        print("✅ Database reset completed successfully!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        raise

if __name__ == "__main__":
    reset_database() 