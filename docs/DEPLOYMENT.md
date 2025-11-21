# Deployment Guide

This document describes how to deploy Gherkin Taster to production.

## Prerequisites

- Docker and Docker Compose installed
- GitHub repository with feature files
- Linear workspace with configured teams
- Domain name with SSL certificate (optional)

## Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure required environment variables:
   ```bash
   LINEAR_API_TOKEN=lin_api_xxx        # Linear API token
   GITHUB_API_TOKEN=ghp_xxx            # GitHub personal access token
   REDIS_URL=redis://redis:6379/0      # Redis connection (Docker)
   SESSION_TTL=86400                    # Session expiry (24 hours)
   EDIT_LOCK_TTL=1800                   # Edit lock expiry (30 minutes)
   ```

3. Optional: Configure LLM for AI-generated commit messages:
   ```bash
   LLM_API_KEY=sk-xxx                   # Anthropic API key (optional)
   ```

## Docker Deployment

### Development

```bash
# Build and start services
docker-compose up --build

# Access application
open http://localhost:8100
```

### Production

1. Create production compose file `docker-compose.prod.yml`:
   ```yaml
   version: '3.8'

   services:
     gherkin-web:
       build:
         context: .
         dockerfile: Dockerfile
       restart: always
       ports:
         - "8100:8000"
       environment:
         - LINEAR_API_TOKEN=${LINEAR_API_TOKEN}
         - GITHUB_API_TOKEN=${GITHUB_API_TOKEN}
         - REDIS_URL=redis://gherkin-redis:6379/0
       depends_on:
         - gherkin-redis
       networks:
         - gherkin-network
         - buckler-shared

     gherkin-redis:
       image: redis:7-alpine
       restart: always
       volumes:
         - redis-data:/data
       networks:
         - gherkin-network

   volumes:
     redis-data:

   networks:
     gherkin-network:
     buckler-shared:
       external: true
       name: buckler_ai_shared_network
   ```

2. Deploy:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. Check logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f gherkin-web
   ```

## Reverse Proxy (Nginx)

Configure Nginx to proxy requests to Gherkin Taster:

```nginx
server {
    listen 443 ssl;
    server_name gherkin.buckler.ai;

    ssl_certificate /etc/ssl/certs/buckler.crt;
    ssl_certificate_key /etc/ssl/private/buckler.key;

    location / {
        proxy_pass http://localhost:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Health Checks

Monitor application health:

```bash
# Check web service
curl http://localhost:8100/health

# Check Redis
docker exec gherkin-redis redis-cli ping
```

## Backup and Recovery

### Redis Data Backup

```bash
# Backup Redis data
docker exec gherkin-redis redis-cli SAVE
docker cp gherkin-redis:/data/dump.rdb ./backup/redis-$(date +%Y%m%d).rdb

# Restore Redis data
docker cp ./backup/redis-20250101.rdb gherkin-redis:/data/dump.rdb
docker-compose restart gherkin-redis
```

### Configuration Backup

```bash
# Backup environment configuration
cp .env .env.backup.$(date +%Y%m%d)
```

## Scaling Considerations

### Horizontal Scaling

To run multiple web instances:

1. Update `docker-compose.prod.yml`:
   ```yaml
   services:
     gherkin-web:
       deploy:
         replicas: 3
   ```

2. Add load balancer (HAProxy, Nginx) in front of instances

### Redis Clustering

For high availability:

1. Use Redis Sentinel or Redis Cluster
2. Update `REDIS_URL` to point to cluster endpoint

## Monitoring

### Application Logs

```bash
# View logs
docker-compose logs -f gherkin-web

# Filter errors
docker-compose logs gherkin-web | grep ERROR
```

### Metrics

Monitor key metrics:
- Request latency (p50, p95, p99)
- Error rate (5xx responses)
- Redis connection pool utilization
- Edit lock contention

## Security Considerations

1. **API Token Rotation**:
   - Rotate Linear/GitHub tokens every 90 days
   - Update `.env` and restart services

2. **Network Security**:
   - Use Docker network isolation
   - Restrict Redis access to internal network only

3. **SSL/TLS**:
   - Use valid SSL certificates
   - Enable HTTPS for all production traffic

4. **Audit Logging**:
   - All approvals logged to Linear comments
   - Git commits provide audit trail

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs gherkin-web

# Verify environment variables
docker-compose config

# Test Redis connection
docker exec gherkin-redis redis-cli ping
```

### Linear API Connection Issues

```bash
# Test Linear token
curl -H "Authorization: Bearer $LINEAR_API_TOKEN" https://api.linear.app/graphql
```

### GitHub API Connection Issues

```bash
# Test GitHub token
curl -H "Authorization: token $GITHUB_API_TOKEN" https://api.github.com/user
```

## Updates and Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Database Migrations

Gherkin Taster is stateless - no database migrations required.

### Dependency Updates

```bash
# Update Python dependencies
uv lock --upgrade

# Rebuild Docker image
docker-compose build --no-cache
```
