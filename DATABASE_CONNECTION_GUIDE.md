# Database Connection Guide - News Analyzer

This guide explains how to connect to the local PostgreSQL database for the News Analyzer application.

## 🗄️ Database Information

### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: news_analyzer
- **Username**: news_user
- **Password**: news_password
- **Connection String**: `postgresql://news_user:news_password@localhost:5432/news_analyzer`

## 🔧 Prerequisites

Before connecting, ensure PostgreSQL is installed and running:

### Check if PostgreSQL is installed:
```bash
psql --version
```

### Check if PostgreSQL service is running:
```bash
pg_isready
```

If PostgreSQL is not installed or running, follow the setup guide:
```bash
./scripts/setup-postgres-local.sh
```

## 🔌 Connection Methods

### 1. Command Line (psql)

#### Connect to the database:
```bash
psql -U news_user -d news_analyzer -h localhost
```

#### Alternative connection methods:
```bash
# Using connection string
psql "postgresql://news_user:news_password@localhost:5432/news_analyzer"

# Using environment variables
export PGPASSWORD=news_password
psql -U news_user -d news_analyzer -h localhost
```

#### Useful psql commands:
```sql
-- List all tables
\dt

-- Describe table structure
\d table_name

-- List all databases
\l

-- List all users
\du

-- Show current database
SELECT current_database();

-- Show current user
SELECT current_user;

-- Exit psql
\q
```

### 2. Python Scripts

#### Using psycopg2:
```python
import psycopg2
from psycopg2 import Error

try:
    # Connect to database
    connection = psycopg2.connect(
        host="localhost",
        database="news_analyzer",
        user="news_user",
        password="news_password",
        port="5432"
    )
    
    # Create cursor
    cursor = connection.cursor()
    
    # Execute query
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"PostgreSQL version: {db_version}")
    
    # List tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print("Tables:", [table[0] for table in tables])
    
except (Exception, Error) as error:
    print(f"Error connecting to PostgreSQL: {error}")
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Database connection closed")
```

#### Using SQLAlchemy (as in the application):
```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Create engine
DATABASE_URL = "postgresql://news_user:news_password@localhost:5432/news_analyzer"
engine = create_engine(DATABASE_URL)

# Test connection
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connection successful!")

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Example query
try:
    result = db.execute(text("SELECT COUNT(*) FROM client"))
    count = result.scalar()
    print(f"Number of clients: {count}")
finally:
    db.close()
```

### 3. GUI Tools

#### pgAdmin (Free PostgreSQL GUI):
1. Download and install pgAdmin from https://www.pgadmin.org/
2. Open pgAdmin
3. Right-click "Servers" → "Register" → "Server"
4. Fill in connection details:
   - **Name**: News Analyzer Local
   - **Host**: localhost
   - **Port**: 5432
   - **Database**: news_analyzer
   - **Username**: news_user
   - **Password**: news_password

#### DBeaver (Universal Database Tool):
1. Download DBeaver from https://dbeaver.io/
2. Open DBeaver
3. Click "New Database Connection"
4. Select "PostgreSQL"
5. Fill in connection details:
   - **Host**: localhost
   - **Port**: 5432
   - **Database**: news_analyzer
   - **Username**: news_user
   - **Password**: news_password

#### TablePlus (macOS/Windows):
1. Download TablePlus from https://tableplus.com/
2. Click "Create a new connection"
3. Select "PostgreSQL"
4. Fill in connection details and connect

## 📊 Database Schema

### Main Tables

#### 1. client
```sql
-- View client table structure
\d client

-- Sample data
SELECT * FROM client LIMIT 5;
```

#### 2. source
```sql
-- View source table structure
\d source

-- Sample data
SELECT * FROM source LIMIT 5;
```

#### 3. business_interest
```sql
-- View business_interest table structure
\d business_interest

-- Sample data
SELECT * FROM business_interest LIMIT 5;
```

#### 4. analysis_session
```sql
-- View analysis_session table structure
\d analysis_session

-- Sample data
SELECT * FROM analysis_session LIMIT 5;
```

#### 5. client_source
```sql
-- View client_source table structure
\d client_source

-- Sample data
SELECT * FROM client_source LIMIT 5;
```

## 🔍 Useful Queries

### Check Database Health:
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('news_analyzer'));

-- Check table sizes
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(table_name)) as size
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY pg_total_relation_size(table_name) DESC;

-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'news_analyzer';
```

### Application Data Queries:
```sql
-- Get all clients with their business interests
SELECT 
    c.client_id,
    c.created_at as client_created,
    COUNT(bi.id) as interest_count
FROM client c
LEFT JOIN business_interest bi ON c.client_id = bi.client_id
GROUP BY c.client_id, c.created_at;

-- Get all sources with usage count
SELECT 
    s.source_url,
    COUNT(cs.client_id) as usage_count
FROM source s
LEFT JOIN client_source cs ON s.source_id = cs.source_id
GROUP BY s.source_url
ORDER BY usage_count DESC;

-- Get recent analysis sessions
SELECT 
    as.id,
    c.client_id,
    bi.interest_text,
    as.created_at
FROM analysis_session as
JOIN client c ON as.client_id = c.client_id
JOIN business_interest bi ON as.business_interest_id = bi.id
ORDER BY as.created_at DESC
LIMIT 10;
```

## 🛠️ Database Management

### Backup Database:
```bash
# Create backup
pg_dump -U news_user -h localhost news_analyzer > backup_$(date +%Y%m%d_%H%M%S).sql

# Create compressed backup
pg_dump -U news_user -h localhost news_analyzer | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restore Database:
```bash
# Restore from backup
psql -U news_user -h localhost news_analyzer < backup_file.sql

# Restore from compressed backup
gunzip -c backup_file.sql.gz | psql -U news_user -h localhost news_analyzer
```

### Reset Database:
```bash
# Drop and recreate database
psql -U news_user -h localhost postgres -c "DROP DATABASE IF EXISTS news_analyzer;"
psql -U news_user -h localhost postgres -c "CREATE DATABASE news_analyzer OWNER news_user;"

# Reinitialize tables (run from backend directory)
cd backend
python -c "from database.database import init_db; import asyncio; asyncio.run(init_db())"
```

## 🔧 Troubleshooting

### Common Connection Issues:

#### 1. Connection Refused:
```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL service
# macOS:
brew services start postgresql

# Ubuntu/Debian:
sudo systemctl start postgresql
```

#### 2. Authentication Failed:
```bash
# Check if user exists
psql -U postgres -h localhost -c "\du"

# Create user if needed
psql -U postgres -h localhost -c "CREATE USER news_user WITH PASSWORD 'news_password';"
```

#### 3. Database Does Not Exist:
```bash
# Create database
psql -U postgres -h localhost -c "CREATE DATABASE news_analyzer OWNER news_user;"
```

#### 4. Permission Denied:
```bash
# Grant permissions
psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE news_analyzer TO news_user;"
psql -U news_user -h localhost news_analyzer -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO news_user;"
```

### Environment Variables:
```bash
# Set environment variables for easier connection
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=news_analyzer
export PGUSER=news_user
export PGPASSWORD=news_password

# Now you can connect simply with:
psql
```

## 📱 Quick Reference

### Connection Commands:
```bash
# Quick connect
psql -U news_user -d news_analyzer -h localhost

# With password prompt
PGPASSWORD=news_password psql -U news_user -d news_analyzer -h localhost

# Using connection string
psql "postgresql://news_user:news_password@localhost:5432/news_analyzer"
```

### Common psql Commands:
```sql
\dt          -- List tables
\d table     -- Describe table
\l           -- List databases
\du          -- List users
\q           -- Quit
\?           -- Help
```

### Application Connection Test:
```bash
# Test from backend directory
cd backend
python -c "
from database.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful!')
"
```

---

## 🆘 Need Help?

If you encounter issues:

1. **Check the setup script**: `./scripts/setup-postgres-local.sh`
2. **Run the migration script**: `cd backend && python migrate_to_postgres.py`
3. **Check PostgreSQL logs**: Look for error messages in system logs
4. **Verify environment**: Ensure all environment variables are set correctly

For additional support, check the main README.md file or run the setup scripts for automated configuration. 