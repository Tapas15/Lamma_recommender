#!/bin/bash

# Job Recommender Application Startup Script
# This script initializes the application and starts all services

set -e

echo "Starting Job Recommender Application..."

# Create log directory if it doesn't exist
mkdir -p /app/logs

# Set proper permissions
chown -R app:app /app/logs

# Initialize database if needed
echo "Checking database initialization..."
if [ -f "/app/backend/init_db.py" ]; then
    echo "Initializing database..."
    cd /app
    python backend/init_db.py || echo "Database initialization failed or already completed"
fi

# Check if .env file exists and has required variables
if [ ! -f "/app/.env" ]; then
    echo "Creating default .env file..."
    cat > /app/.env << EOF
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama3.2
SECRET_KEY=docker-secret-key-$(date +%s)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=job_recommender
LIBRETRANSLATE_URL=http://localhost:5000
EOF
fi

# Source environment variables
export $(grep -v '^#' /app/.env | xargs)

# Wait for external services (if needed)
echo "Checking external service dependencies..."

# Check if MongoDB is accessible (optional)
if [ ! -z "$MONGODB_URL" ] && [ "$MONGODB_URL" != "mongodb://localhost:27017" ]; then
    echo "Waiting for MongoDB to be accessible..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if python -c "
import pymongo
import sys
try:
    client = pymongo.MongoClient('$MONGODB_URL', serverSelectionTimeoutMS=5000)
    client.server_info()
    print('MongoDB is accessible')
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; then
            echo "MongoDB is ready"
            break
        fi
        echo "Waiting for MongoDB... ($timeout seconds remaining)"
        sleep 2
        timeout=$((timeout-2))
    done
fi

# Ensure Next.js build exists
if [ ! -d "/app/frontend/lnd-nexus/.next" ]; then
    echo "Next.js build not found, building..."
    cd /app/frontend/lnd-nexus
    npm run build
fi

# Create nginx directories
mkdir -p /var/log/nginx
mkdir -p /var/lib/nginx/body
mkdir -p /var/lib/nginx/fastcgi
mkdir -p /var/lib/nginx/proxy
mkdir -p /var/lib/nginx/scgi
mkdir -p /var/lib/nginx/uwsgi

# Test nginx configuration
nginx -t

echo "Starting services with Supervisor..."

# Start supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 