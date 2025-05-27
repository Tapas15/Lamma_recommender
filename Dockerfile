# Multi-stage Dockerfile for Job Recommender Application
# This Dockerfile builds both the FastAPI backend and Next.js frontend

# Stage 1: Build Next.js Frontend
FROM node:18-alpine AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy package files
COPY frontend/lnd-nexus/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/lnd-nexus/ ./

# Build the Next.js application
RUN npm run build

# Stage 2: Python Backend Setup
FROM python:3.10-slim AS backend-builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Production Image
FROM python:3.10-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NODE_ENV=production

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    nginx \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/.next /app/frontend/lnd-nexus/.next
COPY --from=frontend-builder /app/frontend/public /app/frontend/lnd-nexus/public
COPY --from=frontend-builder /app/frontend/package*.json /app/frontend/lnd-nexus/
COPY --from=frontend-builder /app/frontend/next.config.ts /app/frontend/lnd-nexus/

# Install only production dependencies for Next.js
WORKDIR /app/frontend/lnd-nexus
RUN npm ci --only=production && npm cache clean --force

# Copy application code
WORKDIR /app
COPY . .

# Copy frontend source files needed for runtime
COPY frontend/lnd-nexus/app /app/frontend/lnd-nexus/app
COPY frontend/lnd-nexus/scripts /app/frontend/lnd-nexus/scripts

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Copy configuration files
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Change ownership to app user
RUN chown -R app:app /app

# Create .env file with default values if it doesn't exist
RUN if [ ! -f /app/.env ]; then \
    echo "OLLAMA_API_BASE=http://localhost:11434" > /app/.env && \
    echo "OLLAMA_MODEL=llama3.2" >> /app/.env && \
    echo "SECRET_KEY=your-secret-key-here" >> /app/.env && \
    echo "MONGODB_URL=mongodb://localhost:27017" >> /app/.env && \
    echo "DATABASE_NAME=job_recommender" >> /app/.env && \
    echo "LIBRETRANSLATE_URL=http://localhost:5000" >> /app/.env; \
    fi

# Expose ports
EXPOSE 80 3000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to app user
USER app

# Start the application
CMD ["/app/start.sh"] 