# GUVNL Queue Management System - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Development Setup](#docker-development-setup)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 10GB minimum, 20GB recommended
- **Network:** Stable internet connection for external services

### Software Dependencies
- **Node.js:** 18.x or higher
- **Python:** 3.9 or higher
- **PostgreSQL:** 13 or higher
- **Redis:** 6.x or higher
- **Docker & Docker Compose:** Latest versions (for containerized setup)
- **Git:** For version control

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/guvnl-queue-management.git
cd guvnl-queue-management
```

### 2. Environment Setup

Copy the environment template:
```bash
cp .env.template .env
```

Edit `.env` with your configuration:
```bash
# Database
DATABASE_URL=postgresql://guvnl_user:guvnl_password@localhost:5432/guvnl_queue_db
REDIS_URL=redis://localhost:6379/0

# JWT Secrets (Generate secure keys)
FLASK_SECRET_KEY=your-super-secret-flask-key
JWT_SECRET_KEY=your-super-secret-jwt-key

# Twilio Configuration
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Database Setup

Install and start PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# Download and install from https://www.postgresql.org/download/windows/
```

Create database and user:
```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE guvnl_queue_db;
CREATE USER guvnl_user WITH PASSWORD 'guvnl_password';
GRANT ALL PRIVILEGES ON DATABASE guvnl_queue_db TO guvnl_user;
\q
```

### 4. Redis Setup

Install and start Redis:
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Windows
# Download from https://github.com/microsoftarchive/redis/releases
```

### 5. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python app.py init-db

# Run the application
python app.py
```

Backend will be available at `http://localhost:5000`

### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at `http://localhost:3000`

### 7. Background Tasks Setup

In a new terminal, start Celery worker:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Celery worker
celery -A app.celery worker --loglevel=info

# In another terminal, start Celery beat scheduler
celery -A app.celery beat --loglevel=info
```

## Docker Development Setup

### 1. Prerequisites
- Docker 20.x or higher
- Docker Compose 2.x or higher

### 2. Environment Setup

Copy and configure environment file:
```bash
cp .env.template .env
# Edit .env with your configurations
```

### 3. Start All Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### 4. Initialize Database

```bash
# Run database initialization
docker-compose exec backend python app.py init-db
```

### 5. Access Applications

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Database:** localhost:5432
- **Redis:** localhost:6379
- **Grafana:** http://localhost:3001 (admin/admin)

## Production Deployment

### Option 1: Cloud Provider (Recommended)

#### AWS Deployment

1. **Setup AWS Infrastructure:**
```bash
# Use AWS CDK or CloudFormation
# Example: Create RDS PostgreSQL instance
# Create ElastiCache Redis cluster
# Setup ECS/EKS for containers
# Configure ALB for load balancing
```

2. **Environment Configuration:**
```bash
# Production environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/db
export REDIS_URL=redis://elasticache-endpoint:6379/0
```

3. **Deploy using Docker:**
```bash
# Build and push images to ECR
docker build -t your-registry/guvnl-backend:latest ./backend
docker build -t your-registry/guvnl-frontend:latest ./frontend

docker push your-registry/guvnl-backend:latest
docker push your-registry/guvnl-frontend:latest

# Deploy using docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

#### Google Cloud Platform Deployment

```bash
# Setup GCP project
gcloud config set project your-project-id

# Deploy to Cloud Run
gcloud run deploy guvnl-backend --image gcr.io/your-project/guvnl-backend
gcloud run deploy guvnl-frontend --image gcr.io/your-project/guvnl-frontend
```

### Option 2: VPS/Dedicated Server

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin

# Install Nginx for reverse proxy
sudo apt install nginx

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

#### 2. Production Configuration

Create production environment file:
```bash
# /opt/guvnl/.env.prod
FLASK_ENV=production
DATABASE_URL=postgresql://user:securepass@localhost:5432/guvnl_queue_db
REDIS_URL=redis://:securepass@localhost:6379/0
JWT_SECRET_KEY=super-secure-jwt-key-64-chars-long
FLASK_SECRET_KEY=super-secure-flask-key-64-chars-long
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 3. Nginx Configuration

```nginx
# /etc/nginx/sites-available/guvnl
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /socket.io/ {
        proxy_pass http://localhost:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. Deploy Application

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/your-org/guvnl-queue-management.git
sudo chown -R $USER:$USER guvnl-queue-management
cd guvnl-queue-management

# Copy production environment
cp .env.template .env.prod
# Edit .env.prod with production values

# Start production services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/guvnl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development`/`production` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | JWT token signing key | `secure-random-key-here` |
| `FLASK_SECRET_KEY` | Flask session secret | `secure-random-key-here` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | None |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | None |
| `TWILIO_PHONE_NUMBER` | Twilio Phone Number | None |
| `SMTP_SERVER` | Email SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | Email SMTP port | `587` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

### Generating Secure Keys

```bash
# Generate secure random keys
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Database Setup

### 1. Manual Schema Creation

```bash
# Connect to your database
psql -h localhost -U guvnl_user -d guvnl_queue_db

# Run schema file
\i database/schema.sql

# Run initialization with seed data
\i database/init.sql
```

### 2. Automated Setup (Recommended)

```bash
# Using Flask CLI command
cd backend
python app.py init-db

# Or using Docker
docker-compose exec backend python app.py init-db
```

### 3. Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Generate migration
flask db migrate -m "Add new column"

# Apply migration
flask db upgrade
```

### 4. Backup and Restore

```bash
# Backup
pg_dump -h localhost -U guvnl_user guvnl_queue_db > backup.sql

# Restore
psql -h localhost -U guvnl_user -d guvnl_queue_db < backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U guvnl_user guvnl_queue_db > "backup_$DATE.sql"
```

## Monitoring and Maintenance

### 1. Health Checks

The application includes health check endpoints:

```bash
# Backend health
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### 2. Log Management

```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker

# Log rotation setup (production)
sudo nano /etc/logrotate.d/guvnl
```

Example logrotate configuration:
```
/opt/guvnl-queue-management/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### 3. Performance Monitoring

Use the included Grafana dashboard:

```bash
# Start monitoring stack
docker-compose -f docker-compose.prod.yml up prometheus grafana

# Access Grafana: http://localhost:3001
# Default login: admin/admin123
```

### 4. Database Maintenance

```sql
-- Regular maintenance queries
VACUUM ANALYZE;
REINDEX DATABASE guvnl_queue_db;

-- Check database size
SELECT pg_size_pretty(pg_database_size('guvnl_queue_db'));

-- Monitor active connections
SELECT count(*) FROM pg_stat_activity;
```

### 5. Backup Strategy

Automated backup script:
```bash
#!/bin/bash
# /opt/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="guvnl_queue_db"

# Database backup
pg_dump -h localhost -U guvnl_user $DB_NAME | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Redis backup
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Application files backup
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" /opt/guvnl-queue-management

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup.sh
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
pg_isready -h localhost -p 5432

# Reset password if needed
sudo -u postgres psql -c "ALTER USER guvnl_user PASSWORD 'new_password';"
```

#### 2. Redis Connection Error
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

#### 3. Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 4. Celery Workers Not Starting
```bash
# Check Redis connection
celery -A app.celery inspect ping

# Clear stale locks
celery -A app.celery purge

# Restart workers
pkill -f celery
celery -A app.celery worker --loglevel=info
```

#### 5. SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Test certificate
sudo certbot certificates
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_appointments_user_date ON appointments(user_id, appointment_date);
CREATE INDEX CONCURRENTLY idx_queues_date_status ON queues(queue_date, status);

-- Optimize queries
EXPLAIN ANALYZE SELECT * FROM appointments WHERE user_id = 'uuid';
```

#### 2. Redis Optimization
```bash
# Redis configuration optimizations
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

#### 3. Application Optimization
```bash
# Use production WSGI server
gunicorn --workers 4 --worker-class eventlet app:app

# Enable compression in Nginx
gzip on;
gzip_types text/plain application/json application/javascript text/css;
```

### Security Hardening

#### 1. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

#### 2. Database Security
```sql
-- Revoke public schema privileges
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO guvnl_user;

-- Create read-only user for monitoring
CREATE USER monitor_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE guvnl_queue_db TO monitor_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitor_user;
```

#### 3. Application Security
```bash
# Regular security updates
sudo apt update && sudo apt upgrade

# Keep Docker images updated
docker-compose pull
docker-compose up -d
```

For additional support, please refer to the project documentation or contact the development team.