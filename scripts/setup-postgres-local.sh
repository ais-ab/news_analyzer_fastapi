#!/bin/bash

# Local PostgreSQL Setup Script for News Analyzer
set -e

echo "🗄️  Setting up PostgreSQL locally for News Analyzer development..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed."
    echo ""
    echo "📦 Installation instructions:"
    echo ""
    echo "macOS (using Homebrew):"
    echo "  brew install postgresql"
    echo "  brew services start postgresql"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib"
    echo "  sudo systemctl start postgresql"
    echo "  sudo systemctl enable postgresql"
    echo ""
    echo "Windows:"
    echo "  Download from https://www.postgresql.org/download/windows/"
    echo ""
    echo "After installation, run this script again."
    exit 1
fi

# Check if PostgreSQL service is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL service is not running."
    echo "Please start PostgreSQL service and run this script again."
    exit 1
fi

echo "✅ PostgreSQL is installed and running"

# Create database and user
echo "🔧 Setting up database and user..."

# Get current user
CURRENT_USER=$(whoami)

# Create user if it doesn't exist
psql -d postgres -c "SELECT 1 FROM pg_roles WHERE rolname='news_user'" | grep -q 1 || {
    echo "Creating user 'news_user'..."
    psql -d postgres -c "CREATE USER news_user WITH PASSWORD 'news_password';"
}

# Create database if it doesn't exist
psql -d postgres -c "SELECT 1 FROM pg_database WHERE datname='news_analyzer'" | grep -q 1 || {
    echo "Creating database 'news_analyzer'..."
    psql -d postgres -c "CREATE DATABASE news_analyzer OWNER news_user;"
}

# Grant privileges
echo "Granting privileges..."
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE news_analyzer TO news_user;"
psql -d news_analyzer -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO news_user;"
psql -d news_analyzer -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO news_user;"

# Create .env file for local development
if [ ! -f .env ]; then
    echo "📝 Creating .env file for local development..."
    cat > .env << EOF
# News Analyzer Environment Variables (Local Development)

# Database (PostgreSQL)
DATABASE_URL=postgresql://news_user:news_password@localhost:5432/news_analyzer

# Security
SECRET_KEY=your-secret-key-change-in-production

# OpenAI API (optional - for AI features)
OPENAI_API_KEY=

# Environment
ENVIRONMENT=development
EOF
    echo "✅ .env file created for local development"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "✅ PostgreSQL setup completed successfully!"
echo ""
echo "📋 Connection Information:"
echo "   - Host: localhost"
echo "   - Port: 5432"
echo "   - Database: news_analyzer"
echo "   - User: news_user"
echo "   - Password: news_password"
echo ""
echo "🔧 Next steps:"
echo "1. Install Python dependencies: pip install -r backend/requirements.txt"
echo "2. Run the migration script if you have existing SQLite data:"
echo "   cd backend && python migrate_to_postgres.py"
echo "3. Start the backend server: cd backend && python main.py"
echo "4. Start the frontend: cd frontend && npm start"
echo ""
echo "🛠️  Useful PostgreSQL commands:"
echo "   - Connect to database: psql -U news_user -d news_analyzer"
echo "   - List tables: \dt"
echo "   - View table structure: \d table_name"
echo "   - Exit: \q" 