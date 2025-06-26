# Docker Troubleshooting Guide for AWS EC2

## 🚨 Common Docker Build Errors and Solutions

### Error: pip install fails during Docker build

**Problem**: The Docker build fails when trying to install Python dependencies, usually at line 15 of Dockerfile.backend.

**Solutions**:

#### Solution 1: Use the Updated Dockerfile (Recommended)

The main `Dockerfile.backend` has been updated with all necessary system dependencies. Try rebuilding:

```bash
# Stop any running containers
docker-compose down

# Remove old images
docker rmi news_analyzer_backend

# Rebuild with the updated Dockerfile
docker-compose up -d --build
```

#### Solution 2: Use the Simplified Version

If the main Dockerfile still fails, use the simplified version:

```bash
# Copy the simplified Dockerfile
cp Dockerfile.backend.simple Dockerfile.backend

# Rebuild
docker-compose down
docker-compose up -d --build
```

#### Solution 3: Manual Debugging

If you want to debug the issue manually:

```bash
# Build with verbose output
docker build -f Dockerfile.backend -t news-analyzer-backend . --progress=plain --no-cache

# Or build step by step
docker build -f Dockerfile.backend -t news-analyzer-backend . --target 0
```

### Error: Memory Issues During Build

**Problem**: EC2 instance runs out of memory during Docker build.

**Solutions**:

```bash
# Check available memory
free -h

# If memory is low, increase swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Error: Network Issues During pip install

**Problem**: pip can't download packages due to network issues.

**Solutions**:

```bash
# Use a different pip mirror
pip install --index-url https://pypi.org/simple/ -r requirements.txt

# Or use a faster mirror
pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

### Error: Permission Issues

**Problem**: Permission denied errors during Docker build.

**Solutions**:

```bash
# Fix file permissions
sudo chown -R ec2-user:ec2-user .
chmod +x docker-compose.yml

# Or run Docker with sudo (not recommended for production)
sudo docker-compose up -d --build
```

## 🔧 Step-by-Step Troubleshooting Process

### Step 1: Check System Resources

```bash
# Check available disk space
df -h

# Check available memory
free -h

# Check CPU usage
top
```

### Step 2: Check Docker Status

```bash
# Check if Docker is running
sudo systemctl status docker

# Restart Docker if needed
sudo systemctl restart docker

# Check Docker version
docker --version
docker-compose --version
```

### Step 3: Clean Docker Environment

```bash
# Remove all containers
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -q)

# Remove all volumes
docker volume prune -f

# Remove all networks
docker network prune -f
```

### Step 4: Rebuild Step by Step

```bash
# Build backend only
docker build -f Dockerfile.backend -t news-analyzer-backend .

# If successful, build frontend
docker build -f Dockerfile.frontend -t news-analyzer-frontend .

# Then run with docker-compose
docker-compose up -d
```

## 🛠️ Alternative Deployment Methods

### Method 1: Use Pre-built Images

If building locally is problematic, you can use a different approach:

```bash
# Use a different base image
# Edit Dockerfile.backend to use:
FROM python:3.11-alpine

# Or use a more complete base image
FROM python:3.11-bullseye
```

### Method 2: Install Dependencies on Host

```bash
# Install Python and dependencies directly on EC2
sudo yum install -y python3 python3-pip

# Install dependencies
pip3 install -r backend/requirements.txt

# Run the application directly
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Method 3: Use Docker Hub Images

```bash
# Pull pre-built images from Docker Hub
docker pull python:3.11-slim
docker pull postgres:15-alpine
docker pull nginx:alpine
```

## 📋 Common Error Messages and Solutions

### "No module named 'psycopg2'"
```bash
# Install PostgreSQL development libraries
sudo yum install -y postgresql-devel
```

### "No module named 'cryptography'"
```bash
# Install OpenSSL development libraries
sudo yum install -y openssl-devel
```

### "No module named 'PIL'"
```bash
# Install image processing libraries
sudo yum install -y libjpeg-devel libpng-devel
```

### "gcc: command not found"
```bash
# Install build tools
sudo yum groupinstall -y "Development Tools"
```

## 🔍 Debugging Commands

### Check Docker Build Context

```bash
# See what files are being copied
docker build -f Dockerfile.backend -t test . --progress=plain 2>&1 | grep "COPY\|ADD"
```

### Check Container Logs

```bash
# Check container logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend
```

### Enter Running Container

```bash
# Enter the container to debug
docker exec -it news_analyzer_backend bash

# Check what's installed
pip list
python -c "import sys; print(sys.path)"
```

## 🚀 Quick Fix Commands

### Complete Reset and Rebuild

```bash
# Stop everything
docker-compose down

# Remove everything
docker system prune -a -f

# Rebuild from scratch
docker-compose up -d --build
```

### Use Simplified Requirements

```bash
# Use simplified requirements
cp backend/requirements-simple.txt backend/requirements.txt

# Rebuild
docker-compose up -d --build
```

### Check for Specific Package Issues

```bash
# Test individual package installation
docker run --rm python:3.11-slim pip install psycopg2-binary

# Test with system dependencies
docker run --rm python:3.11-slim bash -c "
apt-get update && apt-get install -y libpq-dev gcc &&
pip install psycopg2-binary
"
```

## 📞 Getting Help

If you're still having issues:

1. **Check the logs**: `docker-compose logs backend`
2. **Try the simplified version**: Use `Dockerfile.backend.simple`
3. **Check system resources**: Make sure you have enough memory and disk space
4. **Use a larger instance**: Consider upgrading to t3.large if t3.medium is too small
5. **Check AWS status**: Ensure there are no AWS service issues

## 🎯 Success Indicators

When everything is working correctly, you should see:

```bash
# All containers running
docker ps
# Should show: news_analyzer_backend, news_analyzer_frontend, news_analyzer_db

# Health check passing
curl http://localhost:8000/api/health
# Should return: {"status": "healthy"}

# Frontend accessible
curl http://localhost
# Should return HTML content
``` 