# jarvAIs HighCharts Service

A production-ready microservice that provides jarvAIs Analyzer results in HighCharts-compatible format. This service includes comprehensive testing, security features, and automated CI/CD workflows.

## 🎆 Features

- **Production-Ready**: Comprehensive error handling, logging, and security headers
- **Redis Support**: Session management with Redis for scalability
- **Comprehensive Testing**: Unit tests, integration tests, and security scans
- **Docker Support**: Full containerization with health checks
- **CI/CD Ready**: GitHub Actions workflow for automated testing
- **Security**: Input validation, security headers, and vulnerability scanning

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Start the services
docker-compose up -d

# Check service health
curl http://localhost:5000/api/v1/health

# Upload a CSV file for analysis
curl -X POST -F "file=@your_data.csv" http://localhost:5000/upload
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (required)
docker run -d -p 6379:6379 redis:7-alpine

# Run the application
python src/app_production.py
```

## 🧪 Testing

### Run All Tests

```bash
# Comprehensive test suite
./run_tests.sh
```

### Individual Test Types

```bash
# Basic structure tests
python test_basic.py

# Unit tests with pytest
pytest -v

# Integration tests with Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🌐 API Endpoints

### Upload Data
```bash
POST /upload
Content-Type: multipart/form-data

# Upload CSV file
curl -X POST -F "file=@data.csv" http://localhost:5000/upload
```

### Get Visualizations
```bash
# Correlation heatmap
GET /visualization/{analyzer_id}/correlation_heatmap?method=pearson

# Frequency heatmap
GET /visualization/{analyzer_id}/frequency_heatmap?column1=category&column2=region

# Pie chart
GET /visualization/{analyzer_id}/pie_chart?var=category
```

### Analyzer Management
```bash
# List analyzers
GET /analyzers

# Get analyzer info
GET /analyzers/{analyzer_id}

# Delete analyzer
DELETE /api/v1/analyzers/{analyzer_id}
```

### Health Check
```bash
GET /api/v1/health
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server host |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `SESSION_TTL` | `3600` | Session TTL in seconds |

### Production Configuration

For production deployment:

1. Use a proper WSGI server (e.g., Gunicorn)
2. Set up Redis with persistence
3. Configure reverse proxy (e.g., Nginx)
4. Set up monitoring and logging
5. Use secrets management for sensitive data

## 🔒 Security Features

- **Input Validation**: UUID validation for analyzer IDs
- **File Type Validation**: Only CSV files accepted
- **Security Headers**: XSS protection, content type sniffing prevention
- **Error Handling**: Secure error messages without information leakage
- **Session Management**: Automatic session expiration

## 📊 CI/CD Pipeline

The project includes a comprehensive GitHub Actions workflow that:

- Runs unit and integration tests
- Performs security scanning with Bandit
- Tests Docker container builds
- Validates Docker Compose configuration
- Generates coverage reports

## 📦 Dependencies

- **Python 3.12+**
- **Flask**: Web framework
- **Redis**: Session storage
- **Pandas**: Data processing
- **jarvAIs**: Data analysis library

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run the test suite: `./run_tests.sh`
4. Submit a pull request

All pull requests must pass the automated test suite before merging.