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

### Production Docker Compose
```yaml
version: '3.8'

services:
  ai-service:
    build:
      context: .
      dockerfile: Dockerfile.python
    container_name: musicgen-ai
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - MODEL_CACHE_DIR=/app/models/cache
      - CUDA_VISIBLE_DEVICES=0
      - REDIS_URL=redis://redis:6379
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  web-service:
    build:
      context: .
      dockerfile: Dockerfile.node
    container_name: musicgen-web
    ports:
      - "3000:3000"
    depends_on:
      ai-service:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - AI_SERVICE_URL=http://ai-service:8000
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./output:/app/output
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: musicgen-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis-data:
    driver: local
```

## 🔧 Dockerfiles

### Dockerfile.python
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
COPY backend/ ./backend/
COPY ai-engines/ ./ai-engines/
COPY models/ ./models/

# Create directories
RUN mkdir -p /app/output /app/logs /app/models/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.node
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Application code
COPY frontend/ ./frontend/
COPY public/ ./public/

# Build frontend
RUN cd frontend && npm run build

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000

CMD ["npm", "run", "start"]
```

## 🌐 Cloud Deployment

### AWS EC2 + ECS
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

# 3. Deploy application
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

# 2. Install NVIDIA drivers
curl -O https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda-repo-ubuntu2004-12-2-local_12.2.0-535.54.03-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-12-2-local_12.2.0-535.54.03-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-2

# 3. Deploy application
git clone https://github.com/crosspostly/musicgen
cd musicgen
docker-compose up -d
```

## 🔄 Reverse Proxy (Nginx)

### nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream ai_service {
        server ai-service:8000;
    }

    upstream web_service {
        server web-service:3000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Frontend
        location / {
            proxy_pass http://web_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # API endpoints
        location /api/ {
            proxy_pass http://ai_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            
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
    # ... (same as above)

  web-service:
    # ... (same as above)
```

## 📊 Monitoring & Logging

### Prometheus + Grafana
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana-data:
```

### Log Aggregation (ELK Stack)
```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  elasticsearch-data:
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

### Production Tuning
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
          memory: 2G
          cpus: '1.0'
```

### Database Optimization
```bash
# Redis persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# Memory management
redis-cli CONFIG SET maxmemory 1gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🔧 Maintenance

### Backup Strategy
```bash
#!/bin/bash
# backup.sh

# Backup models
tar -czf models-backup-$(date +%Y%m%d).tar.gz ./models/

# Backup Redis data
docker exec musicgen-redis redis-cli BGSAVE
docker cp musicgen-redis:/data/dump.rdb ./redis-backup-$(date +%Y%m%d).rdb

# Backup output files
tar -czf output-backup-$(date +%Y%m%d).tar.gz ./output/

# Upload to cloud storage
aws s3 cp ./models-backup-$(date +%Y%m%d).tar.gz s3://musicgen-backups/
```

### Health Checks
```bash
#!/bin/bash
# health-check.sh

# Check services
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000 || exit 1
redis-cli ping || exit 1

# Check disk space
df -h | grep -E "/models|/output" | awk '{print $5}' | sed 's/%//' | while read usage; do
    if [ $usage -gt 80 ]; then
        echo "Warning: Disk usage at ${usage}%"
    fi
done
```

## 🚨 Troubleshooting

### Common Issues
1. **GPU not detected**: Check NVIDIA drivers and Docker runtime
2. **Model download fails**: Verify internet connection and disk space
3. **Memory errors**: Reduce concurrent jobs or add more RAM
4. **Slow generation**: Check GPU utilization and model caching

### Debug Commands
```bash
# Check service logs
docker-compose logs -f ai-service
docker-compose logs -f web-service

# Monitor resources
docker stats
htop
nvidia-smi

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:3000

# Redis debugging
redis-cli monitor
redis-cli info memory
```