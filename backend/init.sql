-- Initialize the news_analyzer database
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (these will be created by SQLAlchemy, but we can add any custom setup here)
-- The actual table creation is handled by the FastAPI application using SQLAlchemy models

-- Create indexes for better performance (optional)
-- CREATE INDEX IF NOT EXISTS idx_sources_client_id ON sources(client_id);
-- CREATE INDEX IF NOT EXISTS idx_articles_source_id ON articles(source_id);
-- CREATE INDEX IF NOT EXISTS idx_analysis_sessions_client_id ON analysis_sessions(client_id);

-- Insert any initial data if needed
-- INSERT INTO clients (client_id, created_at) VALUES ('demo_user', NOW()) ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE news_analyzer TO news_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO news_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO news_user; 