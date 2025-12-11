# Streamlit Frontend Dockerfile for Cloud Run
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and assets
COPY app_v2.py .
COPY assets/ ./assets/

# Cloud Run will provide PORT environment variable
ENV PORT=8080
EXPOSE 8080

# Streamlit configuration for Cloud Run
# --server.port uses Cloud Run's port
# --server.address 0.0.0.0 allows external connections
# --server.enableCORS false prevents CORS issues
# --server.enableXsrfProtection false needed for Cloud Run
CMD streamlit run app_v2.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --server.headless=true
