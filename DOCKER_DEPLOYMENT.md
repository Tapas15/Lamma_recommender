# Docker Deployment Guide

This guide explains how to deploy the Job Recommender Application using Docker and Docker Compose.

## Overview

The application is containerized using a multi-stage Docker build that includes:
- **FastAPI Backend** (Python 3.10)
- **Next.js Frontend** (Node.js 18)
- **Nginx Reverse Proxy**
- **MongoDB Database**
- **LibreTranslate Service**
- **Ollama AI Service**
- **Redis Cache** (optional)

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- 10GB free disk space

### For GPU Support (Optional)
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit

## Quick Start

### 1. Clone and Prepare

```bash
git clone <your-repo>
cd job-recommender
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Database
MONGODB_URL=mongodb://mongodb:27017
DATABASE_NAME=job_recommender

# AI Services
OLLAMA_API_BASE=http://ollama:11434
OLLAMA_MODEL=llama3.2
LIBRETRANSLATE_URL=http://libretranslate:5000

# Security
SECRET_KEY=your-super-secret-key-here

# Optional: Redis
REDIS_URL=redis://redis:6379
```

### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Initialize Ollama Model

```bash
# Pull the required model
docker-compose exec ollama ollama pull llama3.2

# Verify model is available
docker-compose exec ollama ollama list
```

## Service Access

Once deployed, the application will be available at:

- **Main Application**: http://localhost (port 80)
- **Next.js Frontend**: http://localhost:3000
- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MongoDB**: localhost:27017
- **LibreTranslate**: http://localhost:5000
- **Ollama**: http://localhost:11434
- **Load Balancer**: http://localhost:8080

## Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Nginx LB      │    │   Main App      │
│   (Port 8080)   │────│   (Port 80)     │
└─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼───┐ ┌───▼───┐ ┌───▼────┐
            │ FastAPI   │ │Next.js│ │ Nginx  │
            │ (8000)    │ │(3000) │ │ Proxy  │
            └───────────┘ └───────┘ └────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───┐   ┌───▼────┐  ┌───▼─────┐
    │MongoDB│   │LibreT. │  │ Ollama  │
    │(27017)│   │(5000)  │  │(11434)  │
    └───────┘   └────────┘  └─────────┘
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://mongodb:27017` |
| `DATABASE_NAME` | Database name | `job_recommender` |
| `OLLAMA_API_BASE` | Ollama API endpoint | `http://ollama:11434` |
| `OLLAMA_MODEL` | AI model to use | `llama3.2` |
| `LIBRETRANSLATE_URL` | Translation service URL | `http://libretranslate:5000` |
| `SECRET_KEY` | JWT secret key | Required |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |

### Volume Mounts

- `mongodb_data`: MongoDB database files
- `ollama_data`: Ollama models and data
- `libretranslate_data`: Translation models
- `app_logs`: Application logs
- `app_data`: Application data

## Management Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f job-recommender
docker-compose logs -f mongodb
docker-compose logs -f ollama
```

### Scale Services
```bash
# Scale the main application
docker-compose up -d --scale job-recommender=3
```

### Update Services
```bash
# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

### Database Management
```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Backup database
docker-compose exec mongodb mongodump --out /data/backup

# Restore database
docker-compose exec mongodb mongorestore /data/backup
```

## Monitoring

### Health Checks

The application includes built-in health checks:

```bash
# Check application health
curl http://localhost/health

# Check individual services
curl http://localhost:8000/health  # FastAPI
curl http://localhost:5000/languages  # LibreTranslate
curl http://localhost:11434/api/tags  # Ollama
```

### Logs

Application logs are stored in the `app_logs` volume:

```bash
# View application logs
docker-compose exec job-recommender tail -f /app/logs/fastapi.log
docker-compose exec job-recommender tail -f /app/logs/nextjs.log
docker-compose exec job-recommender tail -f /app/logs/nginx.log
```

### Resource Usage

```bash
# Check resource usage
docker stats

# Check disk usage
docker system df
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using the ports
   netstat -tulpn | grep :80
   netstat -tulpn | grep :8000
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   # Edit Docker Desktop settings or /etc/docker/daemon.json
   ```

3. **Ollama Model Issues**
   ```bash
   # Pull model manually
   docker-compose exec ollama ollama pull llama3.2
   
   # Check available models
   docker-compose exec ollama ollama list
   ```

4. **Database Connection Issues**
   ```bash
   # Check MongoDB status
   docker-compose exec mongodb mongosh --eval "db.adminCommand('ismaster')"
   ```

### Reset Everything

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Remove all images
docker-compose down --rmi all

# Clean up Docker system
docker system prune -a
```

## Production Deployment

### Security Considerations

1. **Change Default Passwords**
   ```bash
   # Update MongoDB credentials
   MONGO_INITDB_ROOT_USERNAME=your_username
   MONGO_INITDB_ROOT_PASSWORD=your_secure_password
   ```

2. **Use Secrets Management**
   ```bash
   # Use Docker secrets or external secret management
   docker secret create mongodb_password password.txt
   ```

3. **Enable SSL/TLS**
   ```bash
   # Add SSL certificates to nginx configuration
   # Update nginx.conf with SSL settings
   ```

4. **Network Security**
   ```bash
   # Restrict network access
   # Use custom networks with limited exposure
   ```

### Performance Optimization

1. **Resource Limits**
   ```yaml
   # Add to docker-compose.yml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 4G
       reservations:
         cpus: '1.0'
         memory: 2G
   ```

2. **Caching**
   ```bash
   # Enable Redis caching
   # Configure application to use Redis
   ```

3. **Load Balancing**
   ```bash
   # Scale application instances
   docker-compose up -d --scale job-recommender=3
   ```

## Backup and Recovery

### Automated Backups

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec mongodb mongodump --out /data/backup_$DATE
docker-compose exec job-recommender tar -czf /app/data/app_backup_$DATE.tar.gz /app/logs /app/data
```

### Recovery

```bash
# Restore from backup
docker-compose exec mongodb mongorestore /data/backup_YYYYMMDD_HHMMSS
```

## Support

For issues and questions:
1. Check the logs: `docker-compose logs -f`
2. Verify service health: `curl http://localhost/health`
3. Review this documentation
4. Check the main README.md for application-specific help

## License

This Docker configuration is part of the Job Recommender Application project. 