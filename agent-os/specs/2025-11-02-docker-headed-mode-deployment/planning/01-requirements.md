# Requirements: Docker Headed Mode Deployment

## Current Working Implementation

### Chrome Configuration
- **Browser:** Google Chrome (NOT Chromium) via `channel='chrome'`
- **Mode:** Headed (`headless=False`) - **Critical for Cloudflare bypass**
- **Launch Method:** `launch_persistent_context`
- **Viewport:** 1920x1080
- **Args:** `['--disable-blink-features=AutomationControlled']`

### Chrome Profile Strategy
**Current (Local):**
- Copies user's local Chrome profile to temp directory
- Source paths:
  - macOS: `~/Library/Application Support/Google/Chrome/Default`
  - Linux: `~/.config/google-chrome/Default`
- Files copied: Cookies, Preferences, History, Web Data, Login Data

**Required for Docker:**
- Need pre-built Chrome profile with trust signals
- Profile must be writable (not read-only)
- Profile should be mounted or copied into container

### Entry Point
- **Main script:** `src/run_myki_workflow.py`
- **Config file:** `config/myki_config.json`
- **Command:** `python src/run_myki_workflow.py config/myki_config.json`

### Environment Variables
```bash
# Per-user passwords (pattern: MYKI_PASSWORD_{USERNAME_UPPERCASE})
MYKI_PASSWORD_KOUSTUBH=your_password_here
MYKI_PASSWORD_JOHN=your_password_here
```

### Success Validation
**Successful run produces:**
- `output/attendance.json` with attendance data
- `auth_data/session_{username}.json` per user
- Exit code: 0
- Console output: "✓ COMPLETED SUCCESSFULLY - All users processed"

**Failed run shows:**
- Exit code: 1
- Error messages in console
- Missing or incomplete output files

## Docker Requirements

### Must Have
1. **Xvfb (Virtual Display)** - Enables headed Chrome without physical display
2. **Google Chrome or Chromium** - Full browser installation
3. **Python 3.8+** - Runtime environment
4. **Playwright dependencies** - Browser automation libraries
5. **Writable directories:**
   - `/app/auth_data/` - Session storage
   - `/app/output/` - Results storage
   - `/app/browser_profile/` - Chrome profile

### System Dependencies
```
xvfb
google-chrome-stable OR chromium
fonts-liberation
libnss3
libnspr4
libatk1.0-0
libatk-bridge2.0-0
libcups2
libdrm2
libxkbcommon0
libxcomposite1
libxdamage1
libxrandr2
libgbm1
libpango-1.0-0
libasound2
```

### Python Dependencies
From `requirements.txt`:
```
playwright==1.55.0
playwright-stealth==2.0.0
python-dotenv==1.2.1
requests==2.32.5
holidays==0.59
pytest==8.4.2
```

### Volume Mounts
```bash
# Configuration
-v $(pwd)/config:/app/config:ro

# Chrome profile (read-write)
-v $(pwd)/browser_profile:/app/browser_profile:rw

# Output directory
-v $(pwd)/output:/app/output:rw

# Auth data directory
-v $(pwd)/auth_data:/app/auth_data:rw
```

### Environment Configuration
```bash
# Display for Xvfb
DISPLAY=:99

# User passwords
MYKI_PASSWORD_KOUSTUBH=password
MYKI_PASSWORD_JOHN=password
```

## Success Criteria

### Local Docker Deployment Must:
1. ✅ Run headed Chrome successfully via Xvfb
2. ✅ Bypass Cloudflare Turnstile (same success rate as local)
3. ✅ Authenticate all configured users
4. ✅ Generate `output/attendance.json` file
5. ✅ Complete within 2-3 minutes for 2 users
6. ✅ Exit with code 0 on success

### Validation Tests:
1. **Smoke test:** Single user authentication and data fetch
2. **Multi-user test:** All users from config
3. **Cloudflare test:** Verify 35-second Turnstile wait succeeds
4. **Output validation:** Check attendance.json structure and data
5. **Repeat test:** Run multiple times to verify consistency

## Known Challenges

### 1. Chrome vs Chromium
- Code uses `channel='chrome'` (Google Chrome)
- Docker images typically include Chromium
- **Solution:** Either install Google Chrome in Docker OR test if Chromium works with `channel='chromium'`

### 2. Chrome Profile Trust
- Fresh profile has no browsing history
- Cloudflare may detect "new" browser
- **Solution:** Pre-warm profile OR use copied profile from local machine

### 3. Xvfb Display Configuration
- Must start Xvfb before launching Chrome
- Display number (`:99`) must not conflict
- Screen resolution must match viewport (1920x1080)

### 4. File Permissions
- Docker runs as different user (UID mismatch)
- Profile directory must be writable
- **Solution:** Use appropriate user permissions or run as non-root

## Out of Scope

This spec focuses ONLY on local Docker deployment:

❌ **Not included:**
- GitHub Actions deployment
- Cloud Run deployment
- Automated scheduling/cron
- Profile synchronization to cloud storage
- CI/CD pipelines
- Production deployment

✅ **Included:**
- Local Docker container setup
- Xvfb configuration for headed Chrome
- Volume mounting for data persistence
- Success validation locally
- Troubleshooting guide

## Next Steps

After requirements are finalized:
1. Create Dockerfile
2. Create docker-compose.yml (optional, for easier local testing)
3. Create docker-run.sh script
4. Test locally with single user
5. Test with multiple users
6. Document troubleshooting steps
