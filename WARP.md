# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Quick Start Commands

### Development Server
```bash
# Start development server with debug logging (PORT=8888 by default in pixi.toml)
pixi run dev

# Development server with auto-reload enabled
pixi run dev-reload

# Production server mode
pixi run prod
```

### Testing
```bash
# Run the test suite
pixi run test

# The test suite includes basic API endpoint checks and plot generation tests
python tests/test_fastapi.py
```

### Docker Commands
```bash
# Build the Docker image
docker build -t jarvais-api:latest .

# Run with Docker Compose (includes Redis)
docker compose up

# The Docker setup runs on PORT=5000 and uses Redis for storage
```

### Environment Setup
```bash
# Install pixi if not already installed
curl -fsSL https://pixi.sh/install.sh | bash

# Install project dependencies
pixi install

# Enter the pixi shell for direct command execution
pixi shell
```

## Architecture Overview

This is a FastAPI-based microservice that provides Highcharts-compatible data visualization for jarvAIs Analyzer results. The service follows a modular router-based architecture:

### Core Components

1. **Router Organization** (`src/routers/`):
   - `upload.py`: CSV file upload and Analyzer creation
   - `visualization.py`: All chart generation endpoints (heatmaps, pie charts, UMAP, box/violin plots)
   - `analyzers.py`: Analyzer management (list, get, delete)
   - `health.py`: Health check endpoint

2. **Storage Abstraction** (`src/storage.py`):
   - Implements a storage manager with automatic fallback mechanism
   - Primary: Redis storage with configurable TTL (default 3600 seconds)
   - Fallback: In-memory storage when Redis is unavailable
   - Storage backend is determined at startup and logged

3. **Configuration System** (`src/config.py`):
   - Pydantic-based settings management
   - Environment variables override defaults
   - Production mode toggle affects middleware and rate limiting

4. **Visualization Generation** (`src/plot/`):
   - Each visualization type has its own module
   - Returns Highcharts-compatible JSON structures
   - Supports correlation heatmaps, frequency heatmaps, pie charts, UMAP scatterplots, violin plots, and box plots

## Key Technical Details

### Port Configuration Discrepancy
- **pixi.toml defaults**: PORT=8888, HOST=localhost
- **README/Docker defaults**: PORT=5000, HOST=0.0.0.0
- Always check which port is actually being used when running locally

### Data Processing Pipeline
1. CSV upload automatically drops UID columns (columns where unique values = row count)
2. UMAP projection is computed during upload for continuous variables
3. UMAP data is stored as part of the Analyzer instance (hack to enable Redis serialization)
4. Analyzer instances are stored with configurable TTL (SESSION_TTL environment variable)

### Production vs Development Modes
- **Development** (default):
  - No rate limiting
  - Simplified logging format
  - Auto-reload available via RELOAD=true
  
- **Production** (PRODUCTION=true):
  - Rate limiting enabled via slowapi
  - Trusted host middleware activated if TRUSTED_HOSTS is set
  - Full timestamp logging format
  - Different rate limits for upload (10/min), visualization (30/min), general (60/min)

### Storage Behavior
- Storage manager checks Redis availability at startup
- Automatic fallback to memory storage if Redis connection fails
- Health endpoint reports current storage type and Redis connection status
- Analyzer IDs are UUIDs generated during upload

## API Endpoint Reference

### File Upload
- `POST /upload` - Upload CSV and create analyzer
  - Returns: analyzer_id, file info, detected variable types

### Visualization Endpoints
All visualization endpoints follow the pattern: `/visualization/{analyzer_id}/{chart_type}`

Required parameters for each visualization:
- **correlation_heatmap**: `method` (optional, default="pearson")
- **frequency_heatmap**: `column1`, `column2` (both categorical)
- **pie_chart**: `var` (variable to plot)
- **umap_scatterplot**: `hue` (optional, for color coding)
- **violin_plot**: `var_categorical`, `var_continuous`
- **box_plot**: `var_categorical`, `var_continuous`

### Analyzer Management
- `GET /analyzers` - List all analyzer IDs
- `GET /analyzers/{analyzer_id}` - Get analyzer details
- `DELETE /analyzers/{analyzer_id}` - Delete analyzer

### Documentation
- Interactive API docs: `http://localhost:{PORT}/docs`
- Alternative docs: `http://localhost:{PORT}/redoc`

## Non-Obvious Implementation Notes

1. **UMAP Computation**: UMAP is computed during upload, not on-demand. This is intentional to allow UMAP data to be serialized and stored in Redis with the Analyzer instance.

2. **File Size Limits**: Only enforced in production mode (MAX_CONTENT_LENGTH, default 100MB).

3. **CORS Configuration**: Default allows all origins (`*`). Configure ALLOWED_ORIGINS for production deployments.

4. **Redis Key Format**: Analyzer instances are stored with the prefix `analyzer:` followed by the UUID.

5. **Test Suite**: The test_fastapi.py is a simple HTTP-based test that requires the server to be running. It's not a unit test suite but rather an integration test.

6. **Session Expiry**: Analyzers expire after SESSION_TTL seconds (default 3600). The expiry time is included in the upload response.

7. **Grouped Box Plot**: Currently commented out in the visualization router but implementation exists.

## Environment Variables

Key environment variables that affect behavior:
- `PRODUCTION`: Enables production mode features
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`: Redis connection
- `SESSION_TTL`: Analyzer lifetime in seconds
- `PORT`, `HOST`: Server binding
- `LOG_LEVEL`: Logging verbosity
- `RELOAD`: Enable auto-reload for development
- `ALLOWED_ORIGINS`: CORS allowed origins (comma-separated)
- `TRUSTED_HOSTS`: Trusted host middleware (production only)
