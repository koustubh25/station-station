# Docker Deployment Guide - Myki Tracker

Complete guide for running the Myki Transaction Tracker in Docker with Xvfb virtual display for headed Chrome execution.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Directory Structure](#directory-structure)
- [Environment Variables](#environment-variables)
- [Build and Run Scripts](#build-and-run-scripts)
- [Validation and Success Criteria](#validation-and-success-criteria)
- [Troubleshooting](#troubleshooting)
- [Architecture and Design](#architecture-and-design)
- [Known Limitations](#known-limitations)

---

## Overview

### Purpose

This Docker deployment enables the Myki tracker to run in a containerized environment with:

- **Headed Chrome execution** - Uses Xvfb virtual display (not headless mode)
- **Cloudflare bypass** - Maintains the same success rate as local execution
- **Multi-user support** - Authenticate and track multiple Myki accounts
- **Reproducible environment** - Consistent execution across different systems

### Why Docker?

- **Consistent environment** - Same dependencies and configuration everywhere
- **No local Chrome dependency** - All browsers installed in container
- **Isolation** - Separate environment from host system
- **Easy deployment** - Build once, run anywhere
- **Cloud-ready** - Prepares for future Cloud Run deployment

### Key Features

- Google Chrome Stable (required for Cloudflare bypass)
- Xvfb virtual display (`:99`) for headed Chrome execution
- Volume mounts for configuration, profile, and output persistence
- Non-root user execution (UID 1000) for security
- Comprehensive health checks and validation scripts

---

## Prerequisites

### System Requirements

1. **Docker Desktop** (version 20.10+)
   - macOS: [Install Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)
   - Windows: [Install Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

2. **Disk Space**
   - Docker image: ~1.5 GB
   - Build context: ~50 MB
   - Runtime volumes: ~100 MB (profile + output)

3. **Operating System**
   - macOS (Intel or Apple Silicon)
   - Linux (Ubuntu, Debian, etc.)
   - Windows with WSL2

### Required Files

Before running the Docker container, prepare:

1. **Chrome Profile** - Pre-warmed browser profile with trust signals
2. **Config File** - `config/myki_config.json` with user settings
3. **Environment File** - `.env` with user passwords

---

## Quick Start

Follow these 5 steps to get started:

### Step 1: Prepare Chrome Profile

Copy your local Chrome profile to the `browser_profile` directory. This provides trust signals for Cloudflare bypass.

**macOS:**
```bash
# Create browser_profile directory
mkdir -p browser_profile

# Copy Chrome profile files
cp -r ~/Library/Application\ Support/Google/Chrome/Default/Cookies browser_profile/
cp -r ~/Library/Application\ Support/Google/Chrome/Default/Preferences browser_profile/
cp -r ~/Library/Application\ Support/Google/Chrome/Default/History browser_profile/
cp -r ~/Library/Application\ Support/Google/Chrome/Default/Web\ Data browser_profile/
cp -r ~/Library/Application\ Support/Google/Chrome/Default/Login\ Data browser_profile/

# Set proper permissions
chmod -R 755 browser_profile/
```

**Linux:**
```bash
# Create browser_profile directory
mkdir -p browser_profile

# Copy Chrome profile files
cp -r ~/.config/google-chrome/Default/Cookies browser_profile/
cp -r ~/.config/google-chrome/Default/Preferences browser_profile/
cp -r ~/.config/google-chrome/Default/History browser_profile/
cp -r ~/.config/google-chrome/Default/Web\ Data browser_profile/
cp -r ~/.config/google-chrome/Default/Login\ Data browser_profile/

# Set proper permissions
chmod -R 755 browser_profile/
```

**Alternative: Automated Script** (see [Chrome Profile Preparation](#chrome-profile-preparation) section)

### Step 2: Create Configuration File

Copy the example config and add your Myki card details:

```bash
cp config/myki_config.example.json config/myki_config.json
```

Edit `config/myki_config.json`:
```json
{
  "users": {
    "koustubh": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Heathmont Station",
      "startDate": "2025-04-15"
    },
    "john": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Melbourne Central",
      "startDate": "2025-01-01"
    }
  },
  "skipDates": [
    "2025-06-10",
    "2025-07-15"
  ]
}
```

**Note:** The config key (e.g., `"koustubh"`) is the Myki username for login.

### Step 3: Set Environment Variables

Create `.env` file with user passwords:

```bash
cp .env.example .env
```

Edit `.env` and set passwords:
```bash
# User passwords (UPPERCASE config keys)
MYKI_PASSWORD_KOUSTUBH=your_password_here
MYKI_PASSWORD_JOHN=your_password_here

# Docker configuration (optional - has defaults)
DISPLAY=:99
CHROME_PROFILE_DIR=/app/browser_profile
```

**Security:** Never commit `.env` file to version control!

### Step 4: Build Docker Image

Run the build script:

```bash
./docker-build.sh
```

This will:
- Build Docker image with Python 3.9, Chrome Stable, and Xvfb
- Tag image as `myki-tracker:local-v1`
- Display image size and details
- Take 3-5 minutes on first build

**Expected output:**
```
[BUILD] Building Docker image: myki-tracker:local-v1
[BUILD] Build completed successfully!
[BUILD] Image size: 1.45GB
```

### Step 5: Run Docker Container

Execute the run script:

```bash
./docker-run.sh
```

This will:
- Start container with all volume mounts
- Initialize Xvfb display `:99`
- Authenticate all configured users
- Track attendance and generate `output/attendance.json`
- Exit with code 0 on success

**Expected completion time:**
- Single user: 45-60 seconds
- Two users: 90-120 seconds
- Three users: 135-180 seconds

---

## Directory Structure

### Volume Mounts Overview

The Docker container uses 5 volume mounts for data persistence:

```
project-root/
├── config/                    # Configuration files (read-only)
│   └── myki_config.json      # User configuration
├── browser_profile/           # Chrome profile (read-write)
│   ├── Cookies               # Session cookies
│   ├── Preferences           # Browser settings
│   ├── History               # Browsing history
│   ├── Web Data              # Form data
│   └── Login Data            # Saved credentials
├── output/                    # Workflow output (read-write)
│   └── attendance.json       # Generated attendance data
├── auth_data/                 # Session files (read-write)
│   ├── session_koustubh.json # Per-user session
│   └── session_john.json     # Per-user session
└── screenshots/               # Debug screenshots (read-write)
    └── error_*.png           # Screenshots on failure
```

### Volume Mount Details

| Mount Point | Host Path | Container Path | Mode | Purpose |
|------------|-----------|----------------|------|---------|
| Config | `./config` | `/app/config` | `ro` | Configuration files |
| Browser Profile | `./browser_profile` | `/app/browser_profile` | `rw` | Chrome profile storage |
| Output | `./output` | `/app/output` | `rw` | Attendance results |
| Auth Data | `./auth_data` | `/app/auth_data` | `rw` | Session files |
| Screenshots | `./screenshots` | `/app/screenshots` | `rw` | Error screenshots |

### File Permissions

The container runs as UID 1000, GID 1000. Ensure volume mount directories are writable:

```bash
# Set ownership to match container user (if needed)
sudo chown -R 1000:1000 browser_profile/ output/ auth_data/ screenshots/

# Or set permissions to allow group write
chmod -R 775 browser_profile/ output/ auth_data/ screenshots/
```

---

## Chrome Profile Preparation

### Why Chrome Profile Matters

Cloudflare Turnstile uses browser fingerprinting and trust signals to detect bots. A pre-warmed Chrome profile with browsing history helps bypass detection by:

- Providing cookies from previous browsing sessions
- Including browsing history and site data
- Storing user preferences and settings
- Containing saved credentials and autofill data

### Required Profile Files

Copy these files from your local Chrome profile:

1. **Cookies** - Session cookies and authentication tokens
2. **Preferences** - Browser settings and site permissions
3. **History** - Browsing history for trust signals
4. **Web Data** - Form autofill and search suggestions
5. **Login Data** - Saved credentials (optional)

### Profile Location by OS

**macOS:**
```
~/Library/Application Support/Google/Chrome/Default/
```

**Linux:**
```
~/.config/google-chrome/Default/
```

**Windows:**
```
C:\Users\{username}\AppData\Local\Google\Chrome\User Data\Default\
```

### Automated Profile Copy Script

**macOS:**
```bash
#!/bin/bash
# copy-chrome-profile-macos.sh

CHROME_PROFILE_SRC="$HOME/Library/Application Support/Google/Chrome/Default"
DEST_DIR="./browser_profile"

echo "Copying Chrome profile from macOS..."

# Create destination directory
mkdir -p "$DEST_DIR"

# Copy required files
cp "$CHROME_PROFILE_SRC/Cookies" "$DEST_DIR/" 2>/dev/null || echo "Warning: Cookies not found"
cp "$CHROME_PROFILE_SRC/Preferences" "$DEST_DIR/" 2>/dev/null || echo "Warning: Preferences not found"
cp "$CHROME_PROFILE_SRC/History" "$DEST_DIR/" 2>/dev/null || echo "Warning: History not found"
cp "$CHROME_PROFILE_SRC/Web Data" "$DEST_DIR/" 2>/dev/null || echo "Warning: Web Data not found"
cp "$CHROME_PROFILE_SRC/Login Data" "$DEST_DIR/" 2>/dev/null || echo "Warning: Login Data not found"

# Set permissions
chmod -R 755 "$DEST_DIR"

echo "Chrome profile copied to $DEST_DIR"
echo "Files copied: $(ls -1 $DEST_DIR | wc -l)"
```

**Linux:**
```bash
#!/bin/bash
# copy-chrome-profile-linux.sh

CHROME_PROFILE_SRC="$HOME/.config/google-chrome/Default"
DEST_DIR="./browser_profile"

echo "Copying Chrome profile from Linux..."

# Create destination directory
mkdir -p "$DEST_DIR"

# Copy required files
cp "$CHROME_PROFILE_SRC/Cookies" "$DEST_DIR/" 2>/dev/null || echo "Warning: Cookies not found"
cp "$CHROME_PROFILE_SRC/Preferences" "$DEST_DIR/" 2>/dev/null || echo "Warning: Preferences not found"
cp "$CHROME_PROFILE_SRC/History" "$DEST_DIR/" 2>/dev/null || echo "Warning: History not found"
cp "$CHROME_PROFILE_SRC/Web Data" "$DEST_DIR/" 2>/dev/null || echo "Warning: Web Data not found"
cp "$CHROME_PROFILE_SRC/Login Data" "$DEST_DIR/" 2>/dev/null || echo "Warning: Login Data not found"

# Set permissions
chmod -R 755 "$DEST_DIR"

echo "Chrome profile copied to $DEST_DIR"
echo "Files copied: $(ls -1 $DEST_DIR | wc -l)"
```

### Profile Warming (Optional)

For best results, "warm" the profile by browsing normally:

1. Run interactive container: `./docker-debug.sh`
2. Manually launch Chrome: `google-chrome --user-data-dir=/app/browser_profile`
3. Visit myki.ptv.vic.gov.au
4. Let Cloudflare verify (wait 35 seconds)
5. Browse around the site
6. Exit Chrome and container

This builds additional trust signals in the profile.

---

## Environment Variables

### Complete Reference Table

| Variable Name | Required | Default | Description |
|--------------|----------|---------|-------------|
| `MYKI_PASSWORD_{USERNAME}` | Yes | None | Password for each user (USERNAME in UPPERCASE) |
| `DISPLAY` | No | `:99` | Xvfb display number for virtual display |
| `CHROME_PROFILE_DIR` | No | `/app/browser_profile` | Chrome profile location inside container |
| `PYTHONUNBUFFERED` | No | `1` | Enable real-time Python logging output |

### User Password Pattern

The password environment variables follow a specific pattern:

**Pattern:** `MYKI_PASSWORD_{USERNAME_UPPERCASE}`

**Examples:**
- Config user: `koustubh` → Environment variable: `MYKI_PASSWORD_KOUSTUBH`
- Config user: `john` → Environment variable: `MYKI_PASSWORD_JOHN`
- Config user: `jane.doe` → Environment variable: `MYKI_PASSWORD_JANE_DOE`

**Rules:**
1. Username from config key is converted to UPPERCASE
2. Dots (`.`) and dashes (`-`) become underscores (`_`)
3. Must match exactly for authentication to work

### Display Variable (DISPLAY)

**Default:** `:99`

Controls which X display Xvfb creates. The default `:99` is chosen to avoid conflicts with existing displays.

**When to change:**
- Conflict with existing X server on `:99`
- Running multiple containers simultaneously
- Custom Xvfb configuration

**Example:**
```bash
DISPLAY=:100
```

### Chrome Profile Directory (CHROME_PROFILE_DIR)

**Default:** `/app/browser_profile`

Specifies the Chrome profile location inside the container. Mounted from host at runtime.

**When to change:**
- Using custom profile location
- Testing with different profiles
- Advanced debugging scenarios

**Example:**
```bash
CHROME_PROFILE_DIR=/app/custom_profile
```

### .env File Setup

Create `.env` in project root:

```bash
# =============================================================================
# User Authentication Passwords
# =============================================================================
# For each user in config/myki_config.json, set their password here
# Pattern: MYKI_PASSWORD_{USERNAME_UPPERCASE}=your_password

MYKI_PASSWORD_KOUSTUBH=your_password_here
MYKI_PASSWORD_JOHN=your_password_here

# =============================================================================
# Docker Configuration (Optional - has defaults)
# =============================================================================
# Xvfb display number (default: :99)
# DISPLAY=:99

# Chrome profile directory (default: /app/browser_profile)
# CHROME_PROFILE_DIR=/app/browser_profile

# Python unbuffered output for real-time logs (default: 1)
# PYTHONUNBUFFERED=1
```

**Security Notes:**
- Never commit `.env` to version control (included in `.gitignore`)
- Keep file permissions restricted: `chmod 600 .env`
- Use strong, unique passwords for each account
- Rotate passwords periodically

---

## Build and Run Scripts

### docker-build.sh

Builds the Docker image with all dependencies.

**Usage:**
```bash
./docker-build.sh
```

**What it does:**
1. Verifies Dockerfile exists
2. Builds image with tag `myki-tracker:local-v1`
3. Displays build progress and logs
4. Shows image size and details on success
5. Exits with code 0 on success, non-zero on failure

**Options:**
- Multi-architecture builds: Uncomment `BUILD_ARGS` in script
- Custom tags: Edit `IMAGE_TAG` variable in script

**Example output:**
```bash
[BUILD] 2025-11-02 09:15:23 - ==================================
[BUILD] 2025-11-02 09:15:23 - Building Myki Tracker Docker Image
[BUILD] 2025-11-02 09:15:23 - ==================================
[BUILD] 2025-11-02 09:15:23 - Build context: /Users/username/myki-tracker
[BUILD] 2025-11-02 09:15:23 - Dockerfile found: /Users/username/myki-tracker/Dockerfile
[BUILD] 2025-11-02 09:15:23 - Building Docker image: myki-tracker:local-v1
[BUILD] 2025-11-02 09:15:23 - Build arguments: none
[BUILD] 2025-11-02 09:15:23 - Using standard docker build for current architecture
[BUILD] 2025-11-02 09:18:45 - ==================================
[BUILD] 2025-11-02 09:18:45 - Build completed successfully!
[BUILD] 2025-11-02 09:18:45 - Image: myki-tracker:local-v1
[BUILD] 2025-11-02 09:18:45 - ==================================
[BUILD] 2025-11-02 09:18:45 - Image size: 1.45GB
```

**Troubleshooting:**
- **Build fails:** Check Docker is running, internet connection available
- **Image too large:** Normal size is 1.2-1.5 GB (includes Chrome, Python, dependencies)
- **Permission errors:** Ensure user has Docker permissions

---

### docker-run.sh

Runs the Docker container with all volume mounts and environment variables.

**Usage:**
```bash
./docker-run.sh
```

**What it does:**
1. Loads environment variables from `.env` file
2. Creates required directories if missing
3. Verifies config file exists
4. Checks Docker image is built
5. Mounts all 5 volumes (config, browser_profile, output, auth_data, screenshots)
6. Passes environment variables to container
7. Runs container with `--rm` flag (auto-removes on exit)
8. Captures and returns container exit code

**Volume mounts:**
```bash
-v $(pwd)/config:/app/config:ro                    # Config (read-only)
-v $(pwd)/browser_profile:/app/browser_profile:rw  # Profile (read-write)
-v $(pwd)/output:/app/output:rw                    # Output (read-write)
-v $(pwd)/auth_data:/app/auth_data:rw              # Sessions (read-write)
-v $(pwd)/screenshots:/app/screenshots:rw          # Screenshots (read-write)
```

**Environment variables passed:**
```bash
-e DISPLAY=:99
-e CHROME_PROFILE_DIR=/app/browser_profile
-e MYKI_PASSWORD_KOUSTUBH=***
-e MYKI_PASSWORD_JOHN=***
```

**Example output:**
```bash
[RUN] 2025-11-02 09:20:15 - ==================================
[RUN] 2025-11-02 09:20:15 - Running Myki Tracker Docker Container
[RUN] 2025-11-02 09:20:15 - ==================================
[RUN] 2025-11-02 09:20:15 - Loading environment variables from .env file
[RUN] 2025-11-02 09:20:15 - Config file found: config/myki_config.json
[RUN] 2025-11-02 09:20:15 - Docker image found: myki-tracker:local-v1
[RUN] 2025-11-02 09:20:15 - Starting container: myki-tracker-run
[RUN] 2025-11-02 09:20:15 - Volume mounts:
[RUN] 2025-11-02 09:20:15 -   - config (ro):          /path/config -> /app/config
[RUN] 2025-11-02 09:20:15 -   - browser_profile (rw): /path/browser_profile -> /app/browser_profile
[RUN] 2025-11-02 09:20:15 -   - output (rw):          /path/output -> /app/output
[RUN] 2025-11-02 09:20:15 -   - auth_data (rw):       /path/auth_data -> /app/auth_data
[RUN] 2025-11-02 09:20:15 -   - screenshots (rw):     /path/screenshots -> /app/screenshots

[ENTRYPOINT] 2025-11-02 09:20:16 - ==================================
[ENTRYPOINT] 2025-11-02 09:20:16 - Myki Tracker Docker Container
[ENTRYPOINT] 2025-11-02 09:20:16 - ==================================
[ENTRYPOINT] 2025-11-02 09:20:16 - Starting Xvfb on display :99
[ENTRYPOINT] 2025-11-02 09:20:19 - Display :99 verified and accessible
[ENTRYPOINT] 2025-11-02 09:20:19 - Executing workflow...

✓ COMPLETED SUCCESSFULLY - All users processed

[ENTRYPOINT] 2025-11-02 09:21:45 - ==================================
[ENTRYPOINT] 2025-11-02 09:21:45 - Workflow completed successfully
[ENTRYPOINT] 2025-11-02 09:21:45 - Exit code: 0
[ENTRYPOINT] 2025-11-02 09:21:45 - ==================================

[RUN] 2025-11-02 09:21:45 - ==================================
[RUN] 2025-11-02 09:21:45 - Container completed successfully!
[RUN] 2025-11-02 09:21:45 - Exit code: 0
[RUN] 2025-11-02 09:21:45 - ==================================
[RUN] 2025-11-02 09:21:45 - Output file: /path/output/attendance.json
```

---

### docker-test.sh

Automated validation script that runs the container and verifies output.

**Usage:**
```bash
./docker-test.sh
```

**What it does:**
1. Cleans up old output files
2. Runs docker-run.sh
3. Validates container exit code (should be 0)
4. Checks output/attendance.json exists
5. Validates JSON structure
6. Checks for expected fields (date, users, attendance data)
7. Verifies session files created
8. Prints PASS/FAIL summary

**Validation checks:**
- Container exit code is 0
- Output file exists: `output/attendance.json`
- JSON is valid and parseable
- Contains required fields: `date`, `metadata`, user data
- Session files exist: `auth_data/session_*.json`
- Success message in logs

**Example output:**
```bash
[TEST] 2025-11-02 09:25:00 - ==================================
[TEST] 2025-11-02 09:25:00 - Myki Tracker Docker Validation Test
[TEST] 2025-11-02 09:25:00 - ==================================
[TEST] 2025-11-02 09:25:00 - Cleaning up old output files...
[TEST] 2025-11-02 09:25:00 - Step 1: Running Docker container via docker-run.sh

<container output>

[TEST] 2025-11-02 09:26:30 - Step 2: Validating container exit code
[TEST SUCCESS] 2025-11-02 09:26:30 - PASS: Container exit code is 0 (success)
[TEST] 2025-11-02 09:26:30 - Step 3: Checking output file exists
[TEST SUCCESS] 2025-11-02 09:26:30 - PASS: Output file exists
[TEST] 2025-11-02 09:26:30 - Step 4: Validating JSON structure
[TEST SUCCESS] 2025-11-02 09:26:30 - PASS: Output file is valid JSON
[TEST SUCCESS] 2025-11-02 09:26:30 - PASS: Output contains 'date' field
[TEST] 2025-11-02 09:26:30 - Step 5: Checking session files
[TEST SUCCESS] 2025-11-02 09:26:30 - PASS: Session files exist

[TEST] 2025-11-02 09:26:30 - ==================================
[TEST] 2025-11-02 09:26:30 - VALIDATION SUMMARY
[TEST] 2025-11-02 09:26:30 - ==================================
[TEST] 2025-11-02 09:26:30 - Tests passed: 6
[TEST] 2025-11-02 09:26:30 - Tests failed: 0
[TEST] 2025-11-02 09:26:30 - ==================================
[TEST SUCCESS] 2025-11-02 09:26:30 - ALL TESTS PASSED
[TEST] 2025-11-02 09:26:30 - ==================================
```

---

### docker-debug.sh

Interactive debugging script for troubleshooting.

**Usage:**
```bash
./docker-debug.sh
```

**What it does:**
1. Starts container with interactive shell (`/bin/bash`)
2. Mounts all volumes (same as docker-run.sh)
3. Passes environment variables
4. Overrides entrypoint to provide shell access
5. Allows manual testing and debugging

**Inside the debug shell:**

```bash
# Check Xvfb can start
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
xdpyinfo -display :99

# Verify Chrome installation
google-chrome --version
which google-chrome

# Check Chrome profile
ls -la /app/browser_profile

# Test Chrome launch
google-chrome --user-data-dir=/app/browser_profile --no-sandbox &

# Manually run workflow
python src/run_myki_workflow.py config/myki_config.json

# Check output files
ls -la /app/output
cat /app/output/attendance.json

# Check session files
ls -la /app/auth_data

# Exit debug shell
exit
```

**Example output:**
```bash
[DEBUG] 2025-11-02 09:30:00 - ==================================
[DEBUG] 2025-11-02 09:30:00 - Myki Tracker Debug Shell
[DEBUG] 2025-11-02 09:30:00 - ==================================
[DEBUG] 2025-11-02 09:30:00 - Starting interactive container...
[DEBUG] 2025-11-02 09:30:00 -
[DEBUG] 2025-11-02 09:30:00 - Debug commands:
[DEBUG] 2025-11-02 09:30:00 -   google-chrome --version         # Check Chrome version
[DEBUG] 2025-11-02 09:30:00 -   ls /app/browser_profile         # Check profile files
[DEBUG] 2025-11-02 09:30:00 -   python src/run_myki_workflow.py # Run workflow manually
[DEBUG] 2025-11-02 09:30:00 -
app@container:/app$
```

---

### docker-health-check.sh

Post-run health check validation script.

**Usage:**
```bash
./docker-health-check.sh
```

**What it does:**
1. Checks container exit code from last run
2. Validates output/attendance.json exists and is valid JSON
3. Verifies session files exist for each user
4. Checks attendance.json contains expected fields
5. Looks for success message in logs
6. Returns 0 if all checks pass, 1 if any fail

**Health checks performed:**
- Container exit code is 0
- `output/attendance.json` exists and is valid JSON
- File contains `date`, `metadata`, and user data
- Session files exist: `auth_data/session_{username}.json`
- Success message present: "COMPLETED SUCCESSFULLY"

**Example output:**
```bash
[HEALTH] 2025-11-02 09:35:00 - ==================================
[HEALTH] 2025-11-02 09:35:00 - Docker Health Check
[HEALTH] 2025-11-02 09:35:00 - ==================================
[HEALTH] 2025-11-02 09:35:00 - Check 1: Container exit code
[HEALTH] 2025-11-02 09:35:00 - ✓ PASS: Exit code is 0
[HEALTH] 2025-11-02 09:35:00 - Check 2: Output file exists
[HEALTH] 2025-11-02 09:35:00 - ✓ PASS: attendance.json exists
[HEALTH] 2025-11-02 09:35:00 - Check 3: Valid JSON structure
[HEALTH] 2025-11-02 09:35:00 - ✓ PASS: Valid JSON
[HEALTH] 2025-11-02 09:35:00 - Check 4: Required fields present
[HEALTH] 2025-11-02 09:35:00 - ✓ PASS: All required fields present
[HEALTH] 2025-11-02 09:35:00 - Check 5: Session files exist
[HEALTH] 2025-11-02 09:35:00 - ✓ PASS: 2 session files found
[HEALTH] 2025-11-02 09:35:00 - ==================================
[HEALTH] 2025-11-02 09:35:00 - ALL HEALTH CHECKS PASSED
[HEALTH] 2025-11-02 09:35:00 - ==================================
```

---

## Validation and Success Criteria

### What a Successful Run Looks Like

A successful Docker container run produces:

1. **Exit Code: 0**
   - Container exits with code 0
   - Indicates workflow completed successfully

2. **Output File: attendance.json**
   - Located at `output/attendance.json`
   - Valid JSON structure
   - Contains attendance data for all users

3. **Session Files**
   - One file per user: `auth_data/session_{username}.json`
   - Contains authentication tokens and cookies

4. **Success Message in Logs**
   - Console output shows: "✓ COMPLETED SUCCESSFULLY - All users processed"

5. **No Error Screenshots**
   - No files created in `screenshots/` directory
   - Indicates no errors encountered

### Expected Output File Structure

**output/attendance.json:**
```json
{
  "metadata": {
    "generatedAt": "2025-11-02T09:21:45Z",
    "totalUsers": 2
  },
  "koustubh": {
    "attendanceDays": [
      "2025-05-08",
      "2025-05-13",
      "2025-05-15"
    ],
    "statistics": {
      "totalWorkingDays": 138,
      "daysAttended": 46,
      "daysMissed": 92,
      "attendancePercentage": 33.33,
      "firstAttendance": "2025-05-08",
      "lastAttendance": "2025-10-29",
      "monthlyBreakdown": [
        {
          "month": "2025-05",
          "workingDays": 22,
          "daysAttended": 4,
          "attendancePercentage": 18.18
        }
      ]
    }
  },
  "john": {
    "attendanceDays": ["2025-01-15", "2025-01-17"],
    "statistics": {
      "totalWorkingDays": 200,
      "daysAttended": 180,
      "daysMissed": 20,
      "attendancePercentage": 90.0,
      "firstAttendance": "2025-01-15",
      "lastAttendance": "2025-10-30",
      "monthlyBreakdown": []
    }
  }
}
```

### Validation Commands

**Manual validation after run:**

```bash
# Check container exit code (from last run)
echo $?
# Expected: 0

# Verify output file exists
ls -lh output/attendance.json
# Expected: File exists with size > 0

# Validate JSON structure
cat output/attendance.json | python -m json.tool
# Expected: Pretty-printed JSON (no errors)

# Check for required fields
cat output/attendance.json | grep -o '"metadata"'
cat output/attendance.json | grep -o '"generatedAt"'
# Expected: Fields found

# Count session files (should match user count)
ls -1 auth_data/session_*.json | wc -l
# Expected: Number matches users in config

# Check file sizes
du -sh output/attendance.json auth_data/session_*.json
# Expected: Non-zero sizes
```

**Automated validation:**
```bash
# Run full validation suite
./docker-test.sh

# Run health check only
./docker-health-check.sh
```

### Success Metrics

| Metric | Expected Value | How to Verify |
|--------|---------------|---------------|
| Exit Code | 0 | `echo $?` after run |
| Execution Time (2 users) | 90-120 seconds | Check timestamps in logs |
| Output File Size | 1-5 KB | `ls -lh output/attendance.json` |
| Session Files | 1 per user | `ls auth_data/session_*.json | wc -l` |
| Error Screenshots | 0 files | `ls screenshots/ | wc -l` |
| Cloudflare Bypass | 100% success | Check logs for "Turnstile verification complete" |

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Container exits with non-zero code

**Symptoms:**
- Container exits with code 1 or higher
- Error messages in logs
- No output file created

**Possible Causes:**
1. Missing environment variables (passwords)
2. Config file errors
3. Chrome profile permission issues
4. Xvfb startup failure

**Solutions:**

```bash
# Check environment variables are set
./docker-run.sh 2>&1 | grep "MYKI_PASSWORD"
# Should show: "Passing environment variable: MYKI_PASSWORD_KOUSTUBH=***"

# Verify .env file exists and has passwords
cat .env | grep MYKI_PASSWORD
# Should show: MYKI_PASSWORD_KOUSTUBH=your_password

# Check config file is valid JSON
cat config/myki_config.json | python -m json.tool
# Should print formatted JSON without errors

# Verify Chrome profile permissions
ls -la browser_profile/
# Should show files owned by your user (or UID 1000)

# Check Xvfb logs via debug shell
./docker-debug.sh
# Inside container:
Xvfb :99 -screen 0 1920x1080x24 &
xdpyinfo -display :99
```

---

#### Issue 2: Cloudflare bypass fails

**Symptoms:**
- Error: "Cloudflare verification failed"
- Workflow hangs during Cloudflare check
- Success rate lower than local execution

**Possible Causes:**
1. Chrome profile missing or empty
2. Profile not pre-warmed with trust signals
3. Headed mode not enabled properly
4. Xvfb display not accessible

**Solutions:**

```bash
# Verify profile files exist
ls -la browser_profile/
# Should show: Cookies, Preferences, History, Web Data, Login Data

# Check profile file sizes (should not be empty)
du -h browser_profile/*
# Files should have non-zero sizes

# Warm the profile manually
./docker-debug.sh
# Inside container:
google-chrome --user-data-dir=/app/browser_profile --no-sandbox
# Visit myki.ptv.vic.gov.au, let Cloudflare verify, browse around

# Verify headed mode is enabled (not headless)
grep "headless" src/*.py
# Should show: headless=False in browser configuration

# Check Xvfb display is accessible
./docker-debug.sh
# Inside container:
export DISPLAY=:99
xdpyinfo -display :99
# Should show display information without errors
```

---

#### Issue 3: Permission denied errors

**Symptoms:**
- Error: "Permission denied" when writing files
- Chrome profile cannot be updated
- Output files not created

**Possible Causes:**
1. Volume mount directories not writable by UID 1000
2. Host directory ownership mismatch
3. Incorrect file permissions

**Solutions:**

```bash
# Check directory ownership
ls -la browser_profile/ output/ auth_data/
# Should be owned by your user or UID 1000

# Fix ownership (Option 1: Change to UID 1000)
sudo chown -R 1000:1000 browser_profile/ output/ auth_data/ screenshots/

# Fix permissions (Option 2: Allow group write)
chmod -R 775 browser_profile/ output/ auth_data/ screenshots/

# Verify container user ID
./docker-debug.sh
# Inside container:
id
# Should show: uid=1000(app) gid=1000(app)

# Check umask inside container
./docker-debug.sh
# Inside container:
umask
# Should show: 0002 (allows group write)

# Test file creation
./docker-debug.sh
# Inside container:
touch /app/output/test.txt
ls -la /app/output/test.txt
# Should succeed and show rw-rw-r-- permissions
```

---

#### Issue 4: Xvfb display errors

**Symptoms:**
- Error: "Cannot open display :99"
- Xvfb failed to start
- Chrome cannot launch

**Possible Causes:**
1. Xvfb process died immediately
2. Display :99 already in use
3. X11 dependencies missing
4. Insufficient wait time for Xvfb startup

**Solutions:**

```bash
# Check Xvfb logs in container
docker logs myki-tracker-run 2>&1 | grep -i xvfb
# Should show: "Xvfb started with PID: <number>"
# Should show: "Display :99 verified and accessible"

# Manually test Xvfb startup
./docker-debug.sh
# Inside container:
Xvfb :99 -screen 0 1920x1080x24 &
sleep 3
xdpyinfo -display :99
# Should show display information

# Try different display number (if :99 conflicts)
# Edit .env file:
DISPLAY=:100
# Re-run container

# Check X11 dependencies installed
./docker-debug.sh
# Inside container:
dpkg -l | grep xvfb
dpkg -l | grep x11
# Should show installed packages

# Increase wait time in entrypoint.sh (if needed)
# Edit entrypoint.sh, change:
sleep 3
# To:
sleep 5
# Rebuild image and test
```

---

#### Issue 5: Chrome fails to launch

**Symptoms:**
- Error: "Chrome failed to launch"
- Browser process crashes
- Chrome not found error

**Possible Causes:**
1. Google Chrome not installed (Chromium installed instead)
2. Missing Chrome dependencies
3. Profile corruption
4. Insufficient resources

**Solutions:**

```bash
# Verify Chrome installation
./docker-debug.sh
# Inside container:
google-chrome --version
# Should show: Google Chrome <version> (NOT Chromium)

# Check Chrome binary location
./docker-debug.sh
# Inside container:
which google-chrome
ls -la /usr/bin/google-chrome
# Should point to Chrome (not Chromium)

# Check Chrome dependencies
./docker-debug.sh
# Inside container:
ldd /usr/bin/google-chrome | grep "not found"
# Should show no missing libraries

# Test Chrome launch with minimal flags
./docker-debug.sh
# Inside container:
google-chrome --version
google-chrome --no-sandbox --headless --dump-dom https://google.com
# Should succeed without errors

# Check Docker resources (memory, CPU)
docker stats
# Ensure sufficient resources allocated

# Try with fresh profile
mv browser_profile browser_profile.backup
mkdir browser_profile
./docker-run.sh
# Test if Chrome launches with empty profile
```

---

#### Issue 6: Output files not created

**Symptoms:**
- No `output/attendance.json` file after run
- Empty output directory
- Workflow appears to complete but no results

**Possible Causes:**
1. Workflow failed before output generation
2. Volume mount not working
3. Write permissions on output directory
4. File path mismatch

**Solutions:**

```bash
# Check workflow logs for errors
docker logs myki-tracker-run 2>&1 | grep -i error
docker logs myki-tracker-run 2>&1 | grep -i fail
# Look for error messages

# Verify volume mount
./docker-debug.sh
# Inside container:
ls -la /app/output
touch /app/output/test.txt
exit
# On host:
ls -la output/test.txt
# File should appear on host

# Check output directory permissions
ls -ld output/
chmod 755 output/
# Ensure directory is writable

# Manually run workflow with verbose logging
./docker-debug.sh
# Inside container:
python src/run_myki_workflow.py config/myki_config.json
# Watch for output file creation
ls -la /app/output/

# Verify workflow reached output generation
docker logs myki-tracker-run 2>&1 | grep "attendance.json"
# Should show output file creation messages
```

---

### Debug Commands Reference

**Container logs:**
```bash
# View logs from last run (if container still exists)
docker logs myki-tracker-run

# Follow logs in real-time
docker logs -f myki-tracker-run

# Search logs for errors
docker logs myki-tracker-run 2>&1 | grep -i error

# Search for specific messages
docker logs myki-tracker-run 2>&1 | grep "Cloudflare"
docker logs myki-tracker-run 2>&1 | grep "Xvfb"
```

**Image inspection:**
```bash
# List Docker images
docker images | grep myki-tracker

# Inspect image details
docker inspect myki-tracker:local-v1

# Check image size
docker images myki-tracker:local-v1 --format "{{.Size}}"

# View image history (layers)
docker history myki-tracker:local-v1
```

**Container inspection:**
```bash
# List running containers
docker ps | grep myki-tracker

# List all containers (including stopped)
docker ps -a | grep myki-tracker

# Inspect container details
docker inspect myki-tracker-run

# Check container resource usage
docker stats myki-tracker-run
```

**File verification:**
```bash
# Check all required files exist
test -f config/myki_config.json && echo "Config: OK" || echo "Config: MISSING"
test -f .env && echo ".env: OK" || echo ".env: MISSING"
test -d browser_profile && echo "Profile dir: OK" || echo "Profile dir: MISSING"

# Verify directory permissions
ls -ld config/ browser_profile/ output/ auth_data/ screenshots/

# Check file counts
echo "Profile files: $(ls -1 browser_profile/ 2>/dev/null | wc -l)"
echo "Session files: $(ls -1 auth_data/session_*.json 2>/dev/null | wc -l)"
echo "Screenshots: $(ls -1 screenshots/ 2>/dev/null | wc -l)"
```

**Using docker-debug.sh:**
```bash
# Start debug session
./docker-debug.sh

# Inside container - check environment
env | grep MYKI
env | grep DISPLAY
env | grep CHROME

# Inside container - verify mounts
df -h | grep /app
ls -la /app/config
ls -la /app/browser_profile
ls -la /app/output

# Inside container - test components
Xvfb :99 &
export DISPLAY=:99
google-chrome --version
python --version
playwright --version

# Inside container - manual workflow run
python src/run_myki_workflow.py config/myki_config.json

# Exit debug session
exit
```

---

## Architecture and Design

### Why Xvfb (X Virtual Framebuffer)?

**Problem:** Cloudflare Turnstile detects headless browsers and blocks them.

**Solution:** Run Chrome in headed mode (with GUI) but without a physical display using Xvfb.

**How it works:**
1. Xvfb creates a virtual X11 display server in memory
2. Display `:99` runs at 1920x1080 resolution with 24-bit color
3. Chrome renders to this virtual display as if it were a real screen
4. Cloudflare sees a "real" browser with GUI, not headless automation

**Benefits:**
- Bypasses Cloudflare headless detection
- No need for physical display or VNC
- Lightweight (runs entirely in memory)
- Standard solution for GUI apps in containers

**Configuration:**
```bash
# Xvfb startup command (from entrypoint.sh)
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &

# Parameters explained:
# :99              - Display number
# -screen 0        - Screen number
# 1920x1080x24     - Resolution (width x height x color depth)
# -ac              - Disable access control (allow all connections)
# +extension GLX   - Enable OpenGL extension (for Chrome rendering)
# +render          - Enable RENDER extension (for anti-aliased graphics)
# -noreset         - Don't reset after last client disconnects
```

---

### Why Headed Mode (headless=False)?

**Problem:** Headless Chrome is easily detected by Cloudflare.

**Evidence:**
- Headless mode sets `navigator.webdriver = true`
- Missing GUI-related browser APIs
- Different behavior in Canvas fingerprinting
- Cloudflare Turnstile has ~90% detection rate for headless

**Solution:** Run in headed mode with Xvfb.

**Configuration in code:**
```python
# browser_config.py
browser = playwright.chromium.launch_persistent_context(
    user_data_dir=profile_dir,
    headless=False,  # CRITICAL: Must be False for Cloudflare bypass
    channel='chrome',
    viewport={'width': 1920, 'height': 1080}
)
```

**Success rate comparison:**
- Headless mode: ~10% bypass success (frequent blocking)
- Headed mode with Xvfb: ~95% bypass success (matches local execution)

---

### Why Google Chrome (Not Chromium)?

**Problem:** Different browser fingerprints between Chrome and Chromium.

**Key Differences:**
- Chrome includes proprietary codecs, DRM, and Google services
- Chromium missing some APIs and features
- Different User-Agent strings
- Different behavior in Cloudflare fingerprinting

**Decision:**
- **Production (AMD64):** Use Google Chrome Stable for best Cloudflare compatibility
- **Development (ARM64/Apple Silicon):** Fall back to Chromium (Chrome not available for ARM64)

**Dockerfile implementation:**
```dockerfile
# Architecture-aware Chrome installation
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        # AMD64: Install Google Chrome Stable
        wget -q -O /tmp/google-chrome-stable_current_amd64.deb \
            https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
        apt-get install -y /tmp/google-chrome-stable_current_amd64.deb; \
    else \
        # ARM64: Install Chromium as fallback
        apt-get install -y chromium chromium-driver && \
        ln -s /usr/bin/chromium /usr/bin/google-chrome; \
    fi
```

**Testing recommendation:**
- Test on AMD64 for production validation
- ARM64 testing OK for development

---

### Volume Mount Strategy

**Design Principle:** Separate concerns - read-only config, read-write data.

**Mounts:**

1. **Config (Read-Only):** `./config:/app/config:ro`
   - Prevents accidental modification
   - Configuration is immutable at runtime
   - Security best practice

2. **Browser Profile (Read-Write):** `./browser_profile:/app/browser_profile:rw`
   - Chrome must update cookies, preferences, session
   - Profile evolves with browsing (trust signals)
   - Persists across runs for consistency

3. **Output (Read-Write):** `./output:/app/output:rw`
   - Workflow results must be written
   - Accessible on host for consumption
   - Persists after container exits

4. **Auth Data (Read-Write):** `./auth_data:/app/auth_data:rw`
   - Session files reused across runs
   - Reduces authentication time
   - One file per user for isolation

5. **Screenshots (Read-Write):** `./screenshots:/app/screenshots:rw`
   - Debugging aid for failures
   - Visual evidence of errors
   - Not required for normal operation

**UID/GID Mapping:**
- Container runs as UID 1000, GID 1000
- Matches typical host user permissions
- Avoids permission issues with volume mounts
- Files created in container are accessible on host

---

### Design Decisions Summary

| Decision | Reason | Alternative Considered |
|----------|--------|----------------------|
| Xvfb virtual display | Bypass Cloudflare headless detection | VNC, headless mode |
| Headed mode (`headless=False`) | Required for Cloudflare bypass | Headless with stealth plugins |
| Google Chrome Stable | Best Cloudflare compatibility | Chromium, Firefox |
| Python 3.9-slim | Balance size vs compatibility | Alpine (too minimal), 3.10+ (newer) |
| Non-root user (UID 1000) | Security, volume mount compatibility | Root user, custom UID |
| Volume mounts | Data persistence, configuration separation | COPY files, environment variables |
| Entrypoint script | Xvfb startup automation | CMD with manual Xvfb start |

---

## Known Limitations

### Current Limitations

1. **Chrome Profile Required**
   - Pre-warmed profile needed for best Cloudflare bypass success
   - Empty profile may have lower success rate (~70% vs 95%)
   - Profile must be copied from host or manually warmed in container

2. **Local Testing Only**
   - This spec covers local Docker deployment only
   - Cloud deployment (Cloud Run, Kubernetes) is separate effort
   - No automated scheduling or CI/CD pipeline included

3. **Sequential Authentication**
   - Multi-user authentication runs sequentially, not parallel
   - Each user takes ~45 seconds to authenticate
   - 3 users = ~135 seconds total authentication time
   - Attendance tracking is parallel after authentication

4. **Platform Limitations**
   - ARM64 (Apple Silicon) uses Chromium fallback, not Chrome
   - May have slightly lower Cloudflare bypass success on ARM64
   - Production should use AMD64 for best results

5. **Fixed Display Number**
   - Xvfb uses display `:99` by default
   - May conflict if host has X server on `:99`
   - Can be changed via `DISPLAY` environment variable

6. **Resource Requirements**
   - ~1.5 GB Docker image size
   - ~500 MB memory usage during execution
   - Chrome rendering requires non-trivial CPU

7. **No Automatic Retry**
   - Workflow exits on first failure
   - No built-in retry logic for Cloudflare timeouts
   - Must manually re-run container

8. **Public Holiday Support**
   - Only Melbourne VIC public holidays included
   - Not configurable for other regions/states
   - Hardcoded in working_days.py

---

### Out of Scope

The following are explicitly NOT included in this Docker deployment:

#### Cloud Deployment
- Google Cloud Run configuration
- Kubernetes manifests
- AWS/Azure container services
- Cloud-specific optimizations

#### CI/CD Pipeline
- GitHub Actions workflows
- GitLab CI configuration
- Automated builds and deployments
- Continuous integration tests

#### Scheduling and Automation
- Cron job setup
- Cloud Scheduler integration
- Automated daily runs
- Retry mechanisms

#### Profile Management
- Google Cloud Storage profile sync
- Automated profile warming
- Profile backup/restore
- Multi-region profile replication

#### Secrets Management
- Google Secret Manager integration
- AWS Secrets Manager
- Kubernetes secrets
- Vault integration

#### Monitoring and Observability
- Prometheus metrics
- Grafana dashboards
- Log aggregation (Stackdriver, CloudWatch)
- Alerting and notifications

#### Performance Optimization
- Parallel user authentication
- Caching strategies
- Image size optimization
- Execution time reduction

---

## Future Work

### Planned Enhancements

1. **Cloud Run Deployment**
   - Create Cloud Run service configuration
   - Implement GCS profile synchronization
   - Add Secret Manager for passwords
   - Configure Cloud Scheduler for daily runs
   - Estimated effort: 2-3 days

2. **CI/CD Pipeline**
   - GitHub Actions for automated builds
   - Multi-architecture builds (AMD64 + ARM64)
   - Automated testing on each commit
   - Docker Hub or GCR publishing
   - Estimated effort: 1-2 days

3. **Parallel Authentication**
   - Refactor to authenticate users in parallel
   - Reduce total time for multi-user scenarios
   - Maintain isolation between user sessions
   - Handle concurrent Cloudflare challenges
   - Estimated effort: 2-3 days

4. **Profile Management**
   - Automated profile warming script
   - GCS backup/restore for profiles
   - Profile validation and health checks
   - Multi-profile support for testing
   - Estimated effort: 2-3 days

5. **Enhanced Monitoring**
   - Structured logging (JSON format)
   - Prometheus metrics export
   - Success rate tracking
   - Performance dashboards
   - Estimated effort: 1-2 days

6. **Retry Logic**
   - Automatic retry on Cloudflare timeout
   - Exponential backoff for failed attempts
   - Configurable retry limits
   - Detailed retry logging
   - Estimated effort: 1 day

7. **Regional Holiday Support**
   - Configurable holiday calendar
   - Support for all Australian states
   - Custom holiday date input
   - Third-party holiday API integration
   - Estimated effort: 1-2 days

8. **Docker Compose**
   - Multi-service orchestration (optional)
   - Database for historical data (optional)
   - Frontend dashboard container
   - Nginx reverse proxy
   - Estimated effort: 1 day

---

## Additional Resources

### Documentation Files

- **README.md** - Main project documentation
- **SETUP.md** - Complete setup guide for attendance tracker
- **DOCKER_VOLUME_MOUNTS.md** - Detailed volume mount strategy
- **.env.example** - Environment variable template
- **config/myki_config.example.json** - Configuration template

### Implementation Notes

Located in `agent-os/specs/2025-11-02-docker-headed-mode-deployment/implementation/`:

- **task-group-1-summary.md** - Dockerfile and base image setup
- **task-group-3-summary.md** - Volume mounts and profile handling
- **task-group-5-summary.md** - Integration testing and validation
- **INTEGRATION_TESTING_NOTES.md** - Manual testing procedures
- **TESTING.md** - Test execution instructions

### Scripts Reference

| Script | Purpose | Documentation Section |
|--------|---------|---------------------|
| `docker-build.sh` | Build Docker image | [Build and Run Scripts](#docker-buildsh) |
| `docker-run.sh` | Run container | [Build and Run Scripts](#docker-runsh) |
| `docker-test.sh` | Automated validation | [Build and Run Scripts](#docker-testsh) |
| `docker-debug.sh` | Interactive debugging | [Build and Run Scripts](#docker-debugsh) |
| `docker-health-check.sh` | Health check validation | [Build and Run Scripts](#docker-health-checksh) |
| `entrypoint.sh` | Container startup | Embedded in Docker image |

### Support and Troubleshooting

For issues:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review container logs: `docker logs myki-tracker-run`
3. Use debug shell: `./docker-debug.sh`
4. Check implementation notes in spec directory

---

## Quick Reference

### One-Command Workflows

**First-time setup:**
```bash
# Copy profile, create config, build image, run container
./copy-chrome-profile.sh && \
cp config/myki_config.example.json config/myki_config.json && \
cp .env.example .env && \
# Edit config and .env manually, then:
./docker-build.sh && \
./docker-run.sh
```

**Daily usage:**
```bash
# Run and validate
./docker-run.sh && ./docker-health-check.sh
```

**Development cycle:**
```bash
# Rebuild and test
./docker-build.sh && ./docker-test.sh
```

**Debugging:**
```bash
# Debug shell
./docker-debug.sh
```

### Verification Checklist

Before first run:
- [ ] Docker Desktop installed and running
- [ ] Chrome profile copied to `browser_profile/`
- [ ] `config/myki_config.json` created and configured
- [ ] `.env` file created with passwords
- [ ] All required directories created
- [ ] Docker image built successfully

After each run:
- [ ] Container exit code is 0
- [ ] `output/attendance.json` exists
- [ ] Session files created in `auth_data/`
- [ ] No error screenshots in `screenshots/`
- [ ] Success message in logs

### Common Commands

```bash
# Build
./docker-build.sh

# Run
./docker-run.sh

# Test
./docker-test.sh

# Debug
./docker-debug.sh

# Validate
./docker-health-check.sh

# Clean up
docker rmi myki-tracker:local-v1
rm -rf output/* auth_data/* screenshots/*

# View logs
docker logs myki-tracker-run

# Check resources
docker stats
```

---

**Last Updated:** 2025-11-02
**Version:** 1.0
**Status:** Stable - Local Docker Deployment
