FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    build-essential \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install pixi
RUN curl -fsSL https://pixi.sh/install.sh | bash
ENV PATH="/root/.pixi/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy pixi configuration files
COPY pixi.toml pixi.lock* ./

# Install dependencies using pixi
RUN pixi install

# Copy application source code
COPY src/ ./src/

# Copy startup script
COPY run_fastapi.py ./

# Create uploads directory if it doesn't exist
RUN mkdir -p uploads

# Expose the port that FastAPI runs on
EXPOSE 5000

# Set default environment variables
ENV APP_FILE=main_production
ENV APP_NAME=app
ENV HOST=0.0.0.0
ENV PORT=5000
ENV LOG_LEVEL=info

# Use pixi to run the FastAPI application
CMD ["pixi", "run", "prod"]