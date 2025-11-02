# Docker Image Testing Instructions

## Prerequisites

1. **Docker Desktop must be running**
   ```bash
   # Start Docker Desktop (macOS)
   open -a Docker

   # Verify Docker is running
   docker ps
   ```

2. **Network access to Docker Hub**
   - Corporate networks may require proxy or registry configuration
   - If you encounter 403 errors from corporate registries, configure Docker to use Docker Hub directly

## Running the Validation Tests

### Option 1: Automated Test Suite (Recommended)

Run the Docker image validation tests using pytest:

```bash
cd /Users/gaikwadk/Documents/station-station-agentos

# Ensure Docker Desktop is running first
docker ps

# Run all Docker validation tests
python -m pytest tests/test_docker_image.py -v

# Run specific test
python -m pytest tests/test_docker_image.py::TestDockerImageBuild::test_chrome_stable_installed -v
```

**Expected Output:**
```
tests/test_docker_image.py::TestDockerImageBuild::test_docker_image_builds_successfully PASSED
tests/test_docker_image.py::TestDockerImageBuild::test_python_version_installed PASSED
tests/test_docker_image.py::TestDockerImageBuild::test_chrome_stable_installed PASSED
tests/test_docker_image.py::TestDockerImageBuild::test_xvfb_installed_and_can_start PASSED

4 passed in XXX seconds
```

### Option 2: Manual Build and Verification

If you prefer to test manually without pytest:

```bash
cd /Users/gaikwadk/Documents/station-station-agentos

# Build the Docker image
docker build -t myki-tracker:test-build .

# Expected: Build completes successfully (may take 5-10 minutes on first run)
```

**Verify Python 3.9+:**
```bash
docker run --rm myki-tracker:test-build python --version
# Expected output: Python 3.9.x
```

**Verify Google Chrome Stable (NOT Chromium):**
```bash
docker run --rm myki-tracker:test-build google-chrome --version
# Expected output: Google Chrome XXX.X.XXXX.XXX
# Must say "Google Chrome", NOT "Chromium"
```

**Verify Xvfb is installed:**
```bash
docker run --rm myki-tracker:test-build which Xvfb
# Expected output: /usr/bin/Xvfb
```

**Verify Xvfb can start on display :99:**
```bash
docker run --rm myki-tracker:test-build /bin/bash -c "Xvfb :99 -screen 0 1920x1080x24 & sleep 2; ps aux | grep Xvfb | grep -v grep"
# Expected output: Process line showing Xvfb :99 -screen 0 1920x1080x24
```

**Verify non-root user (UID 1000):**
```bash
docker run --rm myki-tracker:test-build id
# Expected output: uid=1000(app) gid=1000(app) groups=1000(app)
```

**Verify required directories exist:**
```bash
docker run --rm myki-tracker:test-build ls -la /app
# Expected: config/, browser_profile/, output/, auth_data/, screenshots/, src/
```

## Test Coverage

### What is Tested (Task Group 1)

The 4 tests created in `tests/test_docker_image.py` validate:

1. **Build Success** - Dockerfile builds without errors
2. **Python Version** - Python 3.9+ is installed
3. **Chrome Installation** - Google Chrome Stable (not Chromium) is present
4. **Xvfb Functionality** - Virtual display can start on :99

### What is NOT Tested (Yet)

The following will be tested in later Task Groups:

- **Task Group 2:** Entrypoint script, Xvfb startup, workflow execution
- **Task Group 3:** Volume mounts, file permissions, Chrome profile handling
- **Task Group 4:** Build scripts, run scripts, automation
- **Task Group 5:** End-to-end workflow, Cloudflare bypass, output validation

## Troubleshooting

### Docker daemon not running
```
ERROR: Cannot connect to the Docker daemon at unix:///Users/gaikwadk/.docker/run/docker.sock
```

**Solution:** Start Docker Desktop
```bash
open -a Docker
# Wait 30-60 seconds for Docker to fully start
docker ps
```

### Corporate registry 403 errors
```
ERROR: unexpected status from HEAD request to https://corporate-registry/v2/library/python/manifests/3.9-slim: 403
```

**Solution:** Configure Docker to bypass corporate registry for public images
1. Open Docker Desktop settings
2. Go to Docker Engine
3. Add or modify `registry-mirrors` configuration
4. Or: Configure HTTP proxy settings in Docker Desktop

### Build timeout or slow build
```
Build takes > 10 minutes or times out
```

**Possible causes:**
- Slow network connection (downloading Chrome, Python packages)
- Insufficient disk space
- Corporate proxy slowing downloads

**Solutions:**
- Increase pytest timeout in test fixture (default: 600 seconds)
- Check available disk space: `df -h`
- Run build manually first to warm cache: `docker build -t myki-tracker:test-build .`

### Test failures

If specific tests fail, run them individually to debug:

```bash
# Test just the build
python -m pytest tests/test_docker_image.py::TestDockerImageBuild::test_docker_image_builds_successfully -v

# Test just Chrome
python -m pytest tests/test_docker_image.py::TestDockerImageBuild::test_chrome_stable_installed -v
```

## Image Size

Expected final image size: **1.5-1.8 GB**

Components contributing to size:
- Base Python 3.9-slim: ~150MB
- Google Chrome Stable: ~200MB
- Chrome dependencies: ~300MB
- Python packages (Playwright, etc.): ~400MB
- System utilities: ~100MB

Check image size:
```bash
docker images | grep myki-tracker
# Example: myki-tracker  test-build  abc123  5 minutes ago  1.65GB
```

## Next Steps

After Task Group 1 tests pass:
1. **Task Group 2:** Create entrypoint.sh script for Xvfb startup
2. **Task Group 3:** Set up volume mounts and Chrome profile handling
3. **Task Group 4:** Create build/run automation scripts
4. **Task Group 5:** Run end-to-end integration tests
5. **Task Group 6:** Complete documentation

## Test Results Documentation

When tests pass, document results in `/Users/gaikwadk/Documents/station-station-agentos/agent-os/specs/2025-11-02-docker-headed-mode-deployment/verification/screenshots/` (if applicable for UI testing).

For Task Group 1, verification is primarily through test output, not screenshots.
