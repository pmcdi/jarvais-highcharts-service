# Production Deployment Guide

This guide covers deploying the jarvAIs HighCharts Service in a production environment.

## 🔧 Prerequisites

- Docker and Docker Compose
- Redis server (production-grade)
- Load balancer/reverse proxy (Nginx, HAProxy)
- SSL certificates
- Monitoring system (Prometheus, Grafana)

## 🚀 Production Setup

### 1. Environment Configuration

Create a production environment file:

```bash
# .env.production
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_DB=0
SESSION_TTL=3600
FLASK_ENV=production
WORKERS=4
```

### 2. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  jarvais-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PORT=${REDIS_PORT}
      - REDIS_DB=${REDIS_DB}
      - SESSION_TTL=${SESSION_TTL}
    volumes:
      - uploads:/app/uploads
    restart: unless-stopped
    command: [
      "gunicorn",
      "--bind", "0.0.0.0:8000",
      "--workers", "4",
      "--worker-class", "sync",
      "--timeout", "120",
      "--keepalive", "5",
      "--log-level", "info",
      "--access-logfile", "-",
      "--error-logfile", "-",
      "src.app_production:app"
    ]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

volumes:
  uploads:
    driver: local
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/jarvais-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # File upload size
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (bypass rate limiting)
    location /api/v1/health {
        access_log off;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

### 4. Redis Configuration

For production Redis setup:

```bash
# /etc/redis/redis.conf
bind 127.0.0.1
port 6379
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```

### 5. Monitoring Setup

#### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'jarvais-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

#### Log Aggregation

For log management with ELK stack or similar:

```bash
# Add to docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔒 Security Considerations

### 1. Network Security

- Use private networks for internal communication
- Implement firewall rules
- Use VPN for admin access
- Regular security updates

### 2. Application Security

- Regular dependency updates
- Security scanning in CI/CD
- Input validation and sanitization
- Rate limiting and DDoS protection

### 3. Data Security

- Encrypt data at rest and in transit
- Implement proper backup strategies
- Use secrets management systems
- Regular security audits

## 📊 Performance Optimization

### 1. Application Level

```python
# Use connection pooling for Redis
redis_pool = redis.ConnectionPool(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB'],
    max_connections=20
)
redis_client = redis.Redis(connection_pool=redis_pool)
```

### 2. Infrastructure Level

- Use CDN for static assets
- Implement caching strategies
- Database optimization
- Load balancing

## 📊 Monitoring and Alerting

### Key Metrics to Monitor

- Response time
- Error rate
- Memory usage
- CPU utilization
- Redis connection count
- Upload success rate

### Alert Thresholds

- Response time > 5 seconds
- Error rate > 1%
- Memory usage > 80%
- CPU usage > 70%
- Redis connection failures

## 🔄 Backup and Recovery

### 1. Redis Backup

```bash
# Daily backup script
#!/bin/bash
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

### 2. Application Data

```bash
# Backup uploaded files
tar -czf /backup/uploads-$(date +%Y%m%d).tar.gz /app/uploads/
```

## 🛠️ Maintenance

### Regular Tasks

1. **Weekly**:
   - Review logs for errors
   - Check system resources
   - Update dependencies

2. **Monthly**:
   - Security patches
   - Performance review
   - Backup verification

3. **Quarterly**:
   - Security audit
   - Capacity planning
   - Disaster recovery testing

## 🎆 Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Nginx configuration deployed
- [ ] Redis production setup complete
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security hardening applied
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team training completed

## 📞 Support

For production support issues:

1. Check application logs
2. Verify system resources
3. Check Redis connectivity
4. Review monitoring dashboards
5. Contact development team if needed
