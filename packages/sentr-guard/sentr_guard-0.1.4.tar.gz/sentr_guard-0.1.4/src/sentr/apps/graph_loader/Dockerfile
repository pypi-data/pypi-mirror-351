FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry files
COPY apps/graph_loader/pyproject.toml apps/graph_loader/poetry.lock* /app/

# Install dependencies
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY apps/__init__.py /app/apps/
COPY apps/graph_loader/ /app/apps/graph_loader/

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8083/health || exit 1

# Expose health check port
EXPOSE 8083

# Run the service
CMD ["poetry", "run", "python", "-m", "apps.graph_loader.main"]
