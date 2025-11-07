# Deployment Guide - MusicGen Local

Production deployment instructions for MusicGen Local MVP.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker 20.10+ with Docker Compose
- NVIDIA Docker runtime (for GPU support)
- 8GB+ RAM, 20GB+ storage

### Quick Start
```bash
# Clone and setup
git clone https://github.com/crosspostly/musicgen
cd musicgen
cp .env.example .env

# Edit .env with production values
nano .env

# Deploy
docker-compose up -d

# Monitor
docker-compose logs -f
```

## 🔧 Dockerfiles

### Dockerfile.python (Backend)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY python/ ./python/
COPY models/ ./models/

# Create directories
RUN mkdir -p /app/output /app/logs /app/models/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "python.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.frontend (Static Frontend)
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build frontend
COPY . .
RUN npm run build

# Serve with Python
FROM python:3.9-slim

WORKDIR /app

# Copy built frontend
COPY --from=builder /app/dist ./dist

EXPOSE 3000

CMD ["python", "-m", "http.server", "3000", "--directory", "dist"]
```

## 🔄 Reverse Proxy (Nginx)

### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream python_backend {
        server ai-service:8000;
    }

    upstream frontend {
        server web-service:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # API endpoints (Python FastAPI)
        location /api/ {
            proxy_pass http://python_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # Increase timeout for long operations
            proxy_read_timeout 600s;
            proxy_connect_timeout 600s;
        }

        # Static files
        location /output/ {
            alias /app/output/;
            expires 1d;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### Docker Compose with Nginx
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-service
      - web-service
    restart: unless-stopped

  ai-service:
    # Python FastAPI backend
    build:
      context: .
      dockerfile: Dockerfile.python
    # ... (rest of configuration)

  web-service:
    # Static frontend server
    build:
      context: .
      dockerfile: Dockerfile.frontend
    # ... (rest of configuration)
```

## 🌐 Cloud Deployment

### AWS EC2 + GPU
```bash
# 1. Create EC2 instance with GPU
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type p3.2xlarge \
  --key-name my-key-pair \
  --security-group-ids sg-903004f8

# 2. Install Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker

# 3. Install NVIDIA Docker runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# 4. Deploy application
git clone https://github.com/crosspostly/musicgen
cd musicgen
docker-compose up -d
```

### Google Cloud Platform
```bash
# 1. Create GCE instance with GPU
gcloud compute instances create musicgen-instance \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-k80,count=1

# 2. SSH into instance
gcloud compute ssh musicgen-instance

# 3. Install dependencies
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# 4. Deploy application
git clone https://github.com/crosspostly/musicgen
cd musicgen
docker-compose up -d
```

## 🔒 SSL/TLS Setup

### Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # ... (rest of configuration)
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 🚀 Performance Optimization

### Production Environment Variables
```bash
# Python Backend
MODEL_CACHE_DIR=/app/models/cache
CUDA_VISIBLE_DEVICES=0
REDIS_URL=redis://redis:6379
MAX_CONCURRENT_JOBS=5
JOB_TIMEOUT=300
WORKERS=4

# Frontend (static build)
VITE_API_URL=https://your-domain.com
```

### Docker Resource Limits
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  ai-service:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
    environment:
      - MAX_CONCURRENT_JOBS=5
      - JOB_TIMEOUT=300

  redis:
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru

  web-service:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## 🔧 Maintenance

### Backup Strategy
```bash
#!/bin/bash
# backup.sh

# Backup AI models
tar -czf models-backup-$(date +%Y%m%d).tar.gz ./models/

# Backup Redis data
docker exec musicgen-redis redis-cli BGSAVE
docker cp musicgen-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb

# Backup output files
tar -czf output-backup-$(date +%Y%m%d).tar.gz ./output/

# Upload to cloud storage (optional)
# aws s3 cp ./models-backup-$(date +%Y%m%d).tar.gz s3://musicgen-backups/
```

### Health Checks
```bash
#!/bin/bash
# health-check.sh

# Check Python backend
curl -f http://localhost:8000/health || exit 1

# Check frontend
curl -f http://localhost:3000 || exit 1

# Check Redis
redis-cli ping || exit 1

# Check disk space
df -h | grep -E "/models|/output" | awk '{print $5}' | sed 's/%//' | while read usage; do
    if [ $usage -gt 80 ]; then
        echo "Warning: Disk usage at ${usage}%"
    fi
done
```

## 📊 Monitoring

### Docker Stats
```bash
# Real-time resource monitoring
docker stats

# Check logs
docker-compose logs -f ai-service
docker-compose logs -f web-service
```

### Python Backend Logs
```python
# Add to python/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
```

## 🚨 Troubleshooting

### Common Issues

1. **GPU not detected**: Check NVIDIA drivers and Docker runtime
   ```bash
   nvidia-smi
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

2. **Model download fails**: Verify internet connection and disk space
   ```bash
   df -h
   ping huggingface.co
   ```

3. **Memory errors**: Reduce concurrent jobs or add more RAM
   ```bash
   # Edit .env
   MAX_CONCURRENT_JOBS=2
   ```

4. **Slow generation**: Check GPU utilization
   ```bash
   watch -n 1 nvidia-smi
   ```

### Debug Commands
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs -f ai-service

# Restart services
docker-compose restart

# Access Python backend shell
docker exec -it musicgen-ai bash

# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "DiffRhythm", "prompt": "test", "duration": 30}'

# Redis debugging
redis-cli monitor
redis-cli info memory
```

## 🎯 Production Checklist

- [ ] Environment variables configured (.env)
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured (ports 80, 443)
- [ ] Backup strategy implemented
- [ ] Monitoring and alerts set up
- [ ] Resource limits configured
- [ ] Health checks enabled
- [ ] Log rotation configured
- [ ] GPU drivers installed (if applicable)
- [ ] Domain DNS configured
