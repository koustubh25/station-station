# Specification: Docker Headed Mode Deployment

## Goal
Deploy the working Myki transaction tracker in a Docker container with Xvfb (virtual display) to enable headed Chrome execution without a physical display, replicating the successful local Cloudflare bypass for local testing and validation.

## User Stories
- As a developer, I want to run the Myki tracker in Docker locally so that I can test containerized deployment without modifying the working codebase
- As a system operator, I want the Docker container to produce the same successful results as local execution so that I can trust the containerized workflow before cloud deployment

## Specific Requirements

**Xvfb Virtual Display Configuration**
- Install and configure Xvfb to provide virtual display :99 with 1920x1080 resolution and 24-bit color depth
- Start Xvfb before launching Chrome using a startup script or entrypoint wrapper
- Set DISPLAY environment variable to :99 for all browser processes
- Ensure Xvfb process remains running throughout container execution
- Include xvfb-run wrapper option as alternative startup method

**Chrome Browser Installation**
- Install Google Chrome Stable (NOT Chromium) via official Google repositories to match local `channel='chrome'` configuration
- Install all required Chrome dependencies from requirements.md system dependencies list
- Verify Chrome installation can launch in headed mode with Xvfb display
- Ensure Chrome version compatibility with Playwright 1.55.0
- Add fallback option to test Chromium with `channel='chromium'` modification if Chrome installation fails

**Python Environment Setup**
- Use Python 3.8+ base image (recommend python:3.9-slim or python:3.10-slim)
- Install all dependencies from requirements.txt including Playwright, playwright-stealth, python-dotenv, requests, holidays, pytest
- Run `playwright install-deps` to install Playwright browser dependencies
- Create working directory /app for application code
- Copy entire src directory and preserve directory structure

**Volume Mount Strategy**
- Mount config directory as read-only: /app/config (contains myki_config.json)
- Mount browser_profile directory as read-write: /app/browser_profile (writable Chrome profile)
- Mount output directory as read-write: /app/output (for attendance.json results)
- Mount auth_data directory as read-write: /app/auth_data (for session files)
- Ensure proper file permissions for mounted volumes to avoid UID/GID mismatch errors
- Document that browser_profile should contain pre-warmed Chrome profile with trust signals

**Chrome Profile Handling**
- Support two profile strategies: mounted profile (preferred) and copied local profile
- Modify profile_manager.py usage to accept profile location from environment variable CHROME_PROFILE_DIR
- If mounted profile exists at /app/browser_profile, use it directly instead of copying from local system
- If no mounted profile, copy from host system's Chrome profile during image build or first run
- Ensure profile directory has write permissions for Chrome to update cookies, history, preferences
- Document profile warming process: run Chrome manually in container, visit myki site, let Cloudflare build trust

**Environment Variable Configuration**
- Accept DISPLAY=:99 for Xvfb display targeting
- Accept MYKI_PASSWORD_{USERNAME} pattern for user passwords (e.g., MYKI_PASSWORD_KOUSTUBH)
- Accept CHROME_PROFILE_DIR to override default profile location
- Pass all environment variables through docker run -e flags or --env-file option
- Document all required and optional environment variables in README

**Docker Entrypoint Script**
- Create entrypoint.sh that starts Xvfb in background before running Python script
- Verify Xvfb started successfully by checking for :99 display
- Execute `python src/run_myki_workflow.py config/myki_config.json` as main command
- Capture exit code from workflow script and pass through as container exit code
- Add error handling for Xvfb startup failures
- Keep container logs clean with structured output

**Success Validation Approach**
- Container must exit with code 0 on successful workflow completion
- Verify output/attendance.json file exists and contains valid JSON with attendance data
- Verify auth_data/session_{username}.json files created for each configured user
- Check for success message "COMPLETED SUCCESSFULLY - All users processed" in logs
- Implement health check script that validates output file presence and structure
- Document validation commands for manual testing post-run

**Build and Run Scripts**
- Create docker-build.sh to build image with proper tags and build args
- Support multi-architecture builds (linux/amd64, linux/arm64) using Docker buildx for future cloud deployment compatibility
- Create docker-run.sh with all necessary volume mounts, environment variables, and flags
- Create docker-test.sh to run container and validate output automatically
- Use .dockerignore to exclude unnecessary files (pycache, .env, screenshots, temp files)
- Tag images with version numbers for tracking (e.g., myki-tracker:local-v1)

**File Permissions and User Management**
- Run container as non-root user (UID 1000) to avoid permission issues with mounted volumes
- Create app user in Dockerfile with proper home directory
- Ensure app user owns /app directory and subdirectories
- Set umask appropriately so created files are readable on host
- Document UID/GID mapping requirements for different host systems

**Logging and Debugging Support**
- Mount screenshots directory as volume for debugging failed runs
- Include verbose logging from browser_config.py, myki_auth.py, and run_myki_workflow.py
- Capture Playwright browser logs and console output
- Provide docker-debug.sh script that runs container with interactive shell for troubleshooting
- Document how to access container logs using docker logs command

## Implementation Status

**Completed:**
- ✅ All Docker infrastructure (Dockerfile, entrypoint.sh, build scripts)
- ✅ Multi-architecture support (AMD64/ARM64)
- ✅ Volume mount strategy and Chrome profile handling
- ✅ Test suite (25 tests across 5 test files)
- ✅ Comprehensive documentation (DOCKER_README.md, troubleshooting guides)
- ✅ **GitHub Actions workflow** (.github/workflows/myki-tracker-docker.yml)

**Testing Status:**
- ✅ Docker image builds successfully (2.58GB)
- ⚠️ Functional testing blocked on ARM64 macOS (platform limitation)
- ⏳ Awaiting AMD64 Linux testing via GitHub Actions

**GitHub Actions Deployment:**
- Located at: `.github/workflows/myki-tracker-docker.yml`
- Triggers: Manual (workflow_dispatch), Scheduled (daily 9 AM UTC), Push to main
- Runs Docker container on ubuntu-latest (AMD64 Linux)
- Uploads results as artifacts
- Optional: Commits results back to repository

## Out of Scope (For This Spec)
- Cloud Run deployment configuration and cloud-specific optimizations
- Google Cloud Storage integration for profile synchronization
- Production secrets management with cloud secret managers
- Monitoring, alerting, or observability platform integration
- Performance optimization for faster execution times
- Retry logic or failure recovery mechanisms beyond what exists in code
- Multi-container orchestration with docker-compose (optional nice-to-have but not required)
