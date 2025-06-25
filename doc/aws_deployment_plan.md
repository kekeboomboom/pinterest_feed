# Pinterest Feed API - AWS Deployment Plan

## Overview
This deployment plan covers the complete setup for deploying the Pinterest Feed API using:
- **Docker** for containerization
- **GitHub Actions** for CI/CD
- **AWS EC2** for hosting
- **Nginx** as a reverse proxy
- **SQLite** as the database (simplified setup)


## 1. Prerequisites

### AWS EC2 Setup
- [ ] Create an AWS EC2 instance (e.g., Ubuntu 22.04 LTS, `t2.micro` or `t3.small` tier).
- [ ] Create a new key pair during instance launch and download the `.pem` file for SSH access.
- [ ] Configure a Security Group for your instance to allow inbound traffic on:
  - **Port 22 (SSH)** from your IP address for secure access.
  - **Port 80 (HTTP)** from anywhere (`0.0.0.0/0`) for web traffic.
- [ ] Note your instance's Public IPv4 address.

### GitHub Repository Setup
- [ ] Push your code to a GitHub repository.
- [ ] Set up GitHub Actions secrets (listed below).

### Required GitHub Secrets
Add these secrets to your GitHub repository settings under `Settings > Secrets and variables > Actions`:
```
AWS_HOST                 # Your EC2 instance's Public IPv4 address
AWS_USERNAME             # Server username (e.g., 'ubuntu' for Ubuntu AMIs)
AWS_SSH_KEY              # Private SSH key (.pem file contents) for EC2 access
DJANGO_SECRET_KEY        # Django secret key for production
# Pinterest credentials
ACCOUNT                  # Pinterest account email
PASSWORD                 # Pinterest account password
```

### How to Generate Django Secret Key
Run this Python command to generate a secure secret key:
```python
import secrets
print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))
```

## 2. Docker Configuration

The existing Docker configuration is ready for production and requires no changes.

### 2.1 Dockerfile
Your `Dockerfile` is suitable for this deployment.

### 2.2 Docker Compose for Production
Your `docker-compose.prod.yml` is correctly configured.

### 2.3 Production Requirements
Your `requirements.txt` should include `gunicorn`.

```txt
Django>=4.2.0
djangorestframework>=3.14.0
django-crontab>=0.7.1
django-stubs>=4.2.0
requests>=2.31.0
pinterest-dl==0.7.0
python-dotenv==1.0.0

# Production dependencies
gunicorn>=21.2.0
```

## 3. Application Configuration Updates

The existing application configuration is ready and requires no changes.

### 3.1 Production Settings
Your `pinterest_feed/settings_prod.py` is correctly configured for production.

### 3.2 Nginx Configuration
Your `nginx.conf` is correctly set up to work with the Docker environment.

## 4. GitHub Actions CI/CD Pipeline

### 4.1 Main Workflow
Create `.github/workflows/deploy.yml` with the following content. This workflow will run tests and then deploy the application to your EC2 instance on every push to the `main` branch.

```yaml
name: Deploy to AWS EC2

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python3 manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to AWS EC2
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.AWS_HOST }}
        username: ${{ secrets.AWS_USERNAME }}
        key: ${{ secrets.AWS_SSH_KEY }}
        script: |
          cd /app/pinterest_feed
          
          # Pull latest changes
          git pull origin main
          
          # Create environment file
          cat > .env << EOF
          DJANGO_SECRET_KEY=${{ secrets.DJANGO_SECRET_KEY }}
          DJANGO_SETTINGS_MODULE=pinterest_feed.settings_prod
          ACCOUNT=${{ secrets.ACCOUNT }}
          PASSWORD=${{ secrets.PASSWORD }}
          EOF
          
          # Stop existing containers
          docker-compose -f docker-compose.prod.yml down
          
          # Build and start containers
          docker-compose -f docker-compose.prod.yml up -d --build
          
          # Run migrations
          docker-compose -f docker-compose.prod.yml exec -T web python3 manage.py migrate
          
          # Collect static files
          docker-compose -f docker-compose.prod.yml exec -T web python3 manage.py collectstatic --noinput
          
          # Restart services
          docker-compose -f docker-compose.prod.yml restart
```

## 5. Server Setup Steps

### 5.1 Initial Server Configuration
SSH into your AWS EC2 instance. For an Ubuntu AMI, the command will look like this:
`ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_IP`

Then, run the following commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# You may need to log out and log back in for the group change to take effect.
# Or run `newgrp docker`
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install git
sudo apt install git -y

# Create application directory
sudo mkdir -p /app/pinterest_feed
sudo chown $USER:$USER /app/pinterest_feed
cd /app/pinterest_feed

# Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# Create logs directory (if your app needs it)
mkdir -p logs

# Note: Firewall is managed by AWS Security Groups. No 'ufw' commands needed.
```

## 6. Deployment Checklist

### Pre-deployment
- [ ] Create AWS EC2 instance and Security Group.
- [ ] Set up GitHub repository.
- [ ] Add all required secrets to GitHub Actions.
- [ ] Test Docker build locally (`docker-compose -f docker-compose.prod.yml build`).

### Initial Deployment
- [ ] SSH into the EC2 instance and run the server setup script.
- [ ] Push a commit to the `main` branch to trigger the GitHub Actions workflow.
- [ ] Check the Actions tab in GitHub to monitor the deployment.
- [ ] Verify the API is running at `http://YOUR_EC2_IP/api/home_feed`.

### Post-deployment
- [ ] Monitor application logs if needed:
  `docker-compose -f docker-compose.prod.yml logs -f web`

This plan provides a complete roadmap for deploying your Pinterest Feed API to AWS EC2 with automated CI/CD. 
