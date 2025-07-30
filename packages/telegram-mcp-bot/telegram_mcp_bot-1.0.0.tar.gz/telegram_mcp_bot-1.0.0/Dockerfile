FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for MCP Playwright
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install uv
RUN pip install uv

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN uv sync

# Install Playwright browsers
RUN npx playwright install chromium
RUN npx playwright install-deps chromium

# Set environment variables for headless mode
ENV PLAYWRIGHT_HEADLESS=true
ENV PLAYWRIGHT_NO_SANDBOX=true
ENV PLAYWRIGHT_DISABLE_WEB_SECURITY=true
ENV PLAYWRIGHT_DISABLE_DEV_SHM_USAGE=true
ENV TOKENIZERS_PARALLELISM=false

# Create directories
RUN mkdir -p /app/chroma /app/logs

# Expose webhook port
EXPOSE 8443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD uv run python -c "import requests; requests.get('http://localhost:8443/health', timeout=5)" || exit 1

# Default command (can be overridden)
CMD ["uv", "run", "python", "unified_bot.py"] 