#!/bin/bash
# Docker debug script for Myki Transaction Tracker
# Purpose: Run container with interactive shell for troubleshooting
# Output: Interactive bash shell inside container with all mounts

set -e  # Exit on any error

# Logging function for structured output
log() {
    echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[DEBUG ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# Banner
log "=================================="
log "Myki Tracker Docker Debug Shell"
log "=================================="

# Configuration
IMAGE_NAME="myki-tracker:local-v1"
CONTAINER_NAME="myki-tracker-debug"

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

# Check if Docker image exists
if ! docker images -q "$IMAGE_NAME" > /dev/null 2>&1; then
    log_error "Docker image not found: $IMAGE_NAME"
    log_error "Please run docker-build.sh first to build the image"
    exit 1
fi

log "Docker image found: $IMAGE_NAME"

# Remove existing debug container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "Removing existing debug container: $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1 || true
fi

# Prepare environment variable flags
ENV_FLAGS=()

# Always set DISPLAY for Xvfb
ENV_FLAGS+=("-e" "DISPLAY=:99")

# Set Chrome profile directory
ENV_FLAGS+=("-e" "CHROME_PROFILE_DIR=/app/browser_profile")

# Pass user passwords from environment (pattern: MYKI_PASSWORD_*)
for VAR in $(compgen -e | grep "^MYKI_PASSWORD_" || true); do
    ENV_FLAGS+=("-e" "$VAR=${!VAR}")
    log "Passing environment variable: $VAR=***"
done

# Prepare volume mount flags (same as docker-run.sh)
VOLUME_FLAGS=(
    # Config directory (read-only in production, but read-write for debugging)
    "-v" "$SCRIPT_DIR/config:/app/config:rw"

    # Browser profile directory (read-write)
    "-v" "$SCRIPT_DIR/browser_profile:/app/browser_profile:rw"

    # Output directory (read-write)
    "-v" "$SCRIPT_DIR/output:/app/output:rw"

    # Auth data directory (read-write)
    "-v" "$SCRIPT_DIR/auth_data:/app/auth_data:rw"

    # Screenshots directory (read-write)
    "-v" "$SCRIPT_DIR/screenshots:/app/screenshots:rw"
)

# Container flags
CONTAINER_FLAGS=(
    "-it"                       # Interactive terminal
    "--rm"                      # Automatically remove container when it exits
    "--name" "$CONTAINER_NAME"  # Container name for easy identification
    "--entrypoint" "/bin/bash"  # Override entrypoint to get shell
)

# Display helpful information
log ""
log "Starting interactive debug shell..."
log ""
log "Volume mounts:"
log "  - config (rw):          $SCRIPT_DIR/config -> /app/config"
log "  - browser_profile (rw): $SCRIPT_DIR/browser_profile -> /app/browser_profile"
log "  - output (rw):          $SCRIPT_DIR/output -> /app/output"
log "  - auth_data (rw):       $SCRIPT_DIR/auth_data -> /app/auth_data"
log "  - screenshots (rw):     $SCRIPT_DIR/screenshots -> /app/screenshots"
log ""
log "Common debug commands:"
log "  - Start Xvfb manually:    Xvfb :99 -screen 0 1920x1080x24 &"
log "  - Check Xvfb running:     ps aux | grep Xvfb"
log "  - Verify display:         xdpyinfo -display :99"
log "  - Run workflow manually:  python src/run_myki_workflow.py config/myki_config.json"
log "  - Check Chrome version:   google-chrome --version"
log "  - Test Chrome launch:     google-chrome --display=:99 --no-sandbox --headless"
log "  - Check Python packages:  pip list | grep playwright"
log "  - View environment vars:  env | grep MYKI"
log "  - Check file permissions: ls -la /app/browser_profile"
log "  - Exit debug shell:       exit"
log ""
log "=================================="
log ""

# Execute docker run command with interactive shell
docker run \
    "${CONTAINER_FLAGS[@]}" \
    "${ENV_FLAGS[@]}" \
    "${VOLUME_FLAGS[@]}" \
    "$IMAGE_NAME"

# Capture exit code
DEBUG_EXIT_CODE=$?

log ""
log "Debug shell exited with code: $DEBUG_EXIT_CODE"
exit $DEBUG_EXIT_CODE
