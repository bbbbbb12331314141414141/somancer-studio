FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend source and install dependencies
COPY packages/backend/ .

RUN pip install --no-cache-dir -e .

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run FastAPI with uvicorn
CMD ["uvicorn", "aimusic.main:app", "--host", "0.0.0.0", "--port", "8000"]
