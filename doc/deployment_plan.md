# Pinterest Feed API - Deployment Plan

## Overview
This deployment plan covers the complete setup for deploying the Pinterest Feed API using:
- **Docker** for containerization
- **GitHub Actions** for CI/CD
- **DigitalOcean** for hosting
- **Nginx** as reverse proxy
- **SQLite** as database (simplified setup)


## 1. Prerequisites

### DigitalOcean Setup
- [ ] Create a DigitalOcean droplet (Ubuntu 22.04 LTS, minimum 2GB RAM)
- [ ] Set up SSH key access
- [ ] Note your droplet IP address (no domain needed)
- [ ] Install Docker and Docker Compose on the server

### GitHub Repository Setup
- [ ] Push your code to GitHub repository
- [ ] Set up GitHub Actions secrets (listed below)

### Required GitHub Secrets
Add these secrets to your GitHub repository:
```
DIGITALOCEAN_HOST          # Your server IP address
DIGITALOCEAN_USERNAME      # Server username (usually 'root')
DIGITALOCEAN_SSH_KEY       # Private SSH key for server access
DJANGO_SECRET_KEY          # Django secret key for production
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

### 2.1 Dockerfile
Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for database and logs
RUN mkdir -p /app/db /app/logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Note: Static files will be collected during deployment

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "pinterest_feed.wsgi:application"]
```

### 2.2 Docker Compose for Production
Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    environment:
      - DEBUG=False
      - SECRET_KEY=${DJANGO_SECRET_KEY}
      - ALLOWED_HOSTS="*"
      - DJANGO_SETTINGS_MODULE=pinterest_feed.settings_prod
      - ACCOUNT=${ACCOUNT}
      - PASSWORD=${PASSWORD}
    volumes:
      - sqlite_data:/app/db
      - static_volume:/app/staticfiles
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
    depends_on:
      - web
    restart: unless-stopped
    networks:
      - app-network

volumes:
  sqlite_data:
  static_volume:

networks:
  app-network:
    driver: bridge
```

### 2.3 Production Requirements
Update `requirements.txt` to include production dependencies:

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

### 3.1 Production Settings
Create `pinterest_feed/settings_prod.py`:

```python
from .settings import *
import os
from urllib.parse import urlparse

# Production settings
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# Allowed hosts - Allow all hosts for IP-based access
ALLOWED_HOSTS = ['*']

# Database - Using SQLite with persistent storage
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/app/db/db.sqlite3',
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Basic security settings (HTTP only)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}
```

### 3.2 Nginx Configuration
Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://django;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Host $host;
            proxy_redirect off;
        }

        location /static/ {
            alias /app/staticfiles/;
        }
    }
}
```

## 4. GitHub Actions CI/CD Pipeline

### 4.1 Main Workflow
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to DigitalOcean

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
        python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to DigitalOcean
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.DIGITALOCEAN_HOST }}
        username: ${{ secrets.DIGITALOCEAN_USERNAME }}
        key: ${{ secrets.DIGITALOCEAN_SSH_KEY }}
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
          docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate
          
          # Collect static files
          docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
          
          # Restart services
          docker-compose -f docker-compose.prod.yml restart
```

## 5. Server Setup Steps

### 5.1 Initial Server Configuration
SSH into your DigitalOcean droplet and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /app/pinterest_feed
sudo chown $USER:$USER /app/pinterest_feed
cd /app/pinterest_feed

# Clone repository
git clone https://github.com/YOUR_USERNAME/pinterest_feed.git .

# Create logs directory
mkdir -p logs

# Set up firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw enable
```

## 6. Environment Variables Setup

### 6.1 Production Environment File
Create `.env` file on your server:

```bash
# Django
DJANGO_SECRET_KEY=your_secret_key_here
DJANGO_SETTINGS_MODULE=pinterest_feed.settings_prod
ACCOUNT=<your_pinterest_email>
PASSWORD=<your_pinterest_password>
```

## 7. Deployment Checklist

### Pre-deployment
- [ ] Create DigitalOcean droplet
- [ ] Set up GitHub repository
- [ ] Add all required GitHub secrets
- [ ] Test Docker build locally

### Initial Deployment
- [ ] Set up server environment
- [ ] Clone repository to server
- [ ] Configure environment variables
- [ ] Deploy via GitHub Actions
- [ ] Run database migrations
- [ ] Test API endpoints at http://YOUR_IP/api/home_feed

### Post-deployment
- [ ] Test API functionality

This deployment plan provides a simple, efficient solution for your Pinterest Feed API with automated CI/CD and HTTP access via IP address. The API will be accessible at `http://YOUR_DROPLET_IP/api/home_feed`. 
