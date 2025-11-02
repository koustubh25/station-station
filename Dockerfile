# Dockerfile for Myki Transaction Tracker - Docker Headed Mode Deployment
# Base image: Python 3.9-slim for smaller image size
# Purpose: Enable headed Chrome execution with Xvfb virtual display for Cloudflare bypass

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Xvfb, Chrome, and Playwright
# Install in single RUN command to reduce image layers
RUN apt-get update && apt-get install -y \
    # Xvfb for virtual display
    xvfb \
    x11-utils \
    # Core utilities
    wget \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    # Google Chrome/Chromium dependencies
    fonts-liberation \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libxshmfence1 \
    # Additional fonts for better rendering
    fonts-noto \
    fonts-noto-color-emoji \
    # Process management utilities
    procps \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable (NOT Chromium) from official Google repositories
# This is critical for Cloudflare bypass success
# Note: For ARM64 systems (like Apple Silicon), we use Chromium as Chrome is not available
# For production AMD64 deployment, Google Chrome Stable will be installed
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        # AMD64: Install Google Chrome Stable
        wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
        apt-get update && \
        apt-get install -y /tmp/google-chrome-stable_current_amd64.deb && \
        rm -rf /var/lib/apt/lists/* /tmp/google-chrome-stable_current_amd64.deb; \
    else \
        # ARM64/other: Install Chromium as fallback
        apt-get update && \
        apt-get install -y chromium chromium-driver && \
        rm -rf /var/lib/apt/lists/* && \
        # Create symlink for google-chrome command to point to chromium
        ln -s /usr/bin/chromium /usr/bin/google-chrome || true; \
    fi

# Create non-root user for container execution (UID 1000, GID 1000)
# This matches typical host user permissions for volume mounts
RUN groupadd -g 1000 app \
    && useradd -u 1000 -g 1000 -m -s /bin/bash app

# Create required directories with proper ownership
# These will be used for volume mounts at runtime
RUN mkdir -p /app/config \
    /app/browser_profile \
    /app/output \
    /app/auth_data \
    /app/screenshots \
    && chown -R app:app /app

# Copy requirements.txt first for Docker layer caching optimization
# This layer will only rebuild if requirements.txt changes
COPY --chown=app:app requirements.txt /app/requirements.txt

# Install Python dependencies
# Run as root to install system-level packages, then switch to app user
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Playwright browser dependencies
# This installs additional system packages required by Playwright browsers
RUN playwright install-deps

# Copy application source code
# Preserves directory structure and sets ownership to app user
COPY --chown=app:app src/ /app/src/

# Copy entrypoint script and make it executable
# This script starts Xvfb before running the workflow
COPY --chown=app:app entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user for execution
USER app

# Configure environment variables
# DISPLAY: Points to Xvfb virtual display :99
# PYTHONUNBUFFERED: Enables real-time logging output (no buffering)
ENV DISPLAY=:99 \
    PYTHONUNBUFFERED=1

# Environment variables that should be provided at runtime:
# - MYKI_PASSWORD_{USERNAME}: Password for each user (e.g., MYKI_PASSWORD_KOUSTUBH)
# - CHROME_PROFILE_DIR: Override default Chrome profile location (default: /app/browser_profile)

# Set entrypoint script to start Xvfb and run workflow
# The entrypoint script:
# - Starts Xvfb on display :99 with 1920x1080x24 resolution
# - Waits for Xvfb to initialize and verifies display is available
# - Executes the Python workflow script
# - Captures and passes through the workflow exit code
# - Cleans up Xvfb process on container exit
#
# Command override options:
# - Default: Runs python src/run_myki_workflow.py config/myki_config.json
# - Custom: docker run myki-tracker [custom-command] - for debugging/testing
# - Shell: docker run -it --entrypoint /bin/bash myki-tracker - for interactive access
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command: None (entrypoint script handles default workflow execution)
# Can be overridden at runtime: docker run myki-tracker /bin/bash
CMD []
