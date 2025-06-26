#!/usr/bin/env python3
"""
Database Connection Test Script for News Analyzer
This script tests the PostgreSQL connection and shows basic database information.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection and show basic information"""
    
    # Get database URL from environment or use default
    database_url = os.getenv("DATABASE_URL", "postgresql://news_user:news_password@localhost:5432/news_analyzer")
    
    print("🔍 Testing Database Connection")
    print("=" * 40)
    print(f"Database URL: {database_url}")
    print()
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ Connection test: {test_value}")
            
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📊 PostgreSQL version: {version.split(',')[0]}")
            
            # Get current database and user
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            print(f"🗄️  Database: {db_name}")
            print(f"👤 User: {user}")
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"📋 Tables found: {len(tables)}")
                for table in tables:
                    # Get row count for each table
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    print(f"   - {table}: {count} rows")
            else:
                print("📋 No tables found (database may be empty)")
            
            # Get database size
            result = conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
            size = result.scalar()
            print(f"💾 Database size: {size}")
            
            # Check active connections
            result = conn.execute(text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"))
            connections = result.scalar()
            print(f"🔗 Active connections: {connections}")
            
        print()
        print("✅ Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("🔧 Troubleshooting tips:")
        print("1. Ensure PostgreSQL is running: pg_isready")
        print("2. Check if database exists: psql -U postgres -c '\\l'")
        print("3. Run setup script: ./scripts/setup-postgres-local.sh")
        print("4. Check environment variables in .env file")
        return False

def show_connection_info():
    """Show connection information and commands"""
    print()
    print("🔌 Connection Information")
    print("=" * 40)
    print("Host: localhost")
    print("Port: 5432")
    print("Database: news_analyzer")
    print("Username: news_user")
    print("Password: news_password")
    print()
    print("📝 Quick Connection Commands:")
    print("psql -U news_user -d news_analyzer -h localhost")
    print("psql \"postgresql://news_user:news_password@localhost:5432/news_analyzer\"")
    print()
    print("🛠️  Setup Commands:")
    print("./scripts/setup-postgres-local.sh")
    print("cd backend && python migrate_to_postgres.py")

def main():
    """Main function"""
    print("🗄️  News Analyzer - Database Connection Test")
    print("=" * 50)
    
    # Test connection
    success = test_connection()
    
    # Show connection info
    show_connection_info()
    
    if success:
        print()
        print("🎉 Database is ready for use!")
        print("You can now start the News Analyzer application.")
    else:
        print()
        print("❌ Please fix the connection issues before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main() 