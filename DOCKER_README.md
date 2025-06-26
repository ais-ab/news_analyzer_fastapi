# News Analyzer - Docker Deployment Guide

This guide explains how to deploy the News Analyzer application using Docker.

## 🏗️ Architecture

The application consists of:
- **Frontend**: React application served by Nginx
- **Backend**: FastAPI application with PostgreSQL database
- **Database**: PostgreSQL for data persistence
- **Optional**: Ollama for local LLM processing

## 📋 Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- At least 4GB RAM available
- 10GB free disk space

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd news_analyzer3

# Run setup script
chmod +x scripts/docker-setup.sh
./scripts/docker-setup.sh
```

### 2. Configure Environment

Edit the `.env` file with your configuration:

```bash
# Required
SECRET_KEY=your-super-secret-key-here

# Optional - for AI features
OPENAI_API_KEY=your-openai-api-key

# Optional - for local LLM
OLLAMA_BASE_URL=http://ollama:11434
```

### 3. Deploy to Production

```bash
# Deploy with the deployment script
chmod +x scripts/docker-deploy.sh
./scripts/docker-deploy.sh

# Or manually
docker-compose up -d --build
```

### 4. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development Mode

For development with hot reloading:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access development servers
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 📊 Monitoring & Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Check Service Status

```bash
docker-compose ps
```

### Health Checks

```bash
# Frontend health
curl http://localhost/health

# Backend health
curl http://localhost:8000/api/health

# Database health
docker-compose exec postgres pg_isready -U news_user -d news_analyzer
```

### Database Management

```bash
# Connect to database
docker-compose exec postgres psql -U news_user -d news_analyzer

# Backup database
docker-compose exec postgres pg_dump -U news_user news_analyzer > backup.sql

# Restore database
docker-compose exec -T postgres psql -U news_user -d news_analyzer < backup.sql
```

## 🔒 Security Considerations

### Production Deployment

1. **Change Default Passwords**: Update database passwords in `.env`
2. **Use Strong Secret Key**: Generate a strong SECRET_KEY
3. **Enable HTTPS**: Use a reverse proxy (Nginx/Traefik) with SSL
4. **Network Security**: Restrict container network access
5. **Regular Updates**: Keep base images updated

### Environment Variables

```bash
# Security
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@host:port/db

# API Keys
OPENAI_API_KEY=your-openai-key
OLLAMA_BASE_URL=http://ollama:11434
```

## 🐳 Docker Commands Reference

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Maintenance

```bash
# Update images
docker-compose pull

# Remove old images
docker-compose down --rmi all

# Clean up volumes
docker-compose down -v

# Full cleanup
docker system prune -a
```

### Troubleshooting

```bash
# Check container logs
docker-compose logs [service-name]

# Execute commands in container
docker-compose exec backend python -c "print('Hello')"
docker-compose exec postgres psql -U news_user -d news_analyzer

# Inspect container
docker-compose exec backend bash
```

## 📁 File Structure

```
news_analyzer3/
├── docker-compose.yml          # Production configuration
├── docker-compose.dev.yml      # Development configuration
├── Dockerfile.backend          # Backend production image
├── Dockerfile.frontend         # Frontend production image
├── Dockerfile.backend.dev      # Backend development image
├── Dockerfile.frontend.dev     # Frontend development image
├── nginx.conf                  # Nginx configuration
├── .dockerignore              # Docker ignore file
├── .env                       # Environment variables
├── scripts/
│   ├── docker-setup.sh        # Setup script
│   └── docker-deploy.sh       # Deployment script
└── backend/
    └── init.sql               # Database initialization
```

## 🔄 Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Use load balancer
# Add nginx or traefik for load balancing
```

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or change port in docker-compose.yml
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   # Ensure database is ready before starting backend
   ```

3. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   chmod +x scripts/*.sh
   ```

4. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   # Docker Desktop: Settings > Resources > Memory
   ```

### Performance Optimization

1. **Use Multi-stage Builds**: Already implemented in Dockerfiles
2. **Optimize Images**: Use Alpine Linux base images
3. **Caching**: Leverage Docker layer caching
4. **Resource Limits**: Set appropriate memory/CPU limits

## 📞 Support

For issues related to Docker deployment:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all prerequisites are met
4. Check Docker and Docker Compose versions 