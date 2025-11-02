# Myki Attendance Tracker - Setup Guide

## Overview

This tool automatically tracks work attendance by monitoring Myki "Touch off" events at designated stations.

**Features:**
- **Multi-user support** - Track multiple Myki accounts simultaneously
- **Unified configuration** - One config file for all users
- **Pre-flight validation** - Catches errors before 45-60s authentication
- **Automatic workflow** - Phase 1 (authenticate all users) → Phase 2 (track all users)
- **Per-user sessions** - Each account gets its own secure session
- **Incremental processing** - Only processes new transactions
- **Working days calculation** - Excludes weekends, public holidays, skip dates

## Quick Start

### 1. Create Configuration File

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
      "startDate": "2025-04-15",
      "endDate": "2025-06-15",
      "skipDates": ["2025-05-10", "2025-05-20"]
    },
    "john": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Melbourne Central",
      "startDate": "2025-01-01"
    }
  }
}
```

**Note:** The config key (e.g., `"koustubh"`, `"john"`) IS the Myki username used for login.

**Required fields per user:**
- `mykiCardNumber` - 16-digit Myki card number
- `targetStation` - Exact station name (case-sensitive)
- `startDate` - Start date (YYYY-MM-DD)

**Optional fields:**
- `endDate` - End date (defaults to today)
- `skipDates` - Array of dates to exclude (defaults to [])

### 2. Set Passwords for Each User

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# For user "koustubh" (this IS the Myki username)
MYKI_PASSWORD_KOUSTUBH=koustubh_password_here

# For user "john" (this IS the Myki username)
MYKI_PASSWORD_JOHN=john_password_here
```

**Pattern:** `MYKI_PASSWORD_{USERNAME}` where USERNAME is the UPPERCASE version of the config key.
- Config key `"koustubh"` → `MYKI_PASSWORD_KOUSTUBH`
- Config key `"john"` → `MYKI_PASSWORD_JOHN`

### 3. Run the Workflow

```bash
python src/run_myki_workflow.py
```

Or with a custom config:

```bash
python src/run_myki_workflow.py config/my_config.json
```

## Understanding Multi-User Setup

### Scenario

You want to track attendance for multiple people, each with their own Myki account:

- **Koustubh** has Myki username `koustubh`
- **John** has Myki username `john`

Each person has their own:
- Myki username (the config key) and password
- Card number(s)
- Target station
- Date range

### Configuration

**config/myki_config.json:**
```json
{
  "users": {
    "koustubh": {                          // ← This IS the Myki username
      "mykiCardNumber": "123456789012345",
      "targetStation": "Heathmont Station",
      "startDate": "2025-04-15"
    },
    "john": {                              // ← This IS the Myki username
      "mykiCardNumber": "123456789012345",
      "targetStation": "Melbourne Central",
      "startDate": "2025-01-01"
    }
  }
}
```

**.env:**
```bash
MYKI_PASSWORD_KOUSTUBH=koustubh_password  # ← Password for username "koustubh"
MYKI_PASSWORD_JOHN=john_password          # ← Password for username "john"
```

## What Happens When You Run It

### Pre-Flight Validation ⚡ (< 1 second)
- ✓ Config file exists and is valid JSON
- ✓ All users have required fields (mykiCardNumber, targetStation, startDate)
- ✓ Date formats correct (YYYY-MM-DD)
- ✓ All password environment variables set (`MYKI_PASSWORD_KOUSTUBH`, `MYKI_PASSWORD_JOHN`, etc.)

**If anything is wrong, it stops immediately with clear error messages.**

### Phase 1: Multi-User Authentication 🔐 (45-60s per user)

The workflow authenticates **each user sequentially**:

```
Authenticating: koustubh
├─ Bypasses Cloudflare protection
├─ Logs into Myki with username "koustubh"
└─ Saves session to auth_data/session_koustubh.json

Authenticating: john
├─ Bypasses Cloudflare protection
├─ Logs into Myki with username "john"
└─ Saves session to auth_data/session_john.json

Authentication Summary:
  ✓ Successful: 2
  ✗ Failed: 0
```

**Each user gets their own session file:**
- `auth_data/session_koustubh.json`
- `auth_data/session_john.json`
- `auth_data/cookies_koustubh.json`
- `auth_data/cookies_john.json`
- etc.

### Phase 2: Multi-User Tracking 📊

**Automatically runs after Phase 1** and processes each user:

```
Processing user: koustubh
├─ Uses session_koustubh.json
├─ Fetches transactions for card 123456789012345
├─ Filters for "Touch off" at "Heathmont Station"
├─ Calculates working days
└─ Updates output/attendance.json

Processing user: john
├─ Uses session_john.json
├─ Fetches transactions for card 123456789012345
├─ Filters for "Touch off" at "Melbourne Central"
├─ Calculates working days
└─ Updates output/attendance.json
```

## Output Format

`output/attendance.json`:

```json
{
  "metadata": {
    "generatedAt": "2025-11-01T14:30:00Z",
    "configPath": "config/myki_config.json",
    "totalUsers": 2
  },
  "koustubh": {
    "attendanceDays": ["2025-04-15", "2025-04-16", "2025-04-17"],
    "latestProcessedDate": "2025-04-17T18:30:00+10:00",
    "targetStation": "Heathmont Station",
    "lastUpdated": "2025-11-01T14:30:00Z",
    "statistics": {
      "totalWorkingDays": 138,
      "daysAttended": 46,
      "daysMissed": 92,
      "attendancePercentage": 33.33,
      "firstAttendance": "2025-04-15",
      "lastAttendance": "2025-10-29",
      "periodStart": "2025-04-15",
      "periodEnd": "2025-11-02",
      "monthlyBreakdown": [
        {
          "month": "2025-04",
          "workingDays": 9,
          "daysAttended": 0,
          "attendancePercentage": 0.0
        },
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
  },
  "john": {
    "attendanceDays": ["2025-01-03", "2025-01-04", "2025-01-05"],
    "latestProcessedDate": "2025-01-05T17:45:00+10:00",
    "targetStation": "Melbourne Central",
    "lastUpdated": "2025-11-01T14:30:00Z",
    "statistics": {
      "totalWorkingDays": 22,
      "daysAttended": 3,
      "daysMissed": 19,
      "attendancePercentage": 13.64,
      "firstAttendance": "2025-01-03",
      "lastAttendance": "2025-01-05",
      "periodStart": "2025-01-01",
      "periodEnd": "2025-01-31",
      "monthlyBreakdown": [
        {
          "month": "2025-01",
          "workingDays": 22,
          "daysAttended": 3,
          "attendancePercentage": 13.64
        }
      ]
    }
  }
}
```

### Statistics Breakdown

Each user's output includes:
- **Overall statistics**: Total working days, attendance rate, first/last attendance
- **Monthly breakdown**: Per-month attendance rates for trend analysis
- **Working days calculation**: Automatically excludes weekends, Melbourne VIC holidays, and user skip dates

## Incremental Processing

The tool remembers the last processed transaction **per user**:

**First run:**
- Processes all transactions from each user's `startDate` to `endDate`
- Sets `latestProcessedDate` for each user

**Subsequent runs:**
- Only processes transactions after each user's `latestProcessedDate`
- Merges new attendance days with existing days
- Updates `latestProcessedDate` per user

This makes it efficient for daily/weekly cron jobs.

## Working Days Logic

A day is marked as attended if:
- ✓ At least 1 "Touch off" at user's target station
- ✓ Day is Monday-Friday
- ✓ NOT a Melbourne VIC public holiday
- ✓ NOT in user's `skipDates`

## Troubleshooting

### Error: "Config file not found"
```
✗ Config file not found: config/myki_config.json
  Create config file first (see config/myki_config.example.json)
```

**Fix:** Copy the example config:
```bash
cp config/myki_config.example.json config/myki_config.json
```

### Error: "Missing required field 'mykiCardNumber'"
```
✗ Config validation error: Missing required field 'mykiCardNumber' for user 'koustubh'
```

**Fix:** Ensure all required fields are present:
```json
{
  "users": {
    "koustubh": {
      "mykiCardNumber": "123456789012345",  // ← Required
      "targetStation": "Heathmont Station",  // ← Required
      "startDate": "2025-04-15"              // ← Required
    }
  }
}
```

### Error: "Missing required environment variables for passwords"
```
✗ Missing required environment variables for passwords:
  - MYKI_PASSWORD_KOUSTUBH
  - MYKI_PASSWORD_JOHN

Set these environment variables before running the tracker.
```

**Fix:** Create `.env` file and add passwords:
```bash
cp .env.example .env
# Edit .env and add:
MYKI_PASSWORD_KOUSTUBH=your_password_here
MYKI_PASSWORD_JOHN=your_password_here
```

### Error: "Invalid date format"
```
✗ Invalid date format for startDate in user 'koustubh': '2025/04/15'
  Expected ISO format (YYYY-MM-DD)
```

**Fix:** Use YYYY-MM-DD format:
```json
"startDate": "2025-04-15"  // ✓ Correct
"startDate": "2025/04/15"  // ✗ Wrong
```

### Authentication fails for one user
```
Authentication Summary:
  ✓ Successful: 1
  ✗ Failed: 1

Failed authentications:
  - john

❌ WORKFLOW FAILED - Some authentications did not succeed
```

**Fix:**
1. Verify the config key matches the actual Myki username
2. Check `.env` has correct password: `MYKI_PASSWORD_JOHN`
3. Ensure you can login manually with the same credentials

### "Session file not found" in Phase 2
```
Session file not found: auth_data/session_koustubh.json
Run authentication first to generate session data.
```

**Fix:** Phase 1 authentication failed or was skipped. Run the full workflow again:
```bash
python src/run_myki_workflow.py
```

## Advanced Usage

### Run Only Authentication (Phase 1)

```bash
python src/myki_auth.py
```

Note: This only authenticates ONE user (the one in MYKI_USERNAME/.env). Use the workflow for multi-user.

### Run Only Tracking (Phase 2)

If you already have valid sessions for all users:

```bash
python src/myki_attendance_tracker.py config/myki_config.json
```

### Cron Job Setup

Add to crontab for daily runs:

```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/station-station-agentos && /path/to/venv/bin/python src/run_myki_workflow.py >> /path/to/logs/myki.log 2>&1
```

### Custom Output Location

The output is always saved to `output/attendance.json`. To change this, modify `src/output_manager.py`.

## Exit Codes

- `0` - Success (all users authenticated and processed)
- `1` - Failure (validation failed, auth failed, or some users failed)

Perfect for automation and monitoring.

## File Structure

After setup, your directory will look like:

```
station-station-agentos/
├── config/
│   ├── myki_config.json           # Your config (not in git)
│   └── myki_config.example.json   # Example template
├── auth_data/                      # Created by Phase 1
│   ├── session_koustubh.json      # Koustubh's session
│   ├── cookies_koustubh.json
│   ├── session_john.json          # John's session
│   └── cookies_john.json
├── output/
│   └── attendance.json             # Generated by Phase 2
├── .env                            # Your passwords (not in git)
├── .env.example
└── src/
    └── run_myki_workflow.py        # Main entry point
```

## Security Notes

- `.env` and `config/myki_config.json` are in `.gitignore` - your passwords/data are safe
- Each user's session is stored separately and securely
- Sessions expire after some time - rerun authentication when needed
- Bearer tokens are extracted and saved for API access
