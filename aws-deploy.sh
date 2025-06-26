#!/bin/bash

# AWS Deployment Script for News Analyzer
# This script automates the deployment process to AWS

set -e

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
AWS_ACCOUNT=${AWS_ACCOUNT:-""}
CLUSTER_NAME=${CLUSTER_NAME:-"news-analyzer-cluster"}
BACKEND_SERVICE=${BACKEND_SERVICE:-"news-analyzer-backend"}
FRONTEND_SERVICE=${FRONTEND_SERVICE:-"news-analyzer-frontend"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Get AWS account ID if not provided
    if [ -z "$AWS_ACCOUNT" ]; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        log_info "Using AWS Account: $AWS_ACCOUNT"
    fi
    
    log_success "Prerequisites check passed"
}

# Create ECR repositories
create_ecr_repositories() {
    log_info "Creating ECR repositories..."
    
    # Create backend repository
    if ! aws ecr describe-repositories --repository-names news-analyzer-backend --region $AWS_REGION &> /dev/null; then
        aws ecr create-repository --repository-name news-analyzer-backend --region $AWS_REGION
        log_success "Created ECR repository: news-analyzer-backend"
    else
        log_info "ECR repository news-analyzer-backend already exists"
    fi
    
    # Create frontend repository
    if ! aws ecr describe-repositories --repository-names news-analyzer-frontend --region $AWS_REGION &> /dev/null; then
        aws ecr create-repository --repository-name news-analyzer-frontend --region $AWS_REGION
        log_success "Created ECR repository: news-analyzer-frontend"
    else
        log_info "ECR repository news-analyzer-frontend already exists"
    fi
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    # Login to ECR
    log_info "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build backend image
    log_info "Building backend image..."
    docker build -f Dockerfile.backend -t news-analyzer-backend .
    docker tag news-analyzer-backend:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/news-analyzer-backend:latest
    docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/news-analyzer-backend:latest
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -f Dockerfile.frontend -t news-analyzer-frontend .
    docker tag news-analyzer-frontend:latest $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/news-analyzer-frontend:latest
    docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/news-analyzer-frontend:latest
    
    log_success "Images built and pushed successfully"
}

# Create ECS cluster
create_ecs_cluster() {
    log_info "Creating ECS cluster..."
    
    if ! aws ecs describe-clusters --clusters $CLUSTER_NAME --region $AWS_REGION --query 'clusters[0].status' --output text 2>/dev/null | grep -q ACTIVE; then
        aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION
        log_success "Created ECS cluster: $CLUSTER_NAME"
    else
        log_info "ECS cluster $CLUSTER_NAME already exists"
    fi
}

# Create task definitions
create_task_definitions() {
    log_info "Creating task definitions..."
    
    # Backend task definition
    cat > backend-task-definition.json << EOF
{
  "family": "news-analyzer-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/news-analyzer-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://news_user:news_password@localhost:5432/news_analyzer"
        },
        {
          "name": "SECRET_KEY",
          "value": "your-secret-key-change-this"
        },
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/news-analyzer-backend",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF
    
    # Frontend task definition
    cat > frontend-task-definition.json << EOF
{
  "family": "news-analyzer-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/news-analyzer-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/news-analyzer-frontend",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF
    
    # Register task definitions
    aws ecs register-task-definition --cli-input-json file://backend-task-definition.json --region $AWS_REGION
    aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json --region $AWS_REGION
    
    log_success "Task definitions created successfully"
}

# Create log groups
create_log_groups() {
    log_info "Creating CloudWatch log groups..."
    
    # Create backend log group
    if ! aws logs describe-log-groups --log-group-name-prefix "/ecs/news-analyzer-backend" --region $AWS_REGION --query 'logGroups[0].logGroupName' --output text 2>/dev/null | grep -q "/ecs/news-analyzer-backend"; then
        aws logs create-log-group --log-group-name "/ecs/news-analyzer-backend" --region $AWS_REGION
        log_success "Created log group: /ecs/news-analyzer-backend"
    else
        log_info "Log group /ecs/news-analyzer-backend already exists"
    fi
    
    # Create frontend log group
    if ! aws logs describe-log-groups --log-group-name-prefix "/ecs/news-analyzer-frontend" --region $AWS_REGION --query 'logGroups[0].logGroupName' --output text 2>/dev/null | grep -q "/ecs/news-analyzer-frontend"; then
        aws logs create-log-group --log-group-name "/ecs/news-analyzer-frontend" --region $AWS_REGION
        log_success "Created log group: /ecs/news-analyzer-frontend"
    else
        log_info "Log group /ecs/news-analyzer-frontend already exists"
    fi
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    # Get default VPC and subnets
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION)
    SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region $AWS_REGION | tr '\t' ',' | sed 's/,$//')
    
    # Create security group if it doesn't exist
    SG_NAME="news-analyzer-sg"
    SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --query 'SecurityGroups[0].GroupId' --output text --region $AWS_REGION 2>/dev/null)
    
    if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
        SG_ID=$(aws ec2 create-security-group --group-name $SG_NAME --description "Security group for News Analyzer" --vpc-id $VPC_ID --region $AWS_REGION --query 'GroupId' --output text)
        
        # Add inbound rules
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWS_REGION
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWS_REGION
        
        log_success "Created security group: $SG_ID"
    else
        log_info "Security group $SG_NAME already exists: $SG_ID"
    fi
    
    # Deploy backend service
    if ! aws ecs describe-services --cluster $CLUSTER_NAME --services $BACKEND_SERVICE --region $AWS_REGION --query 'services[0].status' --output text 2>/dev/null | grep -q ACTIVE; then
        aws ecs create-service \
          --cluster $CLUSTER_NAME \
          --service-name $BACKEND_SERVICE \
          --task-definition news-analyzer-backend:1 \
          --desired-count 1 \
          --launch-type FARGATE \
          --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
          --region $AWS_REGION
        
        log_success "Created backend service: $BACKEND_SERVICE"
    else
        log_info "Backend service $BACKEND_SERVICE already exists, updating..."
        aws ecs update-service --cluster $CLUSTER_NAME --service $BACKEND_SERVICE --task-definition news-analyzer-backend --region $AWS_REGION
    fi
    
    # Deploy frontend service
    if ! aws ecs describe-services --cluster $CLUSTER_NAME --services $FRONTEND_SERVICE --region $AWS_REGION --query 'services[0].status' --output text 2>/dev/null | grep -q ACTIVE; then
        aws ecs create-service \
          --cluster $CLUSTER_NAME \
          --service-name $FRONTEND_SERVICE \
          --task-definition news-analyzer-frontend:1 \
          --desired-count 1 \
          --launch-type FARGATE \
          --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
          --region $AWS_REGION
        
        log_success "Created frontend service: $FRONTEND_SERVICE"
    else
        log_info "Frontend service $FRONTEND_SERVICE already exists, updating..."
        aws ecs update-service --cluster $CLUSTER_NAME --service $FRONTEND_SERVICE --task-definition news-analyzer-frontend --region $AWS_REGION
    fi
}

# Wait for services to be stable
wait_for_services() {
    log_info "Waiting for services to be stable..."
    
    aws ecs wait services-stable --cluster $CLUSTER_NAME --services $BACKEND_SERVICE --region $AWS_REGION
    aws ecs wait services-stable --cluster $CLUSTER_NAME --services $FRONTEND_SERVICE --region $AWS_REGION
    
    log_success "Services are now stable"
}

# Display service information
display_service_info() {
    log_info "Service Information:"
    
    echo "ECS Cluster: $CLUSTER_NAME"
    echo "Region: $AWS_REGION"
    echo ""
    
    # Get service details
    BACKEND_TASKS=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $BACKEND_SERVICE --region $AWS_REGION --query 'taskArns' --output text)
    FRONTEND_TASKS=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $FRONTEND_SERVICE --region $AWS_REGION --query 'taskArns' --output text)
    
    if [ ! -z "$BACKEND_TASKS" ]; then
        BACKEND_IP=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $BACKEND_TASKS --region $AWS_REGION --query 'tasks[0].attachments[0].details[?name==`privateIPv4Address`].value' --output text)
        echo "Backend Service: $BACKEND_SERVICE"
        echo "Backend IP: $BACKEND_IP:8000"
        echo "Backend Health: http://$BACKEND_IP:8000/api/health"
    fi
    
    if [ ! -z "$FRONTEND_TASKS" ]; then
        FRONTEND_IP=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $FRONTEND_TASKS --region $AWS_REGION --query 'tasks[0].attachments[0].details[?name==`privateIPv4Address`].value' --output text)
        echo "Frontend Service: $FRONTEND_SERVICE"
        echo "Frontend IP: $FRONTEND_IP:80"
        echo "Frontend URL: http://$FRONTEND_IP"
    fi
    
    echo ""
    log_warning "Note: These are private IPs. You'll need to set up a load balancer or use public subnets for external access."
}

# Cleanup temporary files
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f backend-task-definition.json frontend-task-definition.json
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    echo "🚀 AWS Deployment Script for News Analyzer"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    create_ecr_repositories
    build_and_push_images
    create_ecs_cluster
    create_log_groups
    create_task_definitions
    deploy_services
    wait_for_services
    display_service_info
    cleanup
    
    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Set up a load balancer for external access"
    echo "2. Configure your domain name"
    echo "3. Set up monitoring and alerting"
    echo "4. Configure SSL certificates"
}

# Run main function
main "$@" 