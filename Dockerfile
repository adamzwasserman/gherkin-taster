# Multi-stage Dockerfile for Gherkin Taster
# Based on IDD patterns - Alpine Linux, non-root user, health checks

# Stage 1: Build stage
FROM python:3.13-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system --no-cache .
RUN uv pip install --system --no-cache ".[dev]"

# Stage 2: Runtime stage
FROM python:3.13-alpine

WORKDIR /app

# Install runtime dependencies only
RUN apk add --no-cache \
    libffi \
    openssl \
    curl

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create non-root user
RUN addgroup -g 1000 gherkin && \
    adduser -D -u 1000 -G gherkin gherkin

# Copy application code
COPY --chown=gherkin:gherkin backend/ /app/backend/
COPY --chown=gherkin:gherkin app/ /app/app/

# Switch to non-root user
USER gherkin

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
