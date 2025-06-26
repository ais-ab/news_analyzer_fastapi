#!/bin/bash

# CloudFormation Deployment Script for News Analyzer
# This script deploys the complete infrastructure using CloudFormation

set -e

# Configuration
STACK_NAME=${STACK_NAME:-"news-analyzer-stack"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
AWS_REGION=${AWS_REGION:-"us-east-1"}
DOMAIN_NAME=${DOMAIN_NAME:-""}
CERTIFICATE_ARN=${CERTIFICATE_ARN:-""}

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
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check if CloudFormation template exists
    if [ ! -f "aws-cloudformation.yaml" ]; then
        log_error "CloudFormation template 'aws-cloudformation.yaml' not found."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate secure passwords
generate_secrets() {
    log_info "Generating secure secrets..."
    
    # Generate database password
    if [ -z "$DATABASE_PASSWORD" ]; then
        DATABASE_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        log_info "Generated database password"
    fi
    
    # Generate secret key
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
        log_info "Generated secret key"
    fi
    
    # Check for OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        log_warning "OpenAI API key not provided. You'll need to update it later."
        OPENAI_API_KEY="placeholder-key"
    fi
}

# Validate parameters
validate_parameters() {
    log_info "Validating parameters..."
    
    if [ -n "$DOMAIN_NAME" ] && [ -z "$CERTIFICATE_ARN" ]; then
        log_error "Certificate ARN is required when domain name is provided."
        exit 1
    fi
    
    if [ ${#DATABASE_PASSWORD} -lt 8 ]; then
        log_error "Database password must be at least 8 characters long."
        exit 1
    fi
    
    if [ ${#SECRET_KEY} -lt 32 ]; then
        log_error "Secret key must be at least 32 characters long."
        exit 1
    fi
    
    log_success "Parameters validated"
}

# Deploy CloudFormation stack
deploy_stack() {
    log_info "Deploying CloudFormation stack..."
    
    # Prepare parameters
    PARAMETERS="Environment=$ENVIRONMENT"
    PARAMETERS="$PARAMETERS DatabasePassword=$DATABASE_PASSWORD"
    PARAMETERS="$PARAMETERS SecretKey=$SECRET_KEY"
    PARAMETERS="$PARAMETERS OpenAIApiKey=$OPENAI_API_KEY"
    
    if [ -n "$DOMAIN_NAME" ]; then
        PARAMETERS="$PARAMETERS DomainName=$DOMAIN_NAME"
        PARAMETERS="$PARAMETERS CertificateArn=$CERTIFICATE_ARN"
    fi
    
    # Check if stack exists
    if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION &> /dev/null; then
        log_info "Stack exists, updating..."
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://aws-cloudformation.yaml \
            --parameters $PARAMETERS \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $AWS_REGION
        
        log_info "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $AWS_REGION
    else
        log_info "Creating new stack..."
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://aws-cloudformation.yaml \
            --parameters $PARAMETERS \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $AWS_REGION
        
        log_info "Waiting for stack creation to complete..."
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $AWS_REGION
    fi
    
    log_success "CloudFormation stack deployed successfully"
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    # Get ECR repository URIs from CloudFormation outputs
    BACKEND_REPO=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`BackendRepositoryURI`].OutputValue' \
        --output text)
    
    FRONTEND_REPO=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`FrontendRepositoryURI`].OutputValue' \
        --output text)
    
    # Login to ECR
    log_info "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $BACKEND_REPO
    
    # Build and push backend
    log_info "Building and pushing backend image..."
    docker build -f Dockerfile.backend -t news-analyzer-backend .
    docker tag news-analyzer-backend:latest $BACKEND_REPO:latest
    docker push $BACKEND_REPO:latest
    
    # Build and push frontend
    log_info "Building and pushing frontend image..."
    docker build -f Dockerfile.frontend -t news-analyzer-frontend .
    docker tag news-analyzer-frontend:latest $FRONTEND_REPO:latest
    docker push $FRONTEND_REPO:latest
    
    log_success "Docker images built and pushed successfully"
}

# Update ECS services
update_services() {
    log_info "Updating ECS services..."
    
    # Get cluster name from CloudFormation outputs
    CLUSTER_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ClusterName`].OutputValue' \
        --output text)
    
    # Update backend service
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service "${ENVIRONMENT}-news-analyzer-backend" \
        --force-new-deployment \
        --region $AWS_REGION
    
    # Update frontend service
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service "${ENVIRONMENT}-news-analyzer-frontend" \
        --force-new-deployment \
        --region $AWS_REGION
    
    log_success "ECS services updated"
}

# Display deployment information
display_info() {
    log_info "Deployment Information:"
    
    # Get outputs from CloudFormation
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs')
    
    echo ""
    echo "Stack Name: $STACK_NAME"
    echo "Environment: $ENVIRONMENT"
    echo "Region: $AWS_REGION"
    echo ""
    
    # Parse and display outputs
    echo "$OUTPUTS" | jq -r '.[] | "\(.OutputKey): \(.OutputValue)"'
    
    echo ""
    log_warning "Important Notes:"
    echo "1. The application may take a few minutes to be fully available"
    echo "2. Check ECS service status for deployment progress"
    echo "3. Monitor CloudWatch logs for any issues"
    echo "4. Update OpenAI API key in Secrets Manager if using placeholder"
}

# Main deployment function
main() {
    echo "🚀 CloudFormation Deployment for News Analyzer"
    echo "=============================================="
    echo ""
    
    check_prerequisites
    generate_secrets
    validate_parameters
    deploy_stack
    build_and_push_images
    update_services
    display_info
    
    echo ""
    log_success "Deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Wait for ECS services to be stable"
    echo "2. Test the application endpoints"
    echo "3. Set up monitoring and alerting"
    echo "4. Configure CI/CD pipeline"
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --stack-name NAME     CloudFormation stack name (default: news-analyzer-stack)"
    echo "  -e, --environment ENV     Environment name (default: production)"
    echo "  -r, --region REGION       AWS region (default: us-east-1)"
    echo "  -d, --domain DOMAIN       Domain name (optional)"
    echo "  -c, --certificate ARN     SSL certificate ARN (required if domain provided)"
    echo "  -p, --db-password PASS    Database password (auto-generated if not provided)"
    echo "  -k, --secret-key KEY      Secret key (auto-generated if not provided)"
    echo "  -o, --openai-key KEY      OpenAI API key"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  STACK_NAME, ENVIRONMENT, AWS_REGION, DOMAIN_NAME, CERTIFICATE_ARN"
    echo "  DATABASE_PASSWORD, SECRET_KEY, OPENAI_API_KEY"
    echo ""
    echo "Examples:"
    echo "  $0"
    echo "  $0 -e staging -r us-west-2"
    echo "  $0 -d example.com -c arn:aws:acm:us-east-1:123456789012:certificate/xxx"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -d|--domain)
            DOMAIN_NAME="$2"
            shift 2
            ;;
        -c|--certificate)
            CERTIFICATE_ARN="$2"
            shift 2
            ;;
        -p|--db-password)
            DATABASE_PASSWORD="$2"
            shift 2
            ;;
        -k|--secret-key)
            SECRET_KEY="$2"
            shift 2
            ;;
        -o|--openai-key)
            OPENAI_API_KEY="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function
main "$@" 