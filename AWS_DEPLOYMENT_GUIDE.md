# AWS Deployment Guide for News Analyzer

This guide provides multiple deployment options for your News Analyzer application on AWS, from simple to production-ready setups.

## 🏗️ Architecture Overview

Your application consists of:
- **Frontend**: React.js application
- **Backend**: FastAPI Python application
- **Database**: PostgreSQL
- **Optional**: Redis for caching, Ollama for local LLM

## 🚀 Deployment Options

### Option 1: Simple Deployment (EC2 + Docker)

**Best for**: Development, testing, or small-scale production

#### Prerequisites
- AWS Account
- EC2 instance (t3.medium or larger recommended)
- Domain name (optional)

#### Steps

1. **Launch EC2 Instance**
   ```bash
   # Launch Ubuntu 22.04 LTS instance
   # Security Groups: SSH (22), HTTP (80), HTTPS (443), Custom (8000)
   ```

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Logout and login again
   exit
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Deploy Application**
   ```bash
   # Clone your repository
   git clone <your-repo-url>
   cd news_analyzer3
   
   # Create .env file
   cat > .env << EOF
   DATABASE_URL=postgresql://news_user:news_password@postgres:5432/news_analyzer
   SECRET_KEY=your-super-secret-key-change-this
   OPENAI_API_KEY=your-openai-api-key
   ENVIRONMENT=production
   EOF
   
   # Start the application
   docker-compose up -d
   ```

4. **Setup Nginx (Optional)**
   ```bash
   sudo apt install nginx -y
   sudo nano /etc/nginx/sites-available/news-analyzer
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:80;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/news-analyzer /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Option 2: Production-Ready (ECS + RDS + ALB)

**Best for**: Production workloads with high availability

#### Architecture
- **ECS Fargate**: Containerized application
- **RDS PostgreSQL**: Managed database
- **Application Load Balancer**: Traffic distribution
- **Route 53**: DNS management
- **CloudWatch**: Monitoring and logging

#### Steps

1. **Create RDS Database**
   ```bash
   # Using AWS CLI
   aws rds create-db-instance \
     --db-instance-identifier news-analyzer-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username news_user \
     --master-user-password your-secure-password \
     --allocated-storage 20 \
     --vpc-security-group-ids sg-xxxxxxxxx \
     --db-name news_analyzer
   ```

2. **Create ECR Repositories**
   ```bash
   aws ecr create-repository --repository-name news-analyzer-backend
   aws ecr create-repository --repository-name news-analyzer-frontend
   ```

3. **Build and Push Images**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and push backend
   docker build -f Dockerfile.backend -t news-analyzer-backend .
   docker tag news-analyzer-backend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-backend:latest
   docker push your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-backend:latest
   
   # Build and push frontend
   docker build -f Dockerfile.frontend -t news-analyzer-frontend .
   docker tag news-analyzer-frontend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-frontend:latest
   docker push your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-frontend:latest
   ```

4. **Create ECS Task Definitions**
   ```json
   // backend-task-definition.json
   {
     "family": "news-analyzer-backend",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::your-account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-backend:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql://news_user:password@your-rds-endpoint:5432/news_analyzer"
           },
           {
             "name": "SECRET_KEY",
             "value": "your-secret-key"
           },
           {
             "name": "OPENAI_API_KEY",
             "value": "your-openai-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/news-analyzer-backend",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

5. **Create ECS Services**
   ```bash
   # Register task definitions
   aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
   aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json
   
   # Create services
   aws ecs create-service \
     --cluster news-analyzer-cluster \
     --service-name news-analyzer-backend \
     --task-definition news-analyzer-backend:1 \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx,subnet-yyyyy],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
   ```

### Option 3: Serverless (Lambda + API Gateway + S3)

**Best for**: Cost-effective, auto-scaling applications

#### Architecture
- **Lambda**: Backend API functions
- **API Gateway**: REST API management
- **S3**: Frontend hosting
- **RDS Proxy**: Database connection pooling
- **CloudFront**: CDN for frontend

#### Steps

1. **Setup S3 for Frontend**
   ```bash
   # Create S3 bucket
   aws s3 mb s3://news-analyzer-frontend
   
   # Enable static website hosting
   aws s3 website s3://news-analyzer-frontend --index-document index.html --error-document index.html
   
   # Upload frontend build
   cd frontend
   npm run build
   aws s3 sync build/ s3://news-analyzer-frontend
   ```

2. **Create Lambda Functions**
   ```python
   # lambda_function.py
   import json
   from mangum import Mangum
   from fastapi import FastAPI
   
   app = FastAPI()
   
   @app.get("/api/health")
   async def health_check():
       return {"status": "healthy"}
   
   # Add your FastAPI routes here
   
   handler = Mangum(app)
   ```

3. **Deploy with SAM**
   ```yaml
   # template.yaml
   AWSTemplateFormatVersion: '2010-09-09'
   Transform: AWS::Serverless-2016-10-31
   
   Resources:
     NewsAnalyzerFunction:
       Type: AWS::Serverless::Function
       Properties:
         CodeUri: ./backend/
         Handler: lambda_function.handler
         Runtime: python3.9
         Timeout: 30
         MemorySize: 512
         Environment:
           Variables:
             DATABASE_URL: !Ref DatabaseUrl
             SECRET_KEY: !Ref SecretKey
         Events:
           Api:
             Type: Api
             Properties:
               Path: /{proxy+}
               Method: ANY
   ```

### Option 4: Kubernetes (EKS)

**Best for**: Complex microservices, advanced orchestration

#### Architecture
- **EKS**: Managed Kubernetes cluster
- **RDS**: Database
- **Ingress Controller**: Traffic management
- **Helm**: Package management

#### Steps

1. **Create EKS Cluster**
   ```bash
   eksctl create cluster \
     --name news-analyzer-cluster \
     --region us-east-1 \
     --nodegroup-name standard-workers \
     --node-type t3.medium \
     --nodes 3 \
     --nodes-min 1 \
     --nodes-max 4
   ```

2. **Deploy with Helm**
   ```yaml
   # values.yaml
   backend:
     image:
       repository: your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-backend
       tag: latest
     env:
       - name: DATABASE_URL
         value: "postgresql://user:pass@rds-endpoint:5432/db"
   
   frontend:
     image:
       repository: your-account.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-frontend
       tag: latest
   ```

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your-super-secret-key

# API Keys
OPENAI_API_KEY=your-openai-api-key

# Environment
ENVIRONMENT=production

# Optional
OLLAMA_BASE_URL=http://ollama:11434
REDIS_URL=redis://redis:6379
```

### Secrets Management
```bash
# Using AWS Secrets Manager
aws secretsmanager create-secret \
  --name news-analyzer-secrets \
  --description "News Analyzer application secrets" \
  --secret-string '{"SECRET_KEY":"your-key","OPENAI_API_KEY":"your-key"}'
```

## 📊 Monitoring and Logging

### CloudWatch Setup
```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/ecs/news-analyzer-backend
aws logs create-log-group --log-group-name /aws/ecs/news-analyzer-frontend

# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name NewsAnalyzerDashboard \
  --dashboard-body file://dashboard.json
```

### Health Checks
```python
# backend/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🔒 Security Best Practices

1. **Network Security**
   - Use VPC with private subnets
   - Security groups with minimal access
   - WAF for web application protection

2. **Data Security**
   - Encrypt data at rest and in transit
   - Use IAM roles instead of access keys
   - Regular security updates

3. **Application Security**
   - Input validation
   - Rate limiting
   - CORS configuration

## 💰 Cost Optimization

1. **Right-sizing**
   - Start with smaller instances
   - Use auto-scaling
   - Monitor resource usage

2. **Reserved Instances**
   - Purchase RIs for predictable workloads
   - Use Spot instances for non-critical workloads

3. **Serverless**
   - Use Lambda for variable workloads
   - S3 for static content

## 🚀 Deployment Scripts

### Quick Deploy Script
```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Deploying News Analyzer to AWS..."

# Build images
docker build -f Dockerfile.backend -t news-analyzer-backend .
docker build -f Dockerfile.frontend -t news-analyzer-frontend .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag news-analyzer-backend:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-backend:latest
docker tag news-analyzer-frontend:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-frontend:latest

docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-backend:latest
docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/news-analyzer-frontend:latest

# Update ECS services
aws ecs update-service --cluster news-analyzer-cluster --service news-analyzer-backend --force-new-deployment
aws ecs update-service --cluster news-analyzer-cluster --service news-analyzer-frontend --force-new-deployment

echo "✅ Deployment completed!"
```

## 📝 Next Steps

1. **Choose your deployment option** based on your requirements
2. **Set up AWS CLI** and configure credentials
3. **Create necessary AWS resources** (VPC, security groups, etc.)
4. **Deploy your application** using the chosen method
5. **Configure monitoring** and alerting
6. **Set up CI/CD** pipeline for automated deployments

## 🆘 Troubleshooting

### Common Issues
1. **Database Connection**: Check security groups and network configuration
2. **Container Health**: Verify environment variables and dependencies
3. **Scaling Issues**: Monitor CPU/memory usage and adjust resources

### Useful Commands
```bash
# Check ECS service status
aws ecs describe-services --cluster news-analyzer-cluster --services news-analyzer-backend

# View logs
aws logs tail /ecs/news-analyzer-backend --follow

# Check RDS status
aws rds describe-db-instances --db-instance-identifier news-analyzer-db
```

For more detailed information about any specific deployment option, refer to the AWS documentation or contact your AWS solutions architect. 