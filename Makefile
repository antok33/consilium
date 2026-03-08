.PHONY: help install web-app test run-docker build-docker clean

# Default target
help:
	@echo "Consilium - Makefile Commands"
	@echo "=============================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make web-app       - Launch Gradio web interface (RECOMMENDED)"
	@echo "  make test          - Run pytest test suite"
	@echo "  make build-docker  - Build Docker image"
	@echo "  make run-docker    - Run Gradio app in Docker (port 8080)"
	@echo "  make clean         - Remove generated files and caches"
	@echo ""
	@echo "Note: Consilium is inspired by Andrej Karpathy's llm-council"
	@echo "      Use 'make web-app' as the primary interface."
	@echo "      For CLI usage, run: uv run python src/cli.py run --help"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	uv pip install -e ".[dev]"
	@echo "Dependencies installed successfully!"

# Launch web app (PRIMARY INTERFACE)
web-app:
	@echo "Launching Gradio web interface..."
	@echo "This is the recommended way to use Consilium."
	@echo ""
	uv run python src/cli.py web-app

# Run tests
test:
	@echo "Running test suite..."
	uv run pytest -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=src --cov-report=html --cov-report=term

# Build Docker image
build-docker:
	@echo "Building Docker image..."
	docker build -t consilium:latest .
	@echo "Docker image built successfully!"

# Run Docker container
run-docker:
	@echo "Starting Consilium in Docker (detached mode)..."
	@echo "Web interface will be available at http://localhost:8080"
	docker run -d -p 8080:8080 \
		--name consilium \
		--env-file .env \
		-v $(PWD)/output:/app/output \
		consilium:latest
	@echo "Container started! Check logs with: docker logs consilium"
	@echo "Stop with: make stop-docker"


# Stop Docker container
stop-docker:
	@echo "Stopping Docker container..."
	docker stop consilium
	docker rm consilium

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf output/*.md
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

# Format code (if you add a formatter later)
format:
	@echo "Code formatting not configured yet"

# Lint code (if you add a linter later)
lint:
	@echo "Linting not configured yet"
