#!/bin/bash
# Docker run script for Myki Transaction Tracker
# Purpose: Run Docker container with all required volume mounts and environment variables
# Output: Container execution with proper configuration

set -e  # Exit on any error

# Logging function for structured output
log() {
    echo "[RUN] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[RUN ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# Banner
log "=================================="
log "Running Myki Tracker Docker Container"
log "=================================="

# Configuration
# Allow overriding image name via environment variable or command line argument
IMAGE_NAME="${1:-${DOCKER_IMAGE_NAME:-myki-tracker:latest}}"
CONTAINER_NAME="myki-tracker-run"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
log "Project directory: $SCRIPT_DIR"

# Load environment variables from .env file if it exists
ENV_FILE="$SCRIPT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    log "Loading environment variables from .env file"
    set -a  # Automatically export all variables
    source "$ENV_FILE"
    set +a
else
    log "Warning: .env file not found at $ENV_FILE"
    log "Environment variables must be set manually or passwords will be missing"
fi

# Verify required directories exist
REQUIRED_DIRS=(
    "$SCRIPT_DIR/config"
    "$SCRIPT_DIR/browser_profile"
    "$SCRIPT_DIR/output"
    "$SCRIPT_DIR/auth_data"
    "$SCRIPT_DIR/screenshots"
)

for DIR in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        log "Creating required directory: $DIR"
        mkdir -p "$DIR"
    fi
done

# Fix permissions for mounted directories
# Docker container runs as UID 1000, so ensure directories are writable
log "Setting permissions for mounted directories..."
chmod -R 755 "$SCRIPT_DIR/browser_profile" "$SCRIPT_DIR/output" "$SCRIPT_DIR/auth_data" "$SCRIPT_DIR/screenshots" 2>/dev/null || true

# Verify config file exists
CONFIG_FILE="$SCRIPT_DIR/config/myki_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    log_error "Config file not found: $CONFIG_FILE"
    log_error "Please create config/myki_config.json before running the container"
    exit 1
fi

log "Config file found: $CONFIG_FILE"

# Check if Docker image exists
if ! docker images -q "$IMAGE_NAME" > /dev/null 2>&1; then
    log_error "Docker image not found: $IMAGE_NAME"
    log_error "Please run docker-build.sh first to build the image"
    exit 1
fi

log "Docker image found: $IMAGE_NAME"

# Remove existing container if it exists (from previous runs without --rm)
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "Removing existing container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true
fi

# Prepare environment variable flags
ENV_FLAGS=()

# Always set DISPLAY for Xvfb
ENV_FLAGS+=("-e" "DISPLAY=:99")

# Set Chrome profile directory
ENV_FLAGS+=("-e" "CHROME_PROFILE_DIR=/app/browser_profile")

# Pass user passwords from environment (pattern: MYKI_PASSWORD_*)
# These should be loaded from .env file
for VAR in $(compgen -e | grep "^MYKI_PASSWORD_"); do
    ENV_FLAGS+=("-e" "$VAR=${!VAR}")
    log "Passing environment variable: $VAR=***"
done

# Verify at least one password is set
if [ ${#ENV_FLAGS[@]} -le 2 ]; then
    log_error "No MYKI_PASSWORD_* environment variables found"
    log_error "Please set passwords in .env file (e.g., MYKI_PASSWORD_KOUSTUBH25=your_password)"
    log_error "See .env.example for reference"
    exit 1
fi

# Prepare volume mount flags
VOLUME_FLAGS=(
    # Config directory (read-only)
    "-v" "$SCRIPT_DIR/config:/app/config:ro"

    # Browser profile directory (read-write) - Chrome needs write access
    "-v" "$SCRIPT_DIR/browser_profile:/app/browser_profile:rw"

    # Output directory (read-write) - for attendance.json
    "-v" "$SCRIPT_DIR/output:/app/output:rw"

    # Auth data directory (read-write) - for session files
    "-v" "$SCRIPT_DIR/auth_data:/app/auth_data:rw"

    # Screenshots directory (read-write) - for debugging screenshots
    "-v" "$SCRIPT_DIR/screenshots:/app/screenshots:rw"
)

# Container flags
CONTAINER_FLAGS=(
    "--rm"                      # Automatically remove container when it exits
    "--name" "$CONTAINER_NAME"  # Container name for easy identification
)

# Build complete docker run command
log "Starting container: $CONTAINER_NAME"
log "Volume mounts:"
log "  - config (ro):          $SCRIPT_DIR/config -> /app/config"
log "  - browser_profile (rw): $SCRIPT_DIR/browser_profile -> /app/browser_profile"
log "  - output (rw):          $SCRIPT_DIR/output -> /app/output"
log "  - auth_data (rw):       $SCRIPT_DIR/auth_data -> /app/auth_data"
log "  - screenshots (rw):     $SCRIPT_DIR/screenshots -> /app/screenshots"
log ""

# Execute docker run command
docker run \
    "${CONTAINER_FLAGS[@]}" \
    "${ENV_FLAGS[@]}" \
    "${VOLUME_FLAGS[@]}" \
    "$IMAGE_NAME"

# Capture container exit code
CONTAINER_EXIT_CODE=$?

# Report exit code
if [ $CONTAINER_EXIT_CODE -eq 0 ]; then
    log "=================================="
    log "Container completed successfully!"
    log "Exit code: $CONTAINER_EXIT_CODE"
    log "=================================="
    log "Output file: $SCRIPT_DIR/output/attendance.json"
else
    log_error "=================================="
    log_error "Container failed"
    log_error "Exit code: $CONTAINER_EXIT_CODE"
    log_error "=================================="
    log_error "Check docker logs for details"
fi

exit $CONTAINER_EXIT_CODE
