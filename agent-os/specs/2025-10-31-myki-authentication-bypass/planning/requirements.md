# Spec Requirements: Myki Authentication & Cloudflare Bypass

## Initial Description

Successfully authenticate with Myki portal using headless browser automation, bypass Cloudflare bot detection, and extract required authentication headers and cookies for subsequent API calls.

**Context:**
- This is the foundational feature for the Station Station Myki attendance tracking application
- Previous attempts to bypass Cloudflare bot detection have been unsuccessful
- **Scope is LIMITED to authentication only** - not reverse engineering other API calls yet
- Once authentication is solved and headers/cookies are extracted, subsequent API calls will be tackled separately
- Backend will be Python with local virtual environment
- Requires headless browser automation to mimic real user behavior

## Requirements Discussion

### First Round Questions

**Q1: Browser automation library**
I assume we'll use Playwright for Python as it has better support for modern browser features and stealth mode compared to Selenium. Is that correct, or would you prefer Selenium or another library?

**Answer:** Agreed to use Playwright. User noted that bypassing Cloudflare Turnstile is "extremely hard" and left the final decision up to us. User is aware of the difficulty level.

**Q2: Credential input method**
I'm thinking we should use environment variables (via dotenv) for username and password to keep credentials secure and make testing easy. Should we also support reading from a config file, or is .env sufficient?

**Answer:** Agreed - use environment variables with dotenv for easy testing. .env file is sufficient.

**Q3: Success detection**
After login, how should we confirm authentication succeeded? I assume we should check for a specific DOM element or URL pattern on the dashboard/account page. What page URL and/or element should we look for?

**Answer:**
- Login page URL: https://transport.vic.gov.au/manage-myki
- After successful login, look for this DOM element:
```html
<div class="myki-tabs__tab-menu" role="tablist">
  <button class="myki-tabs__tab-item myki-tabs__tab-item--active" role="tab" aria-selected="true">Active mykis</button>
  <button class="myki-tabs__tab-item" role="tab" aria-selected="false">Inactive mykis</button>
</div>
```

**Q4: Headers and cookies to extract**
What specific headers and cookies do you need extracted for subsequent API calls? I assume we need cookies like session tokens and possibly CSRF tokens. Do you have a sample API request that shows what headers/cookies are required?

**Answer:** User provided complete sample authenticate API call:
```
POST https://mykiapi.ptv.vic.gov.au/v2/account/authenticate

Headers:
- x-ptvwebauth: 1761910412-GCUaVBkWDHJBXldV+N6s5d/Ij49hLIoXIBzByFh+TLE=
- x-verifytoken: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9...
- Origin: https://transport.vic.gov.au
- Referer: https://transport.vic.gov.au/
- content-type: application/json
- accept: application/json
- User-Agent, sec-ch-ua headers, etc.

Cookies:
- _cfuvid (Cloudflare user verification ID)
- __cfruid (Cloudflare request UID)
- __cf_bm (Cloudflare bot management)
- PassthruAuth (JWT token)
- AWSALBCORS (AWS Application Load Balancer CORS)

Body:
{"username":"koustubh25","password":"Rattlesnake25!","privacyConsentAgree":true}
```

**Q5: Retry and timeout behavior**
I assume we should retry the login process a few times (e.g., 3 attempts) if Cloudflare detection fails, with exponential backoff. Should we have a maximum timeout for the entire authentication process (e.g., 60 seconds)?

**Answer:** Perfect - agreed with retry logic and timeout behavior.

**Q6: Browser visibility**
For initial development and debugging, should we run the browser in headed mode (visible) so you can watch what's happening, or should it be headless from the start?

**Answer:** Use headed mode initially so user can watch and report issues with the Cloudflare bypass attempts.

**Q7: Session persistence**
Should we save the extracted cookies/headers to a file for reuse, or keep them in memory only? If saving, where should they be stored and in what format (JSON, pickle, etc.)?

**Answer:** Keep in memory only (no file saving). This will run as a daily cron job, and cookies likely expire quickly anyway. No need for persistent storage.

**Q8: Out of scope confirmation**
Is there anything you specifically want to exclude from this spec? For example, should we skip handling 2FA/MFA for now, or any error handling beyond basic retry logic?

**Answer:**
- Authentication is the ONLY thing that can't be reverse engineered
- Do authentication via web scraping and extract required cookies
- All other calls (transaction data, etc.) can easily be reverse engineered - user can provide curl statements once we have the correct headers/cookies
- Focus solely on solving the Cloudflare bypass and authentication challenge

### Existing Code to Reference

**Similar Features Identified:**
No similar existing features - repository is currently empty. Generating everything from scratch.

## Visual Assets

### Files Provided:
- `ptv_cookie_auth_failed.png`: Screenshot showing the Cloudflare Turnstile verification challenge that fails when accessed programmatically

### Visual Insights:
- **Critical Blocker:** The screenshot shows the Cloudflare "Verifying..." screen with the Cloudflare logo
- **Failure Point:** This verification FAILS when done programmatically, before credentials can even be entered
- **Timing:** Failure happens just a few seconds after the page loads, during the initial Cloudflare bot detection phase
- **Page Context:** The login form with username/password fields is visible, but the Cloudflare Turnstile challenge overlay blocks interaction
- **Fidelity Level:** Production screenshot showing actual failure state
- **Key Challenge:** Need to bypass this Cloudflare Turnstile verification to proceed to credential entry

The visual clearly demonstrates that the main technical challenge occurs at the very first step - getting past Cloudflare's automated bot detection before any authentication credentials can be submitted.

## Requirements Summary

### Functional Requirements

**Core Functionality:**
- Navigate to Myki login page (https://transport.vic.gov.au/manage-myki)
- Bypass Cloudflare Turnstile bot detection challenge
- Enter username and password from environment variables
- Submit login credentials
- Detect successful authentication by checking for specific DOM element (myki-tabs__tab-menu)
- Extract all required headers and cookies from authenticated session
- Return/expose extracted credentials for use in subsequent API calls

**Credential Extraction Requirements:**
Must extract the following cookies:
- `_cfuvid` (Cloudflare user verification ID)
- `__cfruid` (Cloudflare request UID)
- `__cf_bm` (Cloudflare bot management)
- `PassthruAuth` (JWT token)
- `AWSALBCORS` (AWS Application Load Balancer CORS)

Must extract the following headers:
- `x-ptvwebauth` (Authentication token)
- `x-verifytoken` (JWT verification token)
- `User-Agent` and associated `sec-ch-ua` headers
- `Origin` and `Referer` headers

**User Actions Enabled:**
- Automated authentication without manual browser interaction
- Daily cron job execution for fresh authentication tokens
- Credential retrieval for downstream API calls

**Data to be Managed:**
- Username and password (read from .env file)
- Session cookies (stored in memory during execution)
- Authentication headers (stored in memory during execution)
- No persistent storage of session data

### Reusability Opportunities

No existing components or patterns to reuse - this is a greenfield project in an empty repository.

### Scope Boundaries

**In Scope:**
- Cloudflare Turnstile bypass implementation
- Automated login with username/password credentials
- Success detection via DOM element verification
- Extraction of all required cookies and headers
- Retry logic with exponential backoff (3 attempts recommended)
- Timeout handling (60 seconds maximum suggested)
- Headed browser mode for initial debugging
- Environment variable configuration via dotenv
- In-memory credential storage only

**Out of Scope:**
- Persistent storage of cookies/headers to files
- Reverse engineering other Myki API endpoints (user will provide curl statements later)
- Implementing actual attendance tracking features
- Full application integration beyond authentication
- Two-factor authentication (2FA) / Multi-factor authentication (MFA) handling
- Headless mode optimization (start with headed mode first)
- Error handling beyond basic retry logic
- Any features beyond the authentication and credential extraction

**Future Enhancements Mentioned:**
- Once authentication works, user can provide curl statements for other API calls
- Transaction data retrieval (separate from this spec)
- Full Myki attendance tracking application features
- Potential migration to headless mode after debugging complete

### Technical Considerations

**Technology Stack:**
- Language: Python
- Environment: Local virtual environment (venv)
- Browser Automation: Playwright for Python
- Configuration Management: python-dotenv
- Browser Mode: Headed (visible) initially for debugging

**Integration Points:**
- Login page: https://transport.vic.gov.au/manage-myki
- API endpoint (for reference): https://mykiapi.ptv.vic.gov.au/v2/account/authenticate
- Environment variables: USERNAME and PASSWORD

**Critical Technical Challenge:**
- **Primary Blocker:** Cloudflare Turnstile bot detection
- **Challenge Level:** User confirms this is "extremely hard"
- **Failure Point:** Occurs within seconds of page load, before credential entry
- **Detection Method:** Cloudflare analyzes browser fingerprint, behavior, and automation signals
- **Success Criteria:** Must pass Cloudflare verification to access login form

**Cloudflare Bypass Strategies to Explore:**
- Playwright stealth mode plugins
- Browser fingerprint randomization
- Human-like behavior simulation (mouse movements, delays)
- Real browser profiles and user agent rotation
- Potential use of undetected-chromedriver or similar libraries
- Cookie and localStorage pre-seeding if patterns are identified

**Environment Configuration:**
Required .env variables:
```
MYKI_USERNAME=<username>
MYKI_PASSWORD=<password>
```

**Success Detection:**
After login submission, wait for and verify presence of:
```html
<div class="myki-tabs__tab-menu" role="tablist">
  <button class="myki-tabs__tab-item myki-tabs__tab-item--active" role="tab" aria-selected="true">Active mykis</button>
  <button class="myki-tabs__tab-item" role="tab" aria-selected="false">Inactive mykis</button>
</div>
```

**Execution Model:**
- Designed to run as a daily cron job
- No session persistence required (fresh auth each run)
- Cookies/headers kept in memory during single execution
- Results passed to subsequent API call logic in the same process

**Error Handling:**
- Retry logic: Maximum 3 attempts with exponential backoff
- Timeout: 60 seconds for entire authentication process
- Clear error messages for Cloudflare detection failures
- Distinguish between Cloudflare blocking vs. invalid credentials
