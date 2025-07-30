FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
COPY poetry.lock* .

# Install Poetry and dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only=main --no-root

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r sentr && useradd -r -g sentr sentr
RUN chown -R sentr:sentr /app
USER sentr

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "apps.guard.fastapi_app"] 