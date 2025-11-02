# Myki API Authentication & Attendance Tracker

Automated authentication system for the Myki public transport API with Cloudflare Turnstile bypass, plus multi-user work attendance tracking.

## Overview

This project provides a complete solution for:
1. **Authenticating** with the Myki portal using headless browser automation
2. **Bypassing Cloudflare Turnstile** bot detection using Chrome profile trust signals
3. **Extracting** authentication tokens (cookies, headers, and Bearer token)
4. **Making API calls** to retrieve transaction data and other information
5. **Tracking work attendance** for multiple users based on Myki touch-off events

## Features

### Authentication & API Client
- ✅ Cloudflare Turnstile bypass using Chrome profile trust signals
- ✅ Automated login with credentials from environment variables
- ✅ Captures all required authentication tokens including Bearer token
- ✅ Python API client for making authenticated requests
- ✅ Transaction history retrieval
- ✅ Saves authentication data for reuse

### Attendance Tracker (NEW)
- ✅ Multi-user support - track multiple Myki accounts simultaneously
- ✅ Automated workflow - authenticate all users, then track attendance
- ✅ Working days calculation - excludes weekends, public holidays, skip dates
- ✅ Incremental processing - only processes new transactions
- ✅ Per-user sessions - each account gets its own secure session
- ✅ Statistics & analytics - overall and monthly attendance percentages
- ✅ JSON output - ready for frontend consumption

## Quick Start

### For Attendance Tracking (Recommended)

See **[SETUP.md](SETUP.md)** for complete setup guide.

**Quick setup:**
```bash
# 1. Setup config
cp config/myki_config.example.json config/myki_config.json
# Edit config and add users

# 2. Set passwords
cp .env.example .env
# Edit .env and set MYKI_PASSWORD_{USERNAME} for each user

# 3. Run workflow (authenticates + tracks all users)
python src/run_myki_workflow.py
```

**Config format:**
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
  }
}
```

**Note:** Config key (e.g., `"koustubh"`) IS the Myki username for login.

**Environment variables:**
```bash
MYKI_PASSWORD_KOUSTUBH=password1
MYKI_PASSWORD_JOHN=password2
```

### For API Client Only (Advanced)

If you only want to use the authentication and API client without the attendance tracker:

## Prerequisites

- Python 3.8+
- Google Chrome browser
- Active Myki account

## Installation

1. **Clone the repository**
   ```bash
   cd /path/to/station-station-agentos
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

5. **Configure credentials**

   Create a `.env` file in the project root:
   ```env
   MYKI_USERNAME=your_username_here
   MYKI_PASSWORD=your_password_here
   ```

## Usage

### Step 1: Authenticate

Run the authentication script to log in and capture all required tokens:

```bash
python src/myki_auth.py
```

This will:
1. Copy your Chrome profile for browser trust signals
2. Launch Chrome and navigate to Myki portal
3. Wait for Cloudflare Turnstile verification
4. Fill and submit login form
5. Extract cookies, headers, and Bearer token
6. Save all authentication data to `auth_data/` directory

**Files created:**
- `auth_data/session.json` - Complete session data
- `auth_data/cookies.json` - Session cookies
- `auth_data/headers.json` - Request headers
- `auth_data/auth_request.json` - Authentication request/response details
- `auth_data/bearer_token.txt` - Bearer token for authorization

### Step 2: Use the API Client

After authentication, use the API client to make requests:

```python
from src.myki_api_client import MykiAPIClient

# Initialize client (automatically loads saved authentication data)
client = MykiAPIClient()

# Get transactions for a specific myki card
transactions = client.get_transactions(
    card_number="YOUR_CARD_NUMBER",  # e.g., "123456789012345"
    page=0
)

# Print results
print(transactions)
```

**Example output:**
```json
{
  "code": 1,
  "message": "Success",
  "data": [
    {
      "transactionType": "Touch off",
      "serviceType": "Train",
      "transactionDateTime": "2025-10-29T13:04:45+11:00",
      "zone": "2",
      "description": "Heathmont Station",
      "debitAmount": "-",
      "mykiBalance": "-"
    },
    ...
  ]
}
```

### Attendance Output

The attendance tracker generates `output/attendance.json` with statistics:

```json
{
  "metadata": {
    "generatedAt": "2025-11-01T13:56:04Z",
    "totalUsers": 1
  },
  "koustubh": {
    "attendanceDays": ["2025-05-08", "2025-05-13", ...],
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
        },
        {
          "month": "2025-09",
          "workingDays": 21,
          "daysAttended": 13,
          "attendancePercentage": 61.9
        }
      ]
    }
  }
}
```

## API Client Methods

### `MykiAPIClient()`

Initialize the API client. Automatically loads saved authentication data.

```python
client = MykiAPIClient()
```

### `get_transactions(card_number, page=0)`

Retrieve transaction history for a specific myki card.

**Parameters:**
- `card_number` (str): The myki card number
- `page` (int): Page number for pagination (default: 0)

**Returns:** Dictionary containing transaction data

```python
transactions = client.get_transactions("123456789012345", page=0)
```

## Architecture

### Phase 1: Authentication (`src/myki_auth.py`)

1. **Profile Copying** (`src/profile_manager.py`)
   - Copies Chrome profile files (Cookies, Preferences, History, Web Data, Login Data)
   - Creates temporary profile directory
   - Provides browser trust signals to bypass Cloudflare

2. **Cloudflare Bypass**
   - Launches Chrome with copied profile
   - Waits for Cloudflare Turnstile verification (~35 seconds)
   - Uses minimal browser configuration to avoid detection

3. **Login Flow**
   - Simulates human behavior (mouse movements, realistic typing delays)
   - Fills username and password fields
   - Clicks login button
   - Monitors for authentication POST request

4. **Token Extraction**
   - Extracts session cookies from browser context
   - Captures authentication headers from POST request
   - Extracts Bearer token from authentication response
   - Saves all data to `auth_data/` directory

### Phase 2: API Client (`src/myki_api_client.py`)

1. **Session Loading** (`src/auth_loader.py`)
   - Loads cookies, headers, auth request, and Bearer token
   - Validates authentication data is present

2. **Request Building**
   - Constructs headers with all required authentication tokens:
     - `authorization: Bearer <token>` - Primary auth token
     - `x-passthruauth` - PassthruAuth cookie value
     - `x-ptvwebauth` - PTV web authentication token
     - `x-verifytoken` - Cloudflare verification token
   - Includes cookies for session persistence

3. **API Calls**
   - Makes authenticated POST/GET requests to Myki API
   - Handles responses and errors
   - Returns parsed JSON data

## Authentication Tokens Explained

The Myki API requires multiple authentication tokens:

1. **Bearer Token** (`authorization` header)
   - Primary authentication token
   - Obtained from `/authenticate` POST response
   - Format: JWT (HS512 algorithm)
   - Expires after ~20 minutes
   - Example: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9...`

2. **PassthruAuth** (cookie + `x-passthruauth` header)
   - Session authentication cookie
   - Format: JWT (ES256 algorithm)
   - Set by authentication response
   - Example: `eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9...`

3. **x-ptvwebauth** (header)
   - PTV web authentication token
   - Format: `timestamp-base64_signature`
   - Example: `1761921449-OqGn1rhFCCYPA79XG4eN8etIzKcsA2guIawClGHfZZU=`

4. **x-verifytoken** (header)
   - Cloudflare verification token
   - Format: JWT (HS512 algorithm)
   - Short-lived (~5 minutes)
   - Example: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9...`

## API Endpoints

### Base URL
```
https://mykiapi.ptv.vic.gov.au/v2
```

### Transactions Endpoint

**POST** `/myki/transactions?page={page}`

Retrieve transaction history for a myki card.

**Request Body:**
```json
{
  "mykiCardNumber": "123456789012345"
}
```

**Response:**
```json
{
  "code": 1,
  "message": "Success",
  "data": [
    {
      "transactionType": "Touch off",
      "serviceType": "Train",
      "transactionDateTime": "2025-10-29T13:04:45+11:00",
      "zone": "2",
      "GSTAmount": "0.0000",
      "description": "Heathmont Station",
      "debitAmount": "-",
      "creditAmount": "-",
      "txnAmount": "0.0000",
      "mykiBalance": "-"
    }
  ]
}
```

## Troubleshooting

### Authentication Fails with "401 Unauthorized"

The authentication tokens have expired. Re-run the authentication:

```bash
python src/myki_auth.py
```

Tokens typically expire after 20 minutes.

### Cloudflare Blocks with "Please refresh and try again"

This can happen due to:
- **Rate limiting**: Wait a few minutes between authentication attempts
- **Suspicious behavior**: Ensure Chrome profile is recent and has browsing history
- **Multiple rapid attempts**: Space out your authentication runs

Solution: Wait 5-10 minutes and try again.

### Chrome Profile Issues

If Chrome profile copying fails:
- Ensure Chrome is fully closed before running authentication
- Check that Chrome profile path exists: `~/Library/Application Support/Google/Chrome/Default`
- Verify you have read permissions for the profile directory

## Project Structure

```
.
├── src/
│   ├── run_myki_workflow.py      # Main entry point - runs auth + tracking
│   ├── myki_auth.py              # Phase 1: Authentication script
│   ├── myki_attendance_tracker.py # Phase 2: Attendance tracking
│   ├── myki_api_client.py        # API client for making requests
│   ├── auth_loader.py            # Helper to load saved auth data
│   ├── profile_manager.py        # Chrome profile management
│   ├── config_manager.py         # Config loading and validation
│   ├── working_days.py           # Working days calculation
│   ├── transaction_fetcher.py    # Transaction fetching with pagination
│   ├── transaction_processor.py  # Transaction filtering and processing
│   └── output_manager.py         # JSON output generation
├── config/
│   ├── myki_config.json          # Your config (not in git)
│   └── myki_config.example.json  # Example template
├── auth_data/
│   ├── session_koustubh.json     # Per-user session files
│   ├── cookies_koustubh.json
│   ├── session_john.json
│   └── cookies_john.json
├── output/
│   └── attendance.json           # Generated attendance data
├── .env                          # Passwords (not committed)
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── SETUP.md                      # Complete setup guide for attendance tracker
```

## Security Notes

- **Never commit `.env` file** - Contains your passwords (per-user passwords for multi-user setup)
- **Never commit `config/myki_config.json`** - Contains user-specific configuration
- **Authentication data is sensitive** - Files in `auth_data/` contain valid session tokens
- **Tokens expire** - Bearer token valid for ~20 minutes, re-authenticate as needed
- **Chrome profile** - Contains your browsing history and cookies
- **Per-user sessions** - Each user gets their own session file for isolation

## Multi-User Configuration

The system uses a simple pattern:

1. **Config keys are usernames** - The key in the config (e.g., `"koustubh"`) IS the Myki username
2. **One password per user** - Set `MYKI_PASSWORD_{USERNAME}` where USERNAME is uppercase config key
3. **Separate sessions** - Each user gets `auth_data/session_{username}.json`
4. **Parallel processing** - All users authenticated sequentially, then tracked in parallel

Example:
- Config has user `"koustubh"` → Myki username is `"koustubh"` → Set `MYKI_PASSWORD_KOUSTUBH`
- Config has user `"john"` → Myki username is `"john"` → Set `MYKI_PASSWORD_JOHN`

## Limitations

- Requires Google Chrome installed on the system
- Authentication must be re-run every ~20 minutes when tokens expire
- Cloudflare bypass depends on Chrome profile trust signals
- Rate limiting: Avoid multiple rapid authentication attempts
- Multi-user authentication is sequential (45-60s per user)
- Melbourne VIC public holidays only (not configurable for other regions)

## Future Enhancements

- ✅ ~~Multi-user attendance tracking~~ (COMPLETED)
- ✅ ~~Working days calculation with public holidays~~ (COMPLETED)
- ✅ ~~Incremental processing to avoid re-processing~~ (COMPLETED)
- ✅ ~~Scheduled daily authentication via cron job~~ (COMPLETED - via workflow)
- ✅ ~~Statistics and analytics (overall + monthly breakdown)~~ (COMPLETED)
- ✅ ~~Code refactoring into focused modules~~ (COMPLETED)
- Automatic token refresh when expired
- Support for additional API endpoints (balance, card details, etc.)
- Cloud Run deployment with profile persistence
- Parallel multi-user authentication (reduce total time)
- Frontend dashboard for visualizing attendance data
- Export to CSV/Excel for reporting
- Email/Slack notifications for low attendance alerts

## License

This project is for personal use and educational purposes.
