# Specification: Myki Transaction Tracker - Work Attendance Monitor

## Goal
Build a multi-user system that fetches Myki transaction data via authenticated API to track work attendance by identifying "Touch off" events at designated stations, calculating working days, and outputting JSON for frontend consumption.

## User Stories
- As a user, I want to automatically track my work attendance based on Myki touch-off events so that I can monitor my office presence without manual record-keeping
- As a system administrator, I want to configure multiple users with individual settings so that the system can track attendance for my entire team

## Specific Requirements

**Multi-User Configuration System**
- Read user configurations from unified JSON file at configurable path (default: `config/myki_config.json`)
- JSON structure: top-level "users" object with username keys and nested user-specific settings: `mykiCardNumber`, `targetStation`, `skipDates` (array), `startDate`, `endDate`
- **Simplified username pattern**: The config key itself (e.g., "koustubh") IS the Myki username used for login (no separate mykiUsername field needed)
- Passwords stored in environment variables with pattern: `MYKI_PASSWORD_{USERNAME}` where USERNAME is uppercase version of config key
- Example: Config key "koustubh" → Myki username is "koustubh" → Set `MYKI_PASSWORD_KOUSTUBH` in .env
- System fails with clear error message if environment variable for any configured user is missing
- Validate JSON schema on load: all required fields present, dates in ISO format (YYYY-MM-DD), card numbers are strings
- Support sequential processing of all users in single execution (cron-friendly)

**Working Days Calculation Logic**
- Define working day as Monday through Friday only
- Automatically exclude public holidays for Melbourne, Victoria, Australia using Python `holidays` package
- Exclude user-specific skip dates from configuration (e.g., personal leave, known absences)
- Working day determination must occur before checking attendance records
- Date comparison performed using date objects (not datetime) to avoid timezone issues

**Authenticated API Integration**
- Reuse `MykiAPIClient` from `/Users/gaikwadk/Documents/station-station-agentos/src/myki_api_client.py`
- Call existing `get_transactions(card_number, page)` method for each user
- Authentication handled by existing client using saved session data from `auth_loader.py`
- No need to re-implement authentication logic
- API endpoint: `POST https://mykiapi.ptv.vic.gov.au/v2/myki/transactions?page={page}` (already implemented in client)

**Pagination Handling with Special Error Case**
- Start pagination at page 0, increment sequentially
- Implement safety limit of 5 pages maximum per user to prevent infinite loops
- Handle special API error: `{"code":409,"message":"txnTimestamp: Expected a non-empty value. Got: null"}` when page > 0
- This 409 error is NORMAL and indicates end of available data, not a failure condition
- Stop pagination gracefully when this error occurs and continue to next user
- All other HTTP errors should be treated as actual failures and logged appropriately

**Transaction Parsing and Filtering**
- Parse API response to extract transaction objects from response data
- Filter transactions by exact station name match (case-sensitive) in `description` field
- Filter by `transactionType` field equals "Touch off"
- Client-side date range filtering: filter transactions between user's `startDate` and `endDate` after fetching from API
- Extract `transactionDateTime` field for date comparison (parse ISO datetime string to date object)
- Count touches: if >= 1 "Touch off" at target station on a working day, mark day as attended

**Attendance Data Model (Output)**
- Single combined JSON file for all users at: `output/attendance.json`
- Top-level structure: object with username keys (same as config file keys)
- Per-user object contains: `attendanceDays` (array of ISO date strings), `latestProcessedDate` (ISO date string or null), `targetStation` (string), `lastUpdated` (ISO timestamp), `statistics` (object)
- `attendanceDays` array lists all dates where user touched off at target station
- `latestProcessedDate` tracks most recent transaction date processed for incremental updates
- `statistics` object contains: `totalWorkingDays`, `daysAttended`, `daysMissed`, `attendancePercentage`, `firstAttendance`, `lastAttendance`, `periodStart`, `periodEnd`, `monthlyBreakdown` (array)
- `monthlyBreakdown` array contains monthly statistics: `month` (YYYY-MM), `workingDays`, `daysAttended`, `daysMissed`, `attendancePercentage`
- Include metadata: generation timestamp, config file path used, total users processed

**Incremental Processing Logic**
- On first run, `latestProcessedDate` is null, process all transactions in date range
- On subsequent runs, only process transactions after `latestProcessedDate` to avoid re-processing
- Update `latestProcessedDate` to most recent transaction datetime found in current run
- If no new transactions found, keep existing `latestProcessedDate`
- Merge new attendance days with existing days, removing duplicates
- Ensure output file is created if it doesn't exist, updated if it does

**Error Handling and Logging**
- Log authentication failures with user-friendly message suggesting password check
- Handle missing config file with clear error message including expected path
- Handle malformed JSON config with specific syntax error details
- Log API failures (non-409 errors) with HTTP status code and response body
- Validate date formats and provide clear error for invalid dates
- Use print statements for logging (no complex logging framework needed initially)
- Continue processing other users if one user fails, collect and report all errors at end

**Date Range and Skip Dates**
- `startDate` and `endDate` define the inclusive range for processing transactions
- If transaction date is outside this range, skip it (client-side filtering)
- `skipDates` array processed as ISO date strings, convert to date objects for comparison
- Skip dates take precedence: if date is in skipDates, exclude from working days even if Mon-Fri
- Public holidays automatically excluded via `holidays` package without explicit configuration

**Dependencies and File Structure**
- Add `holidays` package to requirements.txt for public holiday detection
- Reuse existing `MykiAPIClient` and `auth_loader` modules (supports per-user sessions via `MYKI_AUTH_USERNAME_KEY`)
- Output directory: `output/` (create if doesn't exist)
- Config directory: `config/` (create if doesn't exist)
- Main script location: `src/run_myki_workflow.py` (orchestrates Phase 1 auth + Phase 2 tracking)
- Core modules: `src/myki_attendance_tracker.py`, `src/config_manager.py`, `src/working_days.py`, `src/transaction_fetcher.py`, `src/transaction_processor.py`, `src/output_manager.py`
- Example config file provided at: `config/myki_config.example.json`
- Per-user session files: `auth_data/session_{username}.json`, `auth_data/cookies_{username}.json`, etc.

**Statistics Calculation**
- Calculate overall statistics: total working days, days attended, days missed, attendance percentage
- Calculate monthly breakdown: for each month in the period, track working days, attended days, missed days, and percentage
- Working days calculation respects: weekends (Sat/Sun), Melbourne VIC public holidays, user-specific skip dates
- Statistics included in output JSON for easy consumption by frontend/dashboards

## Existing Code to Leverage

**MykiAPIClient (`/Users/gaikwadk/Documents/station-station-agentos/src/myki_api_client.py`)**
- Provides `get_transactions(card_number, page)` method that handles authentication, headers, cookies, and Bearer token
- Returns parsed JSON response with transaction data
- Already implements proper error handling with `raise_for_status()`
- Requires authenticated session loaded via `auth_loader.py`
- Reuse this client directly, do not re-implement API logic

**auth_loader.py (`/Users/gaikwadk/Documents/station-station-agentos/src/auth_loader.py`)**
- Provides `load_session_data()` function returning tuple of (cookies, headers, auth_request, bearer_token)
- Loads from `auth_data/session.json` file
- Already handles missing file errors with clear messages
- Pattern to follow: initialize `MykiAPIClient()` without parameters to auto-load session
- No need to implement custom session loading logic

**Session data structure (from auth_data/session.json)**
- JSON file contains cookies, headers, auth_request, and bearer_token
- Bearer token format is JWT with expiry timestamp
- Session includes PassthruAuth cookie and x-passthruauth header
- Pattern shows how authentication data is structured and stored
- Follow similar JSON structure approach for config and output files

**Existing requirements.txt pattern**
- Current dependencies use specific version pinning (e.g., `requests==2.32.5`)
- Add `holidays` package with pinned version for reproducible builds
- Project uses python-dotenv for environment variables - leverage for password loading

**JSON file handling pattern (from auth_loader.py)**
- Use `Path` from `pathlib` for cross-platform file paths
- Use `json.load()` and `json.dump()` for JSON operations
- Check file existence with `path.exists()` before reading
- Provide helpful error messages when files missing
- Replicate this pattern for config and output file handling

## Out of Scope
- Cron job configuration or scheduling setup (user configures cron separately)
- Frontend implementation or UI components (JSON file is the interface)
- User authentication system or login functionality (uses existing Myki auth only)
- Fuzzy or partial station name matching (exact match only)
- Weekend or custom working day definitions (Monday-Friday only, not configurable)
- Multi-city or multi-region support (Melbourne VIC only)
- Real-time notifications or alerts for attendance changes
- Historical data migration or backward compatibility with other formats
- Database storage (file-based JSON only)
- Retry logic or exponential backoff for API failures (fail fast on errors except 409)
