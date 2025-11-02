#!/bin/bash
# Docker entrypoint script for Myki Transaction Tracker
# Purpose: Start Xvfb virtual display before running the workflow
# Ensures Chrome can run in headed mode for Cloudflare bypass

set -e  # Exit on any error

# Set umask for proper file permissions on created files
# umask 0002 allows group write access (rw-rw-r--)
# This ensures files created in mounted volumes are accessible on host
umask 0002

# Logging function for structured output
log() {
    echo "[ENTRYPOINT] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[ENTRYPOINT ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# Cleanup function to kill Xvfb on exit
cleanup() {
    local exit_code=$?
    log "Cleanup triggered (exit code: $exit_code)"

    if [ -n "$XVFB_PID" ] && kill -0 "$XVFB_PID" 2>/dev/null; then
        log "Stopping Xvfb process (PID: $XVFB_PID)"
        kill "$XVFB_PID" 2>/dev/null || true
        wait "$XVFB_PID" 2>/dev/null || true
    fi

    log "Container shutdown complete"
    exit $exit_code
}

# Set up trap to ensure cleanup runs on exit
trap cleanup EXIT INT TERM

# Banner
log "=================================="
log "Myki Tracker Docker Container"
log "=================================="

# Fix permissions on mounted directories
# This is critical for GitHub Actions where mounted volumes may have restrictive permissions
log "Fixing permissions on mounted directories..."
CHROME_PROFILE_DIR="${CHROME_PROFILE_DIR:-/app/browser_profile}"
for dir in /app/output /app/auth_data /app/screenshots "$CHROME_PROFILE_DIR"; do
    if [ -d "$dir" ]; then
        chmod -R 777 "$dir" 2>/dev/null || true
        log "  ✓ Fixed permissions: $dir"
    fi
done

# Environment variable information
log "Environment Configuration:"
log "  DISPLAY: ${DISPLAY:-<not set>}"
log "  CHROME_PROFILE_DIR: ${CHROME_PROFILE_DIR:-/app/browser_profile (default)}"
log "  PYTHONUNBUFFERED: ${PYTHONUNBUFFERED:-<not set>}"

# Step 1: Start Xvfb virtual display
log "Starting Xvfb on display :99 (resolution: 1920x1080x24)"

# Start Xvfb in background
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!

log "Xvfb started with PID: $XVFB_PID"

# Step 2: Wait for Xvfb to initialize
log "Waiting for Xvfb to initialize (3 seconds)..."
sleep 3

# Step 3: Verify Xvfb is running
if ! kill -0 "$XVFB_PID" 2>/dev/null; then
    log_error "Xvfb process failed to start or died immediately"
    log_error "Check Xvfb logs for details"
    exit 1
fi

log "Xvfb process is running"

# Step 4: Verify display :99 is available
log "Verifying display :99 is available..."

if command -v xdpyinfo &> /dev/null; then
    if ! xdpyinfo -display :99 >/dev/null 2>&1; then
        log_error "Display :99 is not accessible via xdpyinfo"
        log_error "Xvfb may not have initialized correctly"
        exit 1
    fi
    log "Display :99 verified and accessible"
else
    log "Warning: xdpyinfo not available, skipping display verification"
    log "Assuming Xvfb is ready based on process check"
fi

# Step 5: Set DISPLAY environment variable (should already be set by Dockerfile)
export DISPLAY=:99
log "DISPLAY environment variable set to: $DISPLAY"

# Step 6: Set Chrome profile directory from environment variable or use default
# This allows runtime override of the Chrome profile location
export CHROME_PROFILE_DIR="${CHROME_PROFILE_DIR:-/app/browser_profile}"
log "Chrome profile directory: $CHROME_PROFILE_DIR"

# Verify Chrome profile directory exists and is writable
if [ ! -d "$CHROME_PROFILE_DIR" ]; then
    log "Warning: Chrome profile directory does not exist: $CHROME_PROFILE_DIR"
    log "Creating Chrome profile directory..."
    mkdir -p "$CHROME_PROFILE_DIR" || log_error "Failed to create profile directory"
fi

if [ ! -w "$CHROME_PROFILE_DIR" ]; then
    log_error "Chrome profile directory is not writable: $CHROME_PROFILE_DIR"
    log_error "Chrome needs write access to update cookies, preferences, and session data"
    log_error "Check volume mount permissions (should be owned by UID 1000)"
fi

# Step 7: Execute the Python workflow script or custom command
# Check if custom command was provided (for debugging/testing)
if [ $# -gt 0 ]; then
    log "Executing custom command: $*"
    "$@"
    WORKFLOW_EXIT_CODE=$?
else
    # Check if the default config file exists before running
    if [ ! -f "config/myki_config.json" ]; then
        log_error "Default config file not found: config/myki_config.json"
        log_error "Either mount the config file or provide a custom command"
        log_error "Example: docker run myki-tracker /bin/bash -c 'your-command'"
        exit 1
    fi

    log "Executing default workflow: python src/run_myki_workflow.py config/myki_config.json"
    python src/run_myki_workflow.py config/myki_config.json
    WORKFLOW_EXIT_CODE=$?
fi

# Step 8: Report workflow exit code
if [ $WORKFLOW_EXIT_CODE -eq 0 ]; then
    log "=================================="
    log "Workflow completed successfully"
    log "Exit code: $WORKFLOW_EXIT_CODE"
    log "=================================="
else
    log_error "=================================="
    log_error "Workflow failed"
    log_error "Exit code: $WORKFLOW_EXIT_CODE"
    log_error "=================================="
fi

# Exit with workflow's exit code
# cleanup() will be called by trap EXIT
exit $WORKFLOW_EXIT_CODE
