# Consilium Dockerfile
# Multi-Agent LLM Debate System
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml ./

# Install Python dependencies directly with pip
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/

# Create output directory
RUN mkdir -p /app/output

# Expose port 8080
EXPOSE 8080

# Set environment variables
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the web app
CMD ["python", "src/cli.py", "web-app", "--host", "0.0.0.0", "--port", "8080"]
