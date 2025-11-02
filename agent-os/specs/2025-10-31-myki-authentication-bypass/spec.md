# Specification: Myki Authentication & Cloudflare Bypass

## Goal
Develop a Python-based headless browser automation solution that successfully bypasses Cloudflare Turnstile bot detection to authenticate with the Myki portal and extract session cookies and authentication headers required for subsequent API calls. Additionally, provide an API client to make authenticated requests to the Myki API for retrieving transaction data.

## Status
✅ **COMPLETED** - Both Phase 1 (Authentication) and Phase 2 (API Client) are fully implemented and tested.

## User Stories
- As a developer, I want to automatically authenticate with the Myki portal daily via cron job so that I can obtain fresh authentication tokens without manual intervention
- As a system integrator, I want to extract all required cookies and headers from an authenticated session so that I can make authorized API calls to retrieve transaction data

## Specific Requirements

**Cloudflare Turnstile Bypass Implementation**
- Navigate to https://transport.vic.gov.au/manage-myki using Playwright in headed mode
- **Use profile-based trust signals approach** (proven successful):
  - Copy key Chrome profile files (Cookies, Preferences, History, Web Data, Login Data) from user's actual Chrome profile
  - Launch browser with copied profile data to inherit trust signals
  - Profile data provides browsing history and cookie state that Cloudflare recognizes as legitimate
- Implement browser fingerprint randomization to avoid bot detection patterns
- Use Playwright stealth plugins to mask automation signals (--disable-blink-features=AutomationControlled)
- Employ real browser user agents with matching sec-ch-ua headers
- Handle the "Verifying..." Cloudflare overlay that blocks access to the login form
- Implement retry mechanism with exponential backoff (3 attempts maximum) if Cloudflare detection occurs
- Set 60-second timeout for the entire authentication process

**Credential Management and Input**
- Load username and password from environment variables using python-dotenv
- Store credentials in .env file with keys MYKI_USERNAME and MYKI_PASSWORD
- Securely input credentials into login form fields only after Cloudflare verification passes
- Never log or expose credentials in error messages or console output

**Authentication Flow Execution**
- Wait for login form to be fully loaded and interactive
- Fill username field with value from MYKI_USERNAME environment variable
- Fill password field with value from MYKI_PASSWORD environment variable
- Submit login form using appropriate button click or form submission
- Wait for navigation to authenticated dashboard page

**Success Detection**
- After login submission, wait for presence of specific DOM element: `div.myki-tabs__tab-menu[role="tablist"]`
- Verify child elements exist: buttons with classes `myki-tabs__tab-item` containing text "Active mykis" and "Inactive mykis"
- Confirm aria-selected attributes are set correctly on tab buttons
- Ensure authentication success is detected within timeout window

**Cookie Extraction**
- Extract all Cloudflare-related cookies: `_cfuvid`, `__cfruid`, `__cf_bm`
- Extract authentication token: `PassthruAuth` (JWT format)
- Extract AWS load balancer cookie: `AWSALBCORS`
- Store extracted cookies in memory as dictionary/object structure
- Ensure cookie values include all metadata (domain, path, expiry, secure flags)

**Header Extraction**
- Extract custom authentication header: `x-ptvwebauth`
- Extract JWT verification header: `x-verifytoken`
- **Extract Bearer token from authentication response**: Critical token from `/authenticate` POST response at `data.token`
- Capture User-Agent and all sec-ch-ua variant headers
- Record Origin header (https://transport.vic.gov.au)
- Record Referer header (https://transport.vic.gov.au/)
- Store headers in memory as dictionary structure for API reuse
- Monitor authentication response to capture Bearer token (JWT, HS512 algorithm)

**Session Data Management**
- Save all extracted cookies, headers, and Bearer token to files in `auth_data/` directory
- Files created: `session.json`, `cookies.json`, `headers.json`, `auth_request.json`, `bearer_token.txt`
- Structure data for easy consumption by downstream API call functions
- Design for single-execution model compatible with daily cron job scheduling
- Provide helper module (`auth_loader.py`) to load saved authentication data

**API Client Implementation** (Phase 2)
- Create `MykiAPIClient` class to make authenticated API requests
- Load saved authentication data (cookies, headers, Bearer token)
- Construct proper request headers with all required authentication tokens:
  - `authorization: Bearer <token>` - Primary authentication (from response)
  - `x-passthruauth` - PassthruAuth cookie value
  - `x-ptvwebauth` - PTV web authentication token
  - `x-verifytoken` - Cloudflare verification token
- Implement `get_transactions(card_number, page)` method for transaction retrieval
- Make POST requests to `https://mykiapi.ptv.vic.gov.au/v2/myki/transactions`
- Handle API responses and errors gracefully

**Profile Persistence for Cloud Run**
- Store Chrome profile files in Google Cloud Storage bucket for persistence across runs
- On each execution:
  - Download profile files from Cloud Storage to temporary directory
  - Launch browser with downloaded profile
  - After successful authentication, upload updated profile files back to Cloud Storage
- Profile ages naturally through repeated use, maintaining trust signals with Cloudflare
- Initial setup: Copy profile files from local Chrome installation to Cloud Storage
- Profile files to persist: Cookies, Preferences, History, Web Data, Login Data
- Implement profile validation to detect corruption or expiration
- Fall back to fresh profile copy if existing profile becomes invalid

**Error Handling and Logging**
- Distinguish between Cloudflare blocking failures and invalid credential failures
- Provide clear error messages indicating failure point (Cloudflare detection vs authentication)
- Implement exponential backoff between retry attempts (e.g., 2s, 4s, 8s delays)
- Log browser console errors for debugging Cloudflare bypass attempts
- Capture screenshots on failure for visual debugging in headed mode

**Browser Configuration**
- Use Playwright with Chromium browser initially
- Run in headed (visible) mode for initial development and debugging
- Configure realistic viewport size (1920x1080 or similar)
- Enable JavaScript execution and modern web APIs
- Set appropriate browser locale and timezone to match target region (Australia/Melbourne)

## Visual Design

**`planning/visuals/ptv_cookie_auth_failed.png`**
- Cloudflare "Verifying..." spinner overlay visible between username/password fields and login button
- Cloudflare logo and "Privacy • Terms" links displayed in verification widget
- Login form shows standard username and password input fields with placeholder text
- Green underline on "myki log in" tab indicates active tab state
- This verification challenge is the primary blocker that must be bypassed before credentials can be entered
- Challenge appears within seconds of initial page load
- Visual demonstrates that bot detection occurs before any user interaction with the form

## Implemented Components

This project has been fully implemented with the following modules:

### Core Modules
- **`src/myki_auth.py`** - Main authentication script with Cloudflare bypass
  - Profile-based browser trust signals
  - Human-like form interaction
  - Authentication response monitoring
  - Bearer token extraction
  - Session data persistence

- **`src/profile_manager.py`** - Chrome profile management
  - Copies key profile files (Cookies, Preferences, History, Web Data, Login Data)
  - Creates temporary profile directories
  - Handles cleanup

- **`src/myki_api_client.py`** - API client for authenticated requests
  - Loads saved authentication data
  - Constructs proper authentication headers
  - Implements `get_transactions()` method
  - Handles API responses and errors

- **`src/auth_loader.py`** - Helper to load saved authentication data
  - Loads cookies, headers, auth request, and Bearer token
  - Validates data presence
  - Returns structured data for API client

### Test Results
- ✅ Cloudflare Turnstile bypass successful with profile-based approach
- ✅ Authentication flow works reliably (with proper rate limiting)
- ✅ All authentication tokens captured (cookies, headers, Bearer token)
- ✅ API client successfully retrieves transaction data
- ✅ Bearer token expires after ~20 minutes (re-authentication required)

## Out of Scope (Completed Items Removed)

The following features are still out of scope:
- ~~Reverse engineering of other Myki API endpoints~~ (transactions endpoint implemented)
- Two-factor authentication (2FA) or multi-factor authentication (MFA) handling
- Headless mode optimization (using headed mode for Cloudflare bypass)
- Automatic token refresh when Bearer token expires
- Cookie refresh or session renewal mechanisms
- Notification system for authentication failures
- Web dashboard or UI for monitoring authentication status
- Docker containerization
- Cloud Run deployment with profile persistence (deferred to future)
- Comprehensive unit testing framework
