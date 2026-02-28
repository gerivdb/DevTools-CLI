# Multi-stage Dockerfile for FastAPI Microservice
# Generated from DevTools-CLI template
# Build: docker build -t {{ APP_NAME }}:latest -f python-fastapi.dockerfile .
# Run: docker run -p {{ PORT }}:{{ PORT }} {{ APP_NAME }}:latest

# ============================================================================
# Stage 1: Builder - Compile dependencies
# ============================================================================
FROM python:{{ PYTHON_VERSION }}-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:{{ PYTHON_VERSION }}-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_NAME={{ APP_NAME }} \
    PORT={{ PORT }}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:{{ PORT }}/health || exit 1

# Expose port
EXPOSE {{ PORT }}

# Run application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{ PORT }}", "--workers", "4"]