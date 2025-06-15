FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install test dependencies for development/testing
ARG INSTALL_TEST_DEPS=false
RUN if [ "$INSTALL_TEST_DEPS" = "true" ]; then pip install --no-cache-dir -r requirements-test.txt; fi

# Copy application code
COPY . /app

# Create uploads directory
RUN mkdir -p /app/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app_production.py
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/health || exit 1

# Run the application
CMD ["python", "src/app_production.py"]