# Myki Attendance Tracker - Current State Summary

**Last Updated:** 2025-11-02  
**Status:** ✅ Production Ready  
**Tests:** 40 passing (29 unit + 11 integration)

## Overview

Fully functional multi-user attendance tracking system that:
1. Authenticates multiple Myki accounts via browser automation (bypasses Cloudflare)
2. Fetches transaction data via Myki API
3. Calculates attendance statistics with monthly breakdown
4. Outputs JSON ready for frontend consumption

## Architecture

### Core Modules (Refactored)
```
src/
├── run_myki_workflow.py           # Orchestrator (Phase 1 + Phase 2)
├── myki_auth.py                   # Browser-based authentication
├── myki_attendance_tracker.py     # Main tracker orchestration (326 lines, down from 1214)
├── myki_api_client.py             # API client with session management
├── config_manager.py              # Config loading & validation
├── working_days.py                # Working day calculations
├── transaction_fetcher.py         # Pagination with special 409 handling
├── transaction_processor.py       # Transaction filtering
└── output_manager.py              # Statistics & JSON output
```

### Data Flow
```
1. Pre-Flight Validation
   ↓
2. Phase 1: Multi-User Authentication (sequential)
   ├─ koustubh25 → session_koustubh25.json
   └─ john → session_john.json
   ↓
3. Phase 2: Multi-User Tracking (using saved sessions)
   ├─ Fetch transactions (with 409 pagination handling)
   ├─ Filter by station + date range
   ├─ Calculate attendance days (working days only)
   ├─ Calculate statistics (overall + monthly)
   └─ Save to output/attendance.json
```

## Configuration

### Unified Config Format
```json
{
  "users": {
    "koustubh25": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Southern Cross Station",
      "startDate": "2025-04-15",
      "endDate": "2025-11-02",
      "skipDates": ["2025-03-15", "2025-06-20"]
    }
  }
}
```

**Environment Variables:**
```bash
MYKI_PASSWORD_KOUSTUBH25=password_here
```

**Pattern:** Config key IS the Myki username (no separate mykiUsername field)

## Output Format

```json
{
  "metadata": {
    "generatedAt": "2025-11-01T13:56:04Z",
    "totalUsers": 1
  },
  "koustubh25": {
    "attendanceDays": ["2025-05-08", "2025-05-13", ...],
    "latestProcessedDate": "2025-10-29T09:35:00+11:00",
    "targetStation": "Southern Cross Station",
    "lastUpdated": "2025-11-01T13:56:04Z",
    "statistics": {
      "totalWorkingDays": 138,
      "daysAttended": 46,
      "daysMissed": 92,
      "attendancePercentage": 33.33,
      "firstAttendance": "2025-05-08",
      "lastAttendance": "2025-10-29",
      "periodStart": "2025-04-15",
      "periodEnd": "2025-11-02",
      "monthlyBreakdown": [
        {
          "month": "2025-05",
          "workingDays": 22,
          "daysAttended": 4,
          "daysMissed": 18,
          "attendancePercentage": 18.18
        },
        {
          "month": "2025-09",
          "workingDays": 21,
          "daysAttended": 13,
          "daysMissed": 8,
          "attendancePercentage": 61.9
        }
      ]
    }
  }
}
```

## Key Features

### ✅ Completed Features

1. **Multi-User Support**
   - Sequential authentication (45-60s per user)
   - Per-user session files (session_{username}.json)
   - Parallel config validation

2. **Cloudflare Bypass**
   - Chrome profile copying for trust signals
   - Invisible Turnstile verification
   - Human behavior simulation

3. **Working Days Calculation**
   - Excludes weekends (Sat/Sun)
   - Excludes Melbourne VIC public holidays (via holidays package)
   - Excludes user-specific skip dates

4. **Incremental Processing**
   - Tracks latestProcessedDate per user
   - Only processes new transactions
   - Merges new data with existing data

5. **Statistics & Analytics** 
   - Overall: total working days, attendance %, first/last dates
   - Monthly breakdown: per-month attendance rates
   - Respects all working day rules

6. **Error Handling**
   - Special 409 error handling (pagination end-of-data signal)
   - Pre-flight validation (catches errors before authentication)
   - Error isolation (one user's failure doesn't stop others)

7. **Testing**
   - 29 unit tests
   - 11 integration tests
   - All 40 passing

## Critical Bug Fixes

### 409 Pagination Error (Fixed)
**Problem:** `requests.Response` objects evaluate to False for 4xx/5xx status codes  
**Solution:** Use `is None` instead of truthy checks  
**Impact:** Workflow now completes successfully end-to-end

### Code Location
```python
# transaction_fetcher.py:29
if http_error.response is None:  # ✅ CORRECT
    return False

# NOT:
if not http_error.response:  # ❌ WRONG - evaluates to True for 409!
    return False
```

## Usage

### Quick Start
```bash
# 1. Setup config
cp config/myki_config.example.json config/myki_config.json
# Edit and add users

# 2. Set passwords
cp .env.example .env
# Add MYKI_PASSWORD_{USERNAME} for each user

# 3. Run workflow
python src/run_myki_workflow.py
```

### Cron Job
```bash
# Daily at 9 AM
0 9 * * * cd /path/to/project && /path/to/venv/bin/python src/run_myki_workflow.py >> logs/myki.log 2>&1
```

## Performance Metrics

- **Pre-flight validation:** < 1 second
- **Authentication per user:** 45-60 seconds
- **Transaction processing:** 5-10 seconds per user
- **Total for 2 users:** ~2 minutes

## Security

- ✅ .env files excluded from git
- ✅ config/myki_config.json excluded from git
- ✅ auth_data/ excluded from git
- ✅ output/ excluded from git
- ✅ Per-user session isolation
- ✅ Bearer tokens expire after ~20 minutes

## Known Limitations

1. **Authentication:** Sequential only (45-60s per user)
2. **Holidays:** Melbourne VIC only (hardcoded)
3. **Sessions:** Expire after ~20 minutes (re-auth required)
4. **Rate limiting:** Avoid rapid authentication attempts
5. **Browser:** Requires Chrome installed

## Future Enhancements

**Priority:**
- [ ] Automatic token refresh when expired
- [ ] Frontend dashboard for visualization
- [ ] Export to CSV/Excel

**Nice to Have:**
- [ ] Parallel multi-user authentication
- [ ] Cloud Run deployment
- [ ] Email/Slack alerts for low attendance
- [ ] Support for other regions' holidays

## Test Coverage

```
Total: 40 tests passing
├─ Configuration (6 tests)
├─ Working Days (7 tests)
├─ Pagination (4 tests)
├─ Filtering (4 tests)
├─ Incremental Processing (4 tests)
├─ Orchestration (4 tests)
└─ Integration (11 tests)
```

## Exit Codes

- `0` - Success (all users processed)
- `1` - Failure (validation failed, auth failed, or some users failed)

Perfect for automation and monitoring!
