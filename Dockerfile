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

# Copy previously uploaded datasets
COPY uploads/ ./uploads/

# Expose the port that Flask runs on
EXPOSE 5000

# Use pixi to run the application
CMD ["/bin/bash"]