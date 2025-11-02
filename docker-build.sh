#!/bin/bash
# Docker build script for Myki Transaction Tracker
# Purpose: Build Docker image with proper tags and build arguments
# Output: Docker image tagged as myki-tracker:local-v1

set -e  # Exit on any error

# Logging function for structured output
log() {
    echo "[BUILD] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[BUILD ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

# Banner
log "=================================="
log "Building Myki Tracker Docker Image"
log "=================================="

# Configuration
IMAGE_NAME="myki-tracker"
IMAGE_TAG="local-v1"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
log "Build context: $SCRIPT_DIR"

# Verify Dockerfile exists
if [ ! -f "$SCRIPT_DIR/Dockerfile" ]; then
    log_error "Dockerfile not found in $SCRIPT_DIR"
    exit 1
fi

log "Dockerfile found: $SCRIPT_DIR/Dockerfile"

# Build options
BUILD_ARGS=""

# Add platform support for multi-architecture builds (optional)
# Uncomment the following line to enable multi-arch builds with buildx:
# BUILD_ARGS="--platform linux/amd64,linux/arm64"
# Note: Multi-arch builds require docker buildx and may not work on all systems

# Build the Docker image
log "Building Docker image: $FULL_IMAGE_NAME"
log "Build arguments: ${BUILD_ARGS:-none}"

if [ -n "$BUILD_ARGS" ]; then
    # Build with buildx for multi-architecture support
    log "Using docker buildx for multi-architecture build"
    docker buildx build $BUILD_ARGS -t "$FULL_IMAGE_NAME" "$SCRIPT_DIR"
else
    # Standard build for current architecture
    log "Using standard docker build for current architecture"
    docker build -t "$FULL_IMAGE_NAME" "$SCRIPT_DIR"
fi

BUILD_EXIT_CODE=$?

# Check build success
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    log "=================================="
    log "Build completed successfully!"
    log "Image: $FULL_IMAGE_NAME"
    log "=================================="

    # Display image information
    log "Image details:"
    docker images "$FULL_IMAGE_NAME"

    # Display image size
    IMAGE_SIZE=$(docker images "$FULL_IMAGE_NAME" --format "{{.Size}}")
    log "Image size: $IMAGE_SIZE"

    exit 0
else
    log_error "=================================="
    log_error "Build failed with exit code: $BUILD_EXIT_CODE"
    log_error "=================================="
    exit $BUILD_EXIT_CODE
fi
