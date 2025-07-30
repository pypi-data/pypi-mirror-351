# Dockerfile for sentr-api
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

# Default command
CMD ["python", "apps/api/main.py"]
