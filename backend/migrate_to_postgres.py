#!/usr/bin/env python3
"""
Migration script to transition from SQLite to PostgreSQL
This script helps migrate existing data and update the database configuration.
"""

import os
import sys
import sqlite3
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

def check_postgresql_connection():
    """Check if PostgreSQL is accessible"""
    try:
        database_url = os.getenv("DATABASE_URL", "postgresql://news_user:news_password@localhost:5432/news_analyzer")
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_sqlite_data():
    """Check if SQLite database exists and has data"""
    sqlite_path = "./db/analyzer.db"
    if not os.path.exists(sqlite_path):
        print("ℹ️  No SQLite database found - starting fresh with PostgreSQL")
        return False
    
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("ℹ️  SQLite database exists but is empty")
            return False
        
        print(f"📊 Found SQLite database with tables: {[table[0] for table in tables]}")
        
        # Check data in each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking SQLite database: {e}")
        return False

def migrate_data_from_sqlite():
    """Migrate data from SQLite to PostgreSQL"""
    sqlite_path = "./db/analyzer.db"
    database_url = os.getenv("DATABASE_URL", "postgresql://news_user:news_password@localhost:5432/news_analyzer")
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to PostgreSQL
        pg_engine = create_engine(database_url)
        pg_session = sessionmaker(bind=pg_engine)()
        
        print("🔄 Starting data migration...")
        
        # Migrate clients
        sqlite_cursor.execute("SELECT client_id, created_at FROM client")
        clients = sqlite_cursor.fetchall()
        for client in clients:
            pg_session.execute(text("""
                INSERT INTO client (client_id, created_at) 
                VALUES (:client_id, :created_at)
                ON CONFLICT (client_id) DO NOTHING
            """), {"client_id": client[0], "created_at": client[1]})
        
        # Migrate sources
        sqlite_cursor.execute("SELECT source_id, source_url, created_at FROM source")
        sources = sqlite_cursor.fetchall()
        for source in sources:
            pg_session.execute(text("""
                INSERT INTO source (source_id, source_url, created_at) 
                VALUES (:source_id, :source_url, :created_at)
                ON CONFLICT (source_id) DO NOTHING
            """), {"source_id": source[0], "source_url": source[1], "created_at": source[2]})
        
        # Migrate business interests
        sqlite_cursor.execute("SELECT id, client_id, interest_text, created_at FROM business_interest")
        interests = sqlite_cursor.fetchall()
        for interest in interests:
            pg_session.execute(text("""
                INSERT INTO business_interest (id, client_id, interest_text, created_at) 
                VALUES (:id, :client_id, :interest_text, :created_at)
                ON CONFLICT (id) DO NOTHING
            """), {"id": interest[0], "client_id": interest[1], "interest_text": interest[2], "created_at": interest[3]})
        
        # Migrate client sources
        sqlite_cursor.execute("SELECT client_id, source_id, created_at FROM client_source")
        client_sources = sqlite_cursor.fetchall()
        for cs in client_sources:
            pg_session.execute(text("""
                INSERT INTO client_source (client_id, source_id, created_at) 
                VALUES (:client_id, :source_id, :created_at)
                ON CONFLICT (client_id, source_id) DO NOTHING
            """), {"client_id": cs[0], "source_id": cs[1], "created_at": cs[2]})
        
        # Migrate analysis sessions
        sqlite_cursor.execute("SELECT id, client_id, business_interest_id, sources, results, created_at FROM analysis_session")
        sessions = sqlite_cursor.fetchall()
        for session in sessions:
            pg_session.execute(text("""
                INSERT INTO analysis_session (id, client_id, business_interest_id, sources, results, created_at) 
                VALUES (:id, :client_id, :business_interest_id, :sources, :results, :created_at)
                ON CONFLICT (id) DO NOTHING
            """), {"id": session[0], "client_id": session[1], "business_interest_id": session[2], 
                   "sources": session[3], "results": session[4], "created_at": session[5]})
        
        # Commit changes
        pg_session.commit()
        
        print("✅ Data migration completed successfully")
        
        # Close connections
        sqlite_conn.close()
        pg_session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def backup_sqlite_database():
    """Create a backup of the SQLite database"""
    sqlite_path = "./db/analyzer.db"
    if os.path.exists(sqlite_path):
        backup_path = f"./db/analyzer_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            import shutil
            shutil.copy2(sqlite_path, backup_path)
            print(f"✅ SQLite database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    return None

def update_environment_file():
    """Update .env file to use PostgreSQL"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update DATABASE_URL if it exists, otherwise add it
        if "DATABASE_URL=" in content:
            content = content.replace(
                "DATABASE_URL=sqlite:///./db/analyzer.db",
                "DATABASE_URL=postgresql://news_user:news_password@localhost:5432/news_analyzer"
            )
        else:
            content += "\nDATABASE_URL=postgresql://news_user:news_password@localhost:5432/news_analyzer"
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated .env file to use PostgreSQL")

def main():
    """Main migration function"""
    print("🚀 News Analyzer - SQLite to PostgreSQL Migration")
    print("=" * 50)
    
    # Step 1: Check PostgreSQL connection
    if not check_postgresql_connection():
        print("\n❌ Cannot proceed without PostgreSQL connection")
        print("Please ensure PostgreSQL is running and accessible")
        sys.exit(1)
    
    # Step 2: Check for existing SQLite data
    has_sqlite_data = check_sqlite_data()
    
    # Step 3: Create backup if needed
    if has_sqlite_data:
        backup_path = backup_sqlite_database()
        if not backup_path:
            print("❌ Failed to create backup - aborting migration")
            sys.exit(1)
    
    # Step 4: Migrate data if needed
    if has_sqlite_data:
        print("\n🔄 Migrating data from SQLite to PostgreSQL...")
        if not migrate_data_from_sqlite():
            print("❌ Data migration failed")
            sys.exit(1)
    
    # Step 5: Update environment configuration
    print("\n📝 Updating environment configuration...")
    update_environment_file()
    
    # Step 6: Initialize PostgreSQL database
    print("\n🔧 Initializing PostgreSQL database...")
    try:
        from database.database import init_db
        import asyncio
        asyncio.run(init_db())
        print("✅ PostgreSQL database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL database: {e}")
        sys.exit(1)
    
    print("\n🎉 Migration completed successfully!")
    print("\nNext steps:")
    print("1. Restart your application")
    print("2. Test the application to ensure everything works")
    print("3. If everything is working, you can remove the SQLite backup file")
    
    if has_sqlite_data:
        print(f"4. SQLite backup is available at: {backup_path}")

if __name__ == "__main__":
    main() 