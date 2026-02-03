FROM python:3.11-slim

# Set metadata
LABEL maintainer="Concilium Team"
LABEL description="Concilium AI Assistant - Workflow Generation Service"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU version (smaller image, works on any system)
RUN pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p uploads outputs/workflows outputs/documents templates logs

# Create non-root user for security
RUN useradd -m -u 1000 concilium && \
    chown -R concilium:concilium /app

# Switch to non-root user
USER concilium

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "-m", "app.main"]
