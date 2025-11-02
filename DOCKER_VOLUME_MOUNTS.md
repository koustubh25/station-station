# Docker Volume Mounts Strategy

## Overview

This document describes the volume mount strategy for the Myki Tracker Docker deployment. Proper volume mounting ensures data persistence, configuration management, and correct file permissions between the host and container.

## Required Volume Mounts

The Docker container requires the following volume mounts for proper operation:

### 1. Config Directory (Read-Only)

```bash
-v $(pwd)/config:/app/config:ro
```

- **Purpose**: Provide configuration files (myki_config.json) to the container
- **Access Mode**: Read-only (`:ro`)
- **Host Path**: `./config/` (relative to project root)
- **Container Path**: `/app/config/`
- **Required Files**:
  - `myki_config.json` - User configuration with credentials mapping

**Notes**:
- Read-only mount prevents accidental modification of config from within container
- Config file must exist before starting container
- Container will fail if config file is missing

### 2. Browser Profile Directory (Read-Write)

```bash
-v $(pwd)/browser_profile:/app/browser_profile:rw
```

- **Purpose**: Chrome profile storage for cookies, preferences, browsing history
- **Access Mode**: Read-write (`:rw`)
- **Host Path**: `./browser_profile/` (relative to project root)
- **Container Path**: `/app/browser_profile/`
- **Critical**: Must be writable for Chrome to update session data

**Why Read-Write?**
Chrome needs write access to update:
- Cookies (authentication tokens, session data)
- Preferences (browser settings, site permissions)
- History (browsing history for trust signals)
- Web Data (form autofill, search suggestions)
- Login Data (saved credentials - if enabled)

**Profile Warming**:
For best Cloudflare bypass success, use a pre-warmed Chrome profile with browsing history and trust signals. See "Chrome Profile Preparation" section below.

### 3. Output Directory (Read-Write)

```bash
-v $(pwd)/output:/app/output:rw
```

- **Purpose**: Store workflow output files (attendance.json)
- **Access Mode**: Read-write (`:rw`)
- **Host Path**: `./output/` (relative to project root)
- **Container Path**: `/app/output/`
- **Output Files**:
  - `attendance.json` - Generated attendance data

**Notes**:
- Container creates attendance.json after successful workflow execution
- File persists on host after container stops
- Exit code 0 indicates successful file generation

### 4. Auth Data Directory (Read-Write)

```bash
-v $(pwd)/auth_data:/app/auth_data:rw
```

- **Purpose**: Store authentication session files
- **Access Mode**: Read-write (`:rw`)
- **Host Path**: `./auth_data/` (relative to project root)
- **Container Path**: `/app/auth_data/`
- **Session Files**:
  - `session_{username}.json` - One file per configured user

**Notes**:
- Session files enable faster re-authentication on subsequent runs
- Files persist between container runs
- Each user gets a separate session file

### 5. Screenshots Directory (Read-Write) - Optional for Debugging

```bash
-v $(pwd)/screenshots:/app/screenshots:rw
```

- **Purpose**: Store debugging screenshots on errors
- **Access Mode**: Read-write (`:rw`)
- **Host Path**: `./screenshots/` (relative to project root)
- **Container Path**: `/app/screenshots/`
- **Usage**: Screenshots captured when workflow encounters errors

**Notes**:
- Optional mount - only needed for debugging
- Screenshots help diagnose Cloudflare bypass failures
- Can be disabled for production runs to save disk I/O

## Complete Docker Run Command Example

```bash
docker run --rm \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/browser_profile:/app/browser_profile:rw \
  -v $(pwd)/output:/app/output:rw \
  -v $(pwd)/auth_data:/app/auth_data:rw \
  -v $(pwd)/screenshots:/app/screenshots:rw \
  -e DISPLAY=:99 \
  -e MYKI_PASSWORD_KOUSTUBH=your_password_here \
  -e CHROME_PROFILE_DIR=/app/browser_profile \
  myki-tracker:latest
```

## File Permissions and UID/GID Mapping

### Container User

The Docker container runs as a non-root user for security:
- **Username**: `app`
- **UID**: 1000
- **GID**: 1000

### Host Compatibility

For seamless file access between host and container:

**macOS/Linux (single user systems)**:
- Most personal systems use UID 1000 for the primary user
- Files created by container will be owned by your user
- No additional permission setup needed

**Linux (multi-user or custom UID)**:
- If your host UID is not 1000, you may encounter permission issues
- Options:
  1. Change ownership of mounted directories: `sudo chown -R 1000:1000 browser_profile output auth_data screenshots`
  2. Run container with `--user $(id -u):$(id -g)` flag (may require Dockerfile modification)
  3. Adjust umask in entrypoint.sh (already set to 0002 for group write)

**Permission Verification**:
```bash
# Check current user UID
id -u

# Check directory ownership
ls -ld browser_profile output auth_data

# Fix ownership if needed (Linux only)
sudo chown -R 1000:1000 browser_profile output auth_data screenshots
```

## Directory Structure in Container

All required directories are created during Docker image build:

```
/app/
├── config/          # Configuration files (mounted)
├── browser_profile/ # Chrome profile data (mounted)
├── output/          # Workflow output files (mounted)
├── auth_data/       # Session files (mounted)
├── screenshots/     # Debug screenshots (mounted)
└── src/             # Application code (copied during build)
```

Directory ownership set to `app:app` (UID 1000, GID 1000) during build.

## Environment Variables

### Required Variables

- **DISPLAY**: Set to `:99` for Xvfb virtual display (set in Dockerfile)
- **MYKI_PASSWORD_{USERNAME}**: Password for each user in config
  - Pattern: Username from config in uppercase
  - Example: `MYKI_PASSWORD_KOUSTUBH`, `MYKI_PASSWORD_JOHN`

### Optional Variables

- **CHROME_PROFILE_DIR**: Override default Chrome profile location
  - Default: `/app/browser_profile`
  - Custom: `-e CHROME_PROFILE_DIR=/custom/path`
  - Useful for testing multiple profiles

## Chrome Profile Preparation

### Option 1: Copy Existing Chrome Profile (Recommended)

This provides the best Cloudflare bypass success rate due to existing trust signals.

#### macOS

```bash
# Locate your Chrome profile
CHROME_PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"

# Create browser_profile directory
mkdir -p browser_profile

# Copy essential profile files
cp "$CHROME_PROFILE/Cookies" browser_profile/
cp "$CHROME_PROFILE/Preferences" browser_profile/
cp "$CHROME_PROFILE/History" browser_profile/
cp "$CHROME_PROFILE/Web Data" browser_profile/
cp "$CHROME_PROFILE/Login Data" browser_profile/ 2>/dev/null || true

# Set permissions for Docker container (UID 1000)
# Note: On macOS, file ownership typically matches your user (usually UID 501)
# Docker for Mac handles UID mapping automatically
chmod -R 755 browser_profile/
```

#### Linux

```bash
# Locate your Chrome profile
CHROME_PROFILE="$HOME/.config/google-chrome/Default"

# Create browser_profile directory
mkdir -p browser_profile

# Copy essential profile files
cp "$CHROME_PROFILE/Cookies" browser_profile/
cp "$CHROME_PROFILE/Preferences" browser_profile/
cp "$CHROME_PROFILE/History" browser_profile/
cp "$CHROME_PROFILE/Web Data" browser_profile/
cp "$CHROME_PROFILE/Login Data" browser_profile/ 2>/dev/null || true

# Set ownership to match container user (UID 1000)
sudo chown -R 1000:1000 browser_profile/
chmod -R 755 browser_profile/
```

#### Files Copied

- **Cookies**: Authentication cookies, session tokens
- **Preferences**: Browser settings, site permissions, Cloudflare trust signals
- **History**: Browsing history (helps establish trust)
- **Web Data**: Form autofill, search suggestions
- **Login Data**: Saved credentials (optional, may not exist)

### Option 2: Profile Warming (Manual)

If you don't have an existing Chrome profile or want to create a fresh one:

#### Step 1: Start Container with Interactive Shell

```bash
docker run -it --rm \
  -v $(pwd)/browser_profile:/app/browser_profile:rw \
  -e DISPLAY=:99 \
  myki-tracker:latest \
  /bin/bash
```

#### Step 2: Inside Container - Start Chrome Manually

```bash
# Start Chrome with the profile directory
google-chrome \
  --user-data-dir=/app/browser_profile \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  &

# Chrome will start in the Xvfb virtual display
```

#### Step 3: Visit Myki Site and Build Trust

Since you can't see the virtual display, use a remote debugging port:

```bash
# Start Chrome with remote debugging
google-chrome \
  --user-data-dir=/app/browser_profile \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --remote-debugging-port=9222 \
  &
```

Then on your host machine:
1. Open Chrome
2. Navigate to `chrome://inspect/#devices`
3. Configure remote target: `localhost:9222`
4. Open the remote session
5. Navigate to Myki site
6. Interact with the site to build trust signals
7. Close Chrome in container

**Note**: This method is more complex and may not be necessary if copying an existing profile works.

### Option 3: Start with Empty Profile

For testing purposes, you can start with an empty profile:

```bash
mkdir -p browser_profile
```

The container will create a fresh Chrome profile. Success rate for Cloudflare bypass may be lower without trust signals.

## Troubleshooting

### Permission Denied Errors

**Symptom**: `Permission denied` when writing to browser_profile, output, or auth_data

**Solution**:
```bash
# Check current ownership
ls -ld browser_profile output auth_data

# Linux: Set ownership to UID 1000
sudo chown -R 1000:1000 browser_profile output auth_data screenshots

# macOS: Usually not needed, but you can set permissions
chmod -R 755 browser_profile output auth_data screenshots
```

### Chrome Profile Lock Errors

**Symptom**: Chrome fails to start with "Profile in use" error

**Solution**:
```bash
# Remove lock files
rm -f browser_profile/SingletonLock
rm -f browser_profile/SingletonSocket
rm -f browser_profile/SingletonCookie
```

### Missing Output Files

**Symptom**: attendance.json not created after run

**Solution**:
1. Check container exit code: `echo $?` (should be 0)
2. Check docker logs for errors
3. Verify output directory is mounted and writable
4. Check workflow logs for authentication failures

### Volume Mount Not Working

**Symptom**: Files not appearing in container or on host

**Solution**:
1. Use absolute paths in volume mounts: `-v /absolute/path/to/config:/app/config:ro`
2. Verify directory exists on host before mounting
3. Check Docker permissions (Docker Desktop settings on macOS/Windows)

## Best Practices

### 1. Use Read-Only Mounts Where Possible

Mount config directory as read-only (`:ro`) to prevent accidental modification.

### 2. Pre-create Directories on Host

```bash
mkdir -p config browser_profile output auth_data screenshots
```

Ensures directories exist before mounting.

### 3. Regular Profile Backups

```bash
# Backup Chrome profile periodically
tar -czf browser_profile_backup_$(date +%Y%m%d).tar.gz browser_profile/
```

Chrome profile contains important cookies and session data.

### 4. Clean Up Old Screenshots

```bash
# Remove old debug screenshots
find screenshots/ -type f -mtime +7 -delete
```

Prevents disk space issues from accumulated screenshots.

### 5. Verify Mounts Before Running

```bash
# Check all required directories exist
ls -ld config browser_profile output auth_data
```

Prevents runtime errors due to missing mounts.

## Security Considerations

### 1. Chrome Profile Contains Sensitive Data

- Cookies include authentication tokens
- History reveals browsing patterns
- Login Data may contain credentials

**Recommendation**: Never commit `browser_profile/` to version control. Already excluded in `.gitignore`.

### 2. Environment Variables for Passwords

- Pass passwords via `-e` flags or `--env-file`
- Never hardcode passwords in Dockerfile or scripts
- Use `.env` file locally (excluded from git)

### 3. File Permissions

- Container runs as non-root (UID 1000) for security
- Mounted files inherit host permissions
- Avoid running container as root

## Related Documentation

- **Dockerfile**: `/Dockerfile` - Image build configuration
- **Entrypoint**: `/entrypoint.sh` - Startup script with Xvfb initialization
- **Docker Ignore**: `/.dockerignore` - Build context exclusions
- **Testing**: `/tests/test_docker_volumes.py` - Volume mount tests
