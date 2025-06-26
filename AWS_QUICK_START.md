# AWS Quick Start Guide for News Analyzer

This guide will help you deploy your News Analyzer application to AWS quickly and easily.

## 🚀 Quick Deployment Options

### Option 1: Simple EC2 Deployment (Recommended for beginners)

**Time**: 15-20 minutes
**Cost**: ~$20-30/month
**Complexity**: Low

#### Prerequisites
- AWS Account
- AWS CLI installed and configured
- Domain name (optional)

#### Steps

1. **Launch EC2 Instance**
   ```bash
   # Launch Ubuntu 22.04 LTS instance
   # Instance Type: t3.medium (2 vCPU, 4 GB RAM)
   # Storage: 20 GB GP2
   # Security Groups: SSH (22), HTTP (80), HTTPS (443), Custom (8000)
   ```

2. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Docker and Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Logout and login again
   exit
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

4. **Deploy Application**
   ```bash
   # Clone your repository
   git clone <your-repo-url>
   cd news_analyzer3
   
   # Create environment file
   cat > .env << EOF
   DATABASE_URL=postgresql://news_user:news_password@postgres:5432/news_analyzer
   SECRET_KEY=your-super-secret-key-change-this
   OPENAI_API_KEY=your-openai-api-key
   ENVIRONMENT=production
   EOF
   
   # Start the application
   docker-compose up -d
   ```

5. **Access Your Application**
   - Frontend: `http://your-ec2-ip`
   - Backend API: `http://your-ec2-ip:8000`
   - Health Check: `http://your-ec2-ip:8000/api/health`

### Option 2: Production ECS Deployment (Recommended for production)

**Time**: 30-45 minutes
**Cost**: ~$50-100/month
**Complexity**: Medium

#### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally

#### Steps

1. **Configure AWS CLI**
   ```bash
   aws configure
   # Enter your AWS Access Key ID
   # Enter your AWS Secret Access Key
   # Enter your default region (e.g., us-east-1)
   ```

2. **Run the Deployment Script**
   ```bash
   # Make script executable
   chmod +x aws-deploy.sh
   
   # Run deployment
   ./aws-deploy.sh
   ```

3. **Access Your Application**
   - The script will output the application URL
   - Check ECS console for service status
   - Monitor CloudWatch logs for any issues

### Option 3: CloudFormation Deployment (Most comprehensive)

**Time**: 45-60 minutes
**Cost**: ~$80-150/month
**Complexity**: High

#### Prerequisites
- AWS Account with full permissions
- AWS CLI installed and configured
- Docker installed locally
- Domain name and SSL certificate (optional)

#### Steps

1. **Prepare Your Environment**
   ```bash
   # Set environment variables
   export ENVIRONMENT=production
   export AWS_REGION=us-east-1
   export OPENAI_API_KEY=your-openai-api-key
   
   # Optional: Set domain and certificate
   export DOMAIN_NAME=your-domain.com
   export CERTIFICATE_ARN=arn:aws:acm:us-east-1:123456789012:certificate/xxx
   ```

2. **Deploy Infrastructure**
   ```bash
   # Make script executable
   chmod +x deploy-cloudformation.sh
   
   # Run deployment
   ./deploy-cloudformation.sh
   ```

3. **Access Your Application**
   - The script will output all relevant URLs and endpoints
   - Application will be available at the provided URL
   - SSL certificate will be automatically configured if provided

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Security
SECRET_KEY=your-super-secret-key-at-least-32-characters

# API Keys
OPENAI_API_KEY=your-openai-api-key

# Environment
ENVIRONMENT=production

# Optional
OLLAMA_BASE_URL=http://ollama:11434
REDIS_URL=redis://redis:6379
```

### Security Best Practices

1. **Generate Strong Secrets**
   ```bash
   # Generate secret key
   openssl rand -base64 64 | tr -d "=+/" | cut -c1-50
   
   # Generate database password
   openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
   ```

2. **Use AWS Secrets Manager**
   ```bash
   # Store secrets in AWS Secrets Manager
   aws secretsmanager create-secret \
     --name news-analyzer-secrets \
     --secret-string '{"SECRET_KEY":"your-key","OPENAI_API_KEY":"your-key"}'
   ```

3. **Configure Security Groups**
   - Only allow necessary ports
   - Use private subnets for databases
   - Restrict access to specific IP ranges

## 📊 Monitoring and Logging

### CloudWatch Setup

1. **View Logs**
   ```bash
   # View backend logs
   aws logs tail /ecs/news-analyzer-backend --follow
   
   # View frontend logs
   aws logs tail /ecs/news-analyzer-frontend --follow
   ```

2. **Create Dashboard**
   ```bash
   # Create CloudWatch dashboard
   aws cloudwatch put-dashboard \
     --dashboard-name NewsAnalyzerDashboard \
     --dashboard-body file://dashboard.json
   ```

### Health Checks

Monitor your application health:

```bash
# Check backend health
curl http://your-app-url/api/health

# Check frontend health
curl http://your-app-url/health
```

## 💰 Cost Optimization

### EC2 Deployment
- Use Spot instances for non-critical workloads
- Right-size instances based on usage
- Use reserved instances for predictable workloads

### ECS Deployment
- Use Fargate Spot for cost savings
- Configure auto-scaling based on CPU/memory
- Monitor and adjust resource allocation

### General Tips
- Use CloudWatch to monitor costs
- Set up billing alerts
- Use AWS Cost Explorer for analysis
- Consider using AWS Free Tier for development

## 🚨 Troubleshooting

### Common Issues

1. **Application Not Starting**
   ```bash
   # Check Docker logs
   docker-compose logs backend
   docker-compose logs frontend
   
   # Check ECS service status
   aws ecs describe-services --cluster news-analyzer-cluster --services news-analyzer-backend
   ```

2. **Database Connection Issues**
   ```bash
   # Check database connectivity
   aws rds describe-db-instances --db-instance-identifier news-analyzer-db
   
   # Check security groups
   aws ec2 describe-security-groups --group-ids sg-xxxxx
   ```

3. **Load Balancer Issues**
   ```bash
   # Check target group health
   aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:...
   
   # Check listener rules
   aws elbv2 describe-listeners --load-balancer-arn arn:aws:elasticloadbalancing:...
   ```

### Useful Commands

```bash
# Check ECS cluster status
aws ecs describe-clusters --clusters news-analyzer-cluster

# List running tasks
aws ecs list-tasks --cluster news-analyzer-cluster

# Describe task details
aws ecs describe-tasks --cluster news-analyzer-cluster --tasks task-arn

# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name news-analyzer-stack
```

## 🔄 Updates and Maintenance

### Updating the Application

1. **EC2 Deployment**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Rebuild and restart
   docker-compose down
   docker-compose up -d --build
   ```

2. **ECS Deployment**
   ```bash
   # Build and push new images
   docker build -f Dockerfile.backend -t news-analyzer-backend .
   docker push your-ecr-repo/news-analyzer-backend:latest
   
   # Update service
   aws ecs update-service --cluster news-analyzer-cluster --service news-analyzer-backend --force-new-deployment
   ```

3. **CloudFormation Deployment**
   ```bash
   # Update stack with new template
   ./deploy-cloudformation.sh
   ```

### Backup and Recovery

1. **Database Backup**
   ```bash
   # Create manual snapshot
   aws rds create-db-snapshot \
     --db-instance-identifier news-analyzer-db \
     --db-snapshot-identifier news-analyzer-backup-$(date +%Y%m%d)
   ```

2. **Application Data**
   - Use EBS snapshots for persistent data
   - Configure automated backups
   - Test recovery procedures regularly

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review CloudWatch logs for errors
3. Verify AWS service status
4. Consult AWS documentation
5. Contact AWS support if needed

## 🎯 Next Steps

After successful deployment:

1. **Set up CI/CD pipeline** for automated deployments
2. **Configure monitoring and alerting** for production
3. **Set up SSL certificates** for HTTPS
4. **Configure custom domain** and DNS
5. **Implement backup strategies** for data protection
6. **Set up cost monitoring** and optimization
7. **Plan for scaling** as your application grows

---

**Need Help?** Check the main [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) for detailed information about each deployment option. 