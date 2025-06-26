#!/bin/bash

# News Analyzer Docker Setup Script
set -e

echo "🚀 Setting up News Analyzer with Docker and PostgreSQL..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# News Analyzer Environment Variables

# Database (PostgreSQL)
DATABASE_URL=postgresql://news_user:news_password@postgres:5432/news_analyzer

# Security
SECRET_KEY=your-secret-key-change-in-production

# OpenAI API (optional - for AI features)
OPENAI_API_KEY=

# Ollama (optional - for local LLM)
OLLAMA_BASE_URL=http://ollama:11434

# Environment
ENVIRONMENT=production
EOF
    echo "✅ .env file created. Please update it with your actual values."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/db
mkdir -p backend/tmp
mkdir -p logs

# Set proper permissions
chmod +x scripts/docker-setup.sh

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your actual API keys and configuration"
echo "2. Run 'docker-compose up -d' to start the application with PostgreSQL"
echo "3. Access the application at http://localhost"
echo ""
echo "🔧 Development mode:"
echo "   Run 'docker-compose -f docker-compose.dev.yml up -d' for development with hot reloading"
echo ""
echo "📊 Monitoring:"
echo "   Run 'docker-compose logs -f' to view logs"
echo "   Run 'docker-compose ps' to check service status"
echo ""
echo "🗄️  Database Information:"
echo "   - PostgreSQL is now the default database"
echo "   - Database: news_analyzer"
echo "   - User: news_user"
echo "   - Password: news_password"
echo "   - Port: 5432 (accessible from host)"
echo ""
echo "🔄 Migration from SQLite:"
echo "   If you have existing SQLite data, run the migration script:"
echo "   cd backend && python migrate_to_postgres.py" 