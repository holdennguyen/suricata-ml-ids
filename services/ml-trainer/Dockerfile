FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add cache-busting argument to ensure source code is always copied fresh
ARG CACHEBUST=1

# Copy application code (this layer will be rebuilt when CACHEBUST changes)
COPY src/ ./src/

# Create necessary directories
RUN mkdir -p /app/datasets /app/models /app/results /app/config /app/scripts

# Expose health check port
EXPOSE 8002

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV ML_ACCURACY_TARGET=0.90

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')" || exit 1

# Start the service
CMD ["python", "src/main.py"]
