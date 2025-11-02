# Task Breakdown: Myki Transaction Tracker - Work Attendance Monitor

## Overview
Total Tasks: 4 Task Groups
Implementation Strategy: Python-based CLI tool with multi-user configuration system

## Task List

### Configuration & Infrastructure Setup

#### Task Group 1: Project Setup and Dependencies
**Dependencies:** None

- [x] 1.0 Complete project setup and dependencies
  - [x] 1.1 Update requirements.txt with holidays package
    - Add `holidays>=0.35` to `/Users/gaikwadk/Documents/station-station-agentos/requirements.txt`
    - Pin version for reproducible builds (follow existing pattern in requirements.txt)
  - [x] 1.2 Create directory structure
    - Create `/Users/gaikwadk/Documents/station-station-agentos/config/` directory if not exists
    - Create `/Users/gaikwadk/Documents/station-station-agentos/output/` directory if not exists
  - [x] 1.3 Create example configuration file
    - Create `/Users/gaikwadk/Documents/station-station-agentos/config/myki_tracker_config.example.json`
    - Include multi-user JSON structure with required and optional fields
    - Add comments as JSON (using special comment keys) explaining each field
    - Example structure (skipDates and endDate are optional):
      ```json
      {
        "koustubh": {
          "mykiCardNumber": "123456789012345",
          "targetStation": "Heathmont Station",
          "skipDates": ["2025-03-15", "2025-06-20"],
          "startDate": "2025-04-15",
          "endDate": "2025-06-15"
        }
      }
      ```
    - Note: Required fields are mykiCardNumber, targetStation, startDate
    - Optional: skipDates (defaults to []), endDate (defaults to current date)
  - [x] 1.4 Document environment variable pattern
    - Add documentation in example config about password environment variables
    - Pattern: `MYKI_PASSWORD_{USERNAME}` where USERNAME is uppercase version of config key
    - Example: For user "koustubh", set `MYKI_PASSWORD_KOUSTUBH`

**Acceptance Criteria:**
- holidays package added to requirements.txt with version pinning
- config/ and output/ directories created
- Example config file contains complete, valid JSON structure
- Environment variable pattern clearly documented

---

### Core Business Logic Implementation

#### Task Group 2: Configuration Loading and Validation
**Dependencies:** Task Group 1 (COMPLETED)

- [x] 2.0 Complete configuration management system
  - [x] 2.1 Write 2-4 focused tests for configuration loading
    - Test: Valid JSON config loads successfully with all required fields
    - Test: Missing environment variable for user raises clear error
    - Test: Invalid date format in config raises validation error
    - Optional test: Missing required field in config raises schema error
    - Store tests in `/Users/gaikwadk/Documents/station-station-agentos/tests/test_myki_attendance_tracker.py`
  - [x] 2.2 Implement load_user_config() function
    - Accept config_path parameter (default: `config/myki_tracker_config.json`)
    - Use `pathlib.Path` for cross-platform file path handling (follow pattern from auth_loader.py)
    - Check file existence with `path.exists()`, raise clear error if missing
    - Use `json.load()` for JSON parsing (follow pattern from auth_loader.py)
    - Return parsed configuration dictionary
  - [x] 2.3 Implement validate_user_config() function
    - Validate JSON schema: check all required fields present per user
    - Required fields: mykiCardNumber, targetStation, startDate
    - Optional fields: skipDates (defaults to empty array), endDate (defaults to current date)
    - Validate date formats: must be ISO format (YYYY-MM-DD)
    - Validate mykiCardNumber: must be string
    - Validate skipDates: must be array of ISO date strings (if provided)
    - Validate endDate: must be ISO format (if provided)
    - Raise ValueError with specific field name if validation fails
  - [x] 2.4 Implement load_user_passwords() function
    - Accept user_config dictionary from load_user_config()
    - For each username key, load environment variable `MYKI_PASSWORD_{USERNAME.upper()}`
    - Use `os.getenv()` for environment variable access
    - Collect missing passwords and fail with clear error listing all missing vars
    - Return dictionary mapping username to password
  - [x] 2.4a Implement get_effective_end_date() helper function
    - Accept user_config and username parameters
    - Return endDate if present in config
    - Return current date (date.today()) if endDate not specified
    - Return as ISO format string (YYYY-MM-DD)
  - [x] 2.4b Implement get_effective_skip_dates() helper function
    - Accept user_config and username parameters
    - Return skipDates if present in config
    - Return empty array if skipDates not specified
    - Return as list of ISO date strings
  - [x] 2.5 Ensure configuration tests pass
    - Run ONLY the 2-4 tests written in 2.1
    - Verify valid config loads correctly
    - Verify validation catches invalid dates and missing fields
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All tests pass (6 tests total including optional field tests)
- Config file loads with proper error handling for missing file
- JSON schema validation catches all required field violations (mykiCardNumber, targetStation, startDate)
- Optional fields (skipDates, endDate) properly handled with defaults
- Date format validation enforces ISO format (YYYY-MM-DD)
- Password loading fails fast with clear message listing all missing environment variables
- Helper functions return correct defaults for optional fields
- Follows pathlib and json patterns from auth_loader.py

---

#### Task Group 3: Working Days Calculation Logic
**Dependencies:** Task Group 2 (COMPLETED)

- [x] 3.0 Complete working days calculation system
  - [x] 3.1 Write 2-4 focused tests for working day logic
    - Test: Monday-Friday dates identified as potential working days
    - Test: Saturday-Sunday excluded from working days
    - Test: Melbourne VIC public holiday excluded from working days
    - Optional test: User skip date excluded from working days
    - Store tests in `/Users/gaikwadk/Documents/station-station-agentos/tests/test_myki_attendance_tracker.py`
  - [x] 3.2 Initialize holidays package for Melbourne VIC
    - Import `holidays` package
    - Initialize with: `holidays.country_holidays('AU', subdiv='VIC')`
    - Store as module-level or class-level constant
    - Reference: https://pypi.org/project/holidays/
  - [x] 3.3 Implement is_working_day() function
    - Parameters: date_obj (date), skip_dates (list of date objects), vic_holidays (holidays object)
    - Return boolean: True if working day, False otherwise
    - Logic: Monday-Friday AND NOT in vic_holidays AND NOT in skip_dates
    - Use date.weekday() method: 0-4 = Mon-Fri, 5-6 = Sat-Sun
    - Date comparison using date objects (not datetime) to avoid timezone issues
  - [x] 3.4 Implement parse_skip_dates() helper function
    - Accept skipDates array of ISO strings from config
    - Parse each string to date object using `datetime.strptime(date_str, '%Y-%m-%d').date()`
    - Return list of date objects
    - Handle parse errors with clear message indicating which date failed
  - [x] 3.5 Ensure working days tests pass
    - Run ONLY the 2-4 tests written in 3.1
    - Verify weekday logic correctly identifies Mon-Fri
    - Verify public holidays properly excluded
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 3.1 pass (7 tests total including parse_skip_dates tests)
- is_working_day() correctly identifies Monday-Friday
- Melbourne VIC public holidays automatically excluded
- User skip dates properly excluded
- Date parsing handles ISO format correctly
- No datetime/timezone confusion (uses date objects only)

---

#### Task Group 4: Transaction Fetching and Pagination
**Dependencies:** Task Group 3 (COMPLETED)

- [x] 4.0 Complete transaction fetching with special pagination handling
  - [x] 4.1 Write 2-4 focused tests for pagination logic
    - Test: Fetch transactions from page 0 successfully
    - Test: Stop pagination when 409 error with "txnTimestamp: Expected a non-empty value. Got: null" occurs (treat as normal)
    - Test: Respect 5-page safety limit
    - Optional test: Handle non-409 HTTP errors as actual failures
    - Mock `MykiAPIClient.get_transactions()` for tests
    - Store tests in `/Users/gaikwadk/Documents/station-station-agentos/tests/test_myki_attendance_tracker.py`
  - [x] 4.2 Import and initialize MykiAPIClient
    - Import from `/Users/gaikwadk/Documents/station-station-agentos/src/myki_api_client.py`
    - Initialize once: `client = MykiAPIClient()` (auto-loads session from auth_loader.py)
    - Reuse client instance for all users (no need to re-initialize per user)
    - Reference existing pattern: MykiAPIClient() loads session automatically
  - [x] 4.3 Implement fetch_all_transactions() function
    - Parameters: client (MykiAPIClient), card_number (str)
    - Initialize: page = 0, all_transactions = [], MAX_PAGES = 5
    - Loop: while page < MAX_PAGES
      - Call `client.get_transactions(card_number, page)`
      - Handle special case: catch requests.HTTPError with status 409
        - Check error message contains "txnTimestamp: Expected a non-empty value. Got: null"
        - If matches: break loop gracefully (this is NORMAL end-of-data signal, not error)
        - If different 409 error: raise as actual error
      - Handle other HTTP errors: log error with status code and response, raise exception
      - Parse response to extract transaction array (API returns object with transactions list)
      - Extend all_transactions list with new transactions
      - Increment page
    - Return all_transactions list
  - [x] 4.4 Implement is_special_pagination_error() helper function
    - Parameters: http_error (requests.HTTPError)
    - Check: status_code == 409
    - Check: error message contains "txnTimestamp: Expected a non-empty value. Got: null"
    - Return boolean: True if special pagination end-of-data error, False otherwise
    - Purpose: Distinguish normal pagination end from actual API errors
  - [x] 4.5 Ensure pagination tests pass
    - Run ONLY the 2-4 tests written in 4.1
    - Verify special 409 error handled gracefully (no exception raised)
    - Verify 5-page limit enforced
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 4.1 pass
- MykiAPIClient properly imported and initialized with auto-loaded session
- Pagination starts at page 0, increments sequentially
- Special 409 error (null txnTimestamp) treated as normal end-of-data
- Other API errors logged and raised appropriately
- 5-page safety limit prevents infinite loops
- Follows error handling pattern from myki_api_client.py

**Special Note on 409 Error:**
The API returns `{"code":409,"message":"txnTimestamp: Expected a non-empty value. Got: null"}` when there are no more pages of transactions available. This is NOT an error condition - it's the API's way of signaling end-of-data. The implementation must:
1. Catch this specific 409 error
2. Stop pagination gracefully
3. Continue processing the next user
4. NOT log this as an error or failure

---

#### Task Group 5: Transaction Filtering and Attendance Tracking
**Dependencies:** Task Group 4 (COMPLETED)

- [x] 5.0 Complete transaction filtering and attendance calculation
  - [x] 5.1 Write 2-4 focused tests for filtering logic
    - Test: Filter transactions by exact station name match (case-sensitive)
    - Test: Filter transactions by transactionType == "Touch off"
    - Test: Filter transactions within user date range (startDate to endDate inclusive)
    - Optional test: Extract transactionDateTime and convert to date for comparison
    - Store tests in `/Users/gaikwadk/Documents/station-station-agentos/tests/test_myki_attendance_tracker.py`
  - [x] 5.2 Implement parse_transaction_date() helper function
    - Parameter: transaction_datetime_str (ISO datetime string from API)
    - Parse using `datetime.fromisoformat()` or `datetime.strptime()`
    - Convert datetime to date object: `.date()`
    - Return date object for comparison
    - Handle parse errors gracefully (skip transaction, log warning)
  - [x] 5.3 Implement filter_transactions() function
    - Parameters: transactions (list), target_station (str), start_date (date), end_date (date)
    - Filter by: transaction['description'] == target_station (exact match, case-sensitive)
    - Filter by: transaction['transactionType'] == "Touch off"
    - Filter by: start_date <= parse_transaction_date(transaction['transactionDateTime']) <= end_date
    - Return filtered list of transactions
  - [x] 5.4 Implement calculate_attendance_days() function
    - Parameters: transactions (filtered list), skip_dates (list of dates), vic_holidays (holidays object)
    - Extract transaction dates from each transaction
    - Filter to only working days using is_working_day()
    - Remove duplicates: convert to set, then back to sorted list
    - Return list of ISO date strings (YYYY-MM-DD format)
    - Logic: if >= 1 touch-off at target station on working day, include that day
  - [x] 5.5 Ensure filtering tests pass
    - Run ONLY the 2-4 tests written in 5.1
    - Verify exact station name matching (case-sensitive)
    - Verify "Touch off" filtering
    - Verify date range filtering
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 5.1 pass
- Station name matching is exact and case-sensitive
- Only "Touch off" transactions counted
- Date range filtering works with inclusive bounds
- Attendance days calculated correctly (>= 1 touch-off on working day)
- Duplicate dates removed from attendance days
- Output is sorted list of ISO date strings

---

#### Task Group 6: Incremental Processing and Output Generation
**Dependencies:** Task Group 5 (COMPLETED)

- [x] 6.0 Complete incremental processing and JSON output
  - [x] 6.1 Write 2-4 focused tests for incremental processing
    - Test: First run (no existing output) processes all transactions, sets latestProcessedDate
    - Test: Subsequent run only processes transactions after latestProcessedDate
    - Test: Merge new attendance days with existing days (no duplicates)
    - Optional test: Update lastUpdated timestamp on each run
    - Store tests in `/Users/gaikwadk/Documents/station-station-agentos/tests/test_myki_attendance_tracker.py`
  - [x] 6.2 Implement load_existing_output() function
    - Path: `/Users/gaikwadk/Documents/station-station-agentos/output/attendance.json`
    - If file doesn't exist, return empty dict {}
    - If exists, load with `json.load()` and return
    - Handle JSON parse errors gracefully (log warning, return empty dict)
  - [x] 6.3 Implement get_latest_processed_date() function
    - Parameters: existing_output (dict), username (str)
    - If username not in existing_output, return None
    - If username exists, get latestProcessedDate field
    - If latestProcessedDate is null/None, return None
    - Parse ISO datetime string to datetime object and return
    - Used to determine which transactions are "new" vs "already processed"
  - [x] 6.4 Implement filter_new_transactions() function
    - Parameters: transactions (list), latest_processed_date (datetime or None)
    - If latest_processed_date is None, return all transactions (first run)
    - Otherwise, filter to transactions where transactionDateTime > latest_processed_date
    - Return filtered list
  - [x] 6.5 Implement update_user_output() function
    - Parameters: existing_output (dict), username (str), new_attendance_days (list), latest_txn_datetime (datetime or None), target_station (str)
    - Get existing user data or initialize empty
    - Merge new_attendance_days with existing attendanceDays (remove duplicates, sort)
    - Update latestProcessedDate: use max of existing and latest_txn_datetime
    - Set targetStation
    - Set lastUpdated to current ISO timestamp
    - Return updated user object
  - [x] 6.6 Implement save_output() function
    - Parameters: output_data (dict)
    - Path: `/Users/gaikwadk/Documents/station-station-agentos/output/attendance.json`
    - Add metadata: generatedAt (ISO timestamp), configPath, totalUsers
    - Write with `json.dump()` with indent=2 for readability
    - Use pathlib.Path for file operations (follow auth_loader.py pattern)
    - Create output directory if doesn't exist
  - [x] 6.7 Ensure incremental processing tests pass
    - Run ONLY the 2-4 tests written in 6.1
    - Verify first run processes all transactions
    - Verify subsequent runs only process new transactions
    - Verify attendance days properly merged
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 6.1 pass
- First run (no existing output) processes all transactions in date range
- Subsequent runs only process transactions after latestProcessedDate
- New attendance days merged with existing days (no duplicates)
- latestProcessedDate updated to most recent transaction datetime
- Output file created if doesn't exist, updated if it does
- JSON output is well-formatted (indented) for human readability
- Follows file handling pattern from auth_loader.py (pathlib.Path, json.load/dump)

**Output JSON Structure:**
```json
{
  "metadata": {
    "generatedAt": "2025-11-01T14:30:00Z",
    "configPath": "config/myki_tracker_config.json",
    "totalUsers": 1
  },
  "koustubh": {
    "attendanceDays": ["2025-04-15", "2025-04-16", "2025-04-17"],
    "latestProcessedDate": "2025-04-17T18:30:00",
    "targetStation": "Heathmont Station",
    "lastUpdated": "2025-11-01T14:30:00Z"
  }
}
```

---

#### Task Group 7: Main Orchestration and Error Handling
**Dependencies:** Task Groups 2-6

- [x] 7.0 Complete main orchestration and multi-user processing
  - [x] 7.1 Write 2-4 focused tests for orchestration
    - Test: Process multiple users sequentially
    - Test: Continue processing other users if one user fails
    - Test: Collect and report all errors at end
    - Optional test: Successful run returns exit code 0
    - Store tests in `/Users/gaikwadk/Documents/station-station-agentos/tests/test_myki_attendance_tracker.py`
  - [x] 7.2 Implement process_user() function
    - Parameters: username (str), user_config (dict), password (str), client (MykiAPIClient), existing_output (dict), vic_holidays
    - Orchestrate all steps for one user:
      1. Parse user config (card number, station, dates, skip dates)
      2. Fetch all transactions (handle pagination)
      3. Filter new transactions (incremental processing)
      4. Filter by station, type, and date range
      5. Calculate attendance days (working days only)
      6. Update output data for user
    - Return tuple: (success: bool, user_output_data: dict or None, error: Exception or None)
    - Catch all exceptions within function, return them (don't raise)
    - Use print statements for user-friendly logging at each step
  - [x] 7.3 Implement main() function
    - Initialize: config_path from CLI arg or default
    - Load and validate user config
    - Load user passwords from environment variables
    - Initialize MykiAPIClient once (reuse for all users)
    - Initialize Melbourne VIC holidays object
    - Load existing output file
    - Initialize results tracking: successes = [], failures = []
    - Loop through all users sequentially:
      - Call process_user() for each user
      - Collect successes and failures
      - Continue on error (don't stop processing other users)
    - Merge all successful user outputs
    - Save combined output file
    - Print summary: X/Y users processed successfully
    - If any failures, print error details for each
    - Return exit code: 0 if all success, 1 if any failures
  - [x] 7.4 Implement CLI entry point
    - Add `if __name__ == '__main__':` block
    - Support optional config path argument: `python myki_attendance_tracker.py [config_path]`
    - Use sys.argv for simple argument parsing (no argparse needed initially)
    - Call main() and exit with returned code: `sys.exit(main())`
  - [x] 7.5 Add user-friendly error messages
    - Authentication failure: "Failed to authenticate for user X. Check password in MYKI_PASSWORD_X"
    - Missing config file: "Config file not found at: [path]. Create config file first."
    - Malformed JSON: "Invalid JSON in config file: [syntax error details]"
    - API failure (non-409): "API request failed for user X: HTTP [status] - [response]"
    - Invalid date format: "Invalid date format in config for user X, field Y: expected YYYY-MM-DD"
    - All errors should use print statements (no complex logging framework)
  - [x] 7.6 Ensure orchestration tests pass
    - Run ONLY the 2-4 tests written in 7.1
    - Verify multi-user sequential processing
    - Verify error isolation (one user's failure doesn't stop others)
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-4 tests written in 7.1 pass
- All users processed sequentially in single execution (cron-friendly)
- One user's failure doesn't prevent other users from processing
- All errors collected and reported at end with clear messages
- Exit code 0 if all users succeed, 1 if any failures
- User-friendly error messages for all failure scenarios
- Uses print statements for logging (no complex framework)
- Follows fail-fast pattern for missing config/invalid schema
- Follows graceful degradation for per-user API failures

**File Location:**
Create main script at: `/Users/gaikwadk/Documents/station-station-agentos/src/myki_attendance_tracker.py`

---

### Testing & Validation

#### Task Group 8: Integration Testing and Validation
**Dependencies:** Task Groups 1-7

- [x] 8.0 Review and validate complete system (COMPLETED)
  - [x] 8.1 Review all tests from Task Groups 2-7
    - Count total tests: should be approximately 12-24 tests (2-4 per group × 6 groups)
    - Verify tests cover:
      - Configuration loading and validation
      - Working day calculation
      - Pagination with special 409 error handling
      - Transaction filtering
      - Incremental processing
      - Multi-user orchestration
  - [x] 8.2 Run all feature tests together
    - Run: `pytest tests/test_myki_attendance_tracker.py -v`
    - Verify all 12-24 tests pass
    - Do NOT run entire application test suite
    - Focus only on this feature's tests
  - [x] 8.3 Perform automated end-to-end test
    - Create test config file with 2 users
    - Set environment variables for both users
    - Run automated end-to-end tests
    - Verify output/attendance.json created with correct structure
    - Test incremental processing (should only process new transactions)
    - Verify latestProcessedDate updated correctly
    - Test with invalid config to verify error handling
    - Test with missing environment variable to verify failure message
  - [x] 8.4 Test special 409 pagination error handling
    - Automated verification: 409 "txnTimestamp: Expected a non-empty value. Got: null" handled gracefully
    - Verify: No exception raised for special 409 error
    - Verify: Processing continues to next user gracefully
    - Verify: Other 409 errors still raise exceptions
  - [x] 8.5 Validate output JSON structure
    - Check metadata fields: generatedAt, configPath, totalUsers
    - Check per-user fields: attendanceDays, latestProcessedDate, targetStation, lastUpdated
    - Verify attendanceDays is sorted array of ISO date strings
    - Verify no duplicate dates in attendanceDays
    - Verify latestProcessedDate is ISO datetime string or null
    - Verify lastUpdated is ISO timestamp
  - [x] 8.6 Test error scenarios
    - Missing config file: verify clear error message with expected path
    - Malformed JSON config: verify syntax error details shown
    - Missing environment variable: verify lists all missing vars
    - Invalid date format: verify field name and expected format shown
    - API failure: verify HTTP status and response logged
    - One user fails: verify other users still process successfully

**Acceptance Criteria:**
- ✅ All 29 unit tests pass (from Task Groups 2-7)
- ✅ All 11 integration tests pass (Task Group 8)
- ✅ Total: 40 tests passing
- ✅ End-to-end automated test completes successfully
- ✅ Incremental processing works (only new transactions processed)
- ✅ Special 409 pagination error handled gracefully (no error logged)
- ✅ Output JSON structure matches specification exactly
- ✅ All error scenarios produce clear, actionable error messages
- ✅ Multi-user processing isolated (one failure doesn't affect others)

---

### Post-Implementation Enhancements

#### Task Group 9: Code Refactoring and Modularization (COMPLETED)
**Status:** ✅ COMPLETED

- [x] 9.0 Refactor monolithic myki_attendance_tracker.py into focused modules
  - [x] 9.1 Created `src/config_manager.py` - Configuration loading and validation
  - [x] 9.2 Created `src/working_days.py` - Working day calculations with holiday handling
  - [x] 9.3 Created `src/transaction_fetcher.py` - Transaction fetching with special 409 error handling
  - [x] 9.4 Created `src/transaction_processor.py` - Transaction filtering and attendance calculation
  - [x] 9.5 Created `src/output_manager.py` - JSON output generation and incremental processing
  - [x] 9.6 Reduced main file from 1214 lines to 326 lines (73% reduction)
  - [x] 9.7 All 40 tests passing after refactoring

#### Task Group 10: Workflow Automation (COMPLETED)
**Status:** ✅ COMPLETED

- [x] 10.0 Create automated workflow orchestrator
  - [x] 10.1 Created `src/run_myki_workflow.py` - Orchestrates Phase 1 (auth) + Phase 2 (tracking)
  - [x] 10.2 Implemented pre-flight validation - checks all requirements before time-consuming auth
  - [x] 10.3 Multi-user authentication loop - authenticates all users sequentially
  - [x] 10.4 Per-user session management - each user gets `session_{username}.json`
  - [x] 10.5 Error isolation - one user's failure doesn't stop processing of other users
  - [x] 10.6 Exit codes: 0 for success, 1 for any failures (cron-friendly)

#### Task Group 11: Statistics and Analytics (COMPLETED)
**Status:** ✅ COMPLETED

- [x] 11.0 Add attendance statistics calculation
  - [x] 11.1 Implemented overall statistics:
    - Total working days in period
    - Days attended
    - Days missed
    - Attendance percentage
    - First and last attendance dates
  - [x] 11.2 Implemented monthly breakdown:
    - Per-month working days calculation
    - Per-month attendance tracking
    - Per-month attendance percentage
    - Monthly statistics array in output
  - [x] 11.3 Statistics respect all working day rules (weekends, holidays, skip dates)
  - [x] 11.4 Statistics included in output JSON for frontend consumption

#### Task Group 12: Bug Fixes and Production Readiness (COMPLETED)
**Status:** ✅ COMPLETED

- [x] 12.0 Fix critical 409 pagination error bug
  - [x] 12.1 Root cause: `requests.Response` objects evaluate to False for 4xx/5xx status codes
  - [x] 12.2 Fixed by using `is None` instead of truthy checks
  - [x] 12.3 Special 409 error now correctly recognized as end-of-data signal
  - [x] 12.4 Workflow completes successfully end-to-end
- [x] 12.1 Code cleanup
  - [x] Removed obsolete config files (old format)
  - [x] Removed temporary test files
  - [x] Cleaned up __pycache__ directories
  - [x] Updated .gitignore for better security
- [x] 12.2 Documentation updates
  - [x] Updated README.md with statistics feature
  - [x] Updated SETUP.md with multi-user examples
  - [x] Updated agent-os spec documentation
  - [x] Updated agent-os tasks documentation

**Total Tests:** 40 passing (29 unit + 11 integration)

---

## Execution Order

Recommended implementation sequence:
1. **Configuration & Infrastructure Setup** (Task Group 1) - Set up project structure and dependencies
2. **Configuration Loading and Validation** (Task Group 2) - Load and validate user configs
3. **Working Days Calculation Logic** (Task Group 3) - Implement business logic for working days
4. **Transaction Fetching and Pagination** (Task Group 4) - Integrate with Myki API, handle special 409 error
5. **Transaction Filtering and Attendance Tracking** (Task Group 5) - Filter transactions and calculate attendance
6. **Incremental Processing and Output Generation** (Task Group 6) - Handle incremental updates and JSON output
7. **Main Orchestration and Error Handling** (Task Group 7) - Tie everything together with multi-user processing
8. **Integration Testing and Validation** (Task Group 8) - Comprehensive testing and validation

## Key Implementation Notes

### Existing Code to Reuse

**MykiAPIClient** (`/Users/gaikwadk/Documents/station-station-agentos/src/myki_api_client.py`):
- Use `get_transactions(card_number, page)` method for fetching transaction data
- Initialize once without parameters: `client = MykiAPIClient()` (auto-loads session)
- Already handles authentication, headers, cookies, and Bearer token
- Raises `requests.HTTPError` on API failures (use this for error handling)

**auth_loader.py** (`/Users/gaikwadk/Documents/station-station-agentos/src/auth_loader.py`):
- Reference for file handling patterns: pathlib.Path, json.load/dump
- Reference for error handling: check file.exists(), clear error messages
- MykiAPIClient automatically uses this for session loading (no need to call directly)

### Special Pagination Error Handling

**Critical Implementation Detail:**

The Myki API returns this error when there are no more pages:
```json
{"code":409,"message":"txnTimestamp: Expected a non-empty value. Got: null"}
```

This is **NOT an error** - it's the normal way the API signals end-of-data. Implementation must:
1. Catch `requests.HTTPError` with status_code 409
2. Check if message contains "txnTimestamp: Expected a non-empty value. Got: null"
3. If yes: stop pagination gracefully, continue to next user (no error logging)
4. If no (different 409 error): treat as actual error and raise

Other HTTP errors should be treated as actual failures.

### Testing Strategy

- Each task group (2-7) writes 2-4 focused tests maximum
- Tests run only the newly written tests (not entire suite)
- Task Group 8 runs all feature tests together (approximately 12-24 total)
- Focus on critical behaviors, not exhaustive coverage
- Mock MykiAPIClient for unit tests, use real client for integration tests

### Multi-User Configuration Pattern

**Config File** (`config/myki_config.json`):
```json
{
  "users": {
    "koustubh": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Heathmont Station",
      "skipDates": ["2025-03-15", "2025-06-20"],
      "startDate": "2025-04-15",
      "endDate": "2025-06-15"
    },
    "john": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Melbourne Central",
      "startDate": "2025-01-01"
    }
  }
}
```

**Simplified Username Pattern:**
- **Config key IS the Myki username**: The key "koustubh" IS the Myki username used for login
- **No separate mykiUsername field needed**: Simplified configuration structure
- **Required fields:** mykiCardNumber, targetStation, startDate
- **Optional fields:** skipDates (defaults to []), endDate (defaults to current date)
- In the example above, "john" omits skipDates and endDate, which will use defaults

**Environment Variables:**
- `MYKI_PASSWORD_KOUSTUBH` for user "koustubh" (config key → Myki username)
- `MYKI_PASSWORD_JOHN` for user "john" (config key → Myki username)

**Per-User Sessions:**
- Each user gets their own session file: `auth_data/session_koustubh.json`, `auth_data/session_john.json`
- Session file naming uses the config key (username) as suffix

### Working Days Logic

Working day = **Monday-Friday** AND **NOT a public holiday** AND **NOT in skip dates**

- Use `date.weekday()`: 0-4 = Mon-Fri, 5-6 = Sat-Sun
- Use `holidays.country_holidays('AU', subdiv='VIC')` for Melbourne public holidays
- Compare using date objects (not datetime) to avoid timezone confusion

### Incremental Processing Flow

**First Run (no existing output):**
1. latestProcessedDate is null
2. Process all transactions in user's date range (startDate to endDate)
3. Calculate attendance days
4. Set latestProcessedDate to most recent transaction datetime
5. Save output

**Subsequent Runs (existing output exists):**
1. Load latestProcessedDate from existing output
2. Fetch all transactions via API (same as first run)
3. Filter to only transactions where transactionDateTime > latestProcessedDate
4. Calculate attendance days for new transactions
5. Merge new attendance days with existing days (remove duplicates)
6. Update latestProcessedDate to max(existing, latest new transaction)
7. Save output

### Date Handling

- **Config dates**: ISO strings (YYYY-MM-DD) → parse to date objects
- **Transaction dates**: ISO datetime strings → parse to datetime, then extract .date()
- **Comparisons**: Always use date objects (not datetime) for day-level comparisons
- **Output dates**: Convert date objects back to ISO strings (YYYY-MM-DD)
- **Timestamps**: Use ISO format with timezone for lastUpdated and generatedAt

### Error Handling Philosophy

- **Fail fast**: Invalid config, missing passwords → stop immediately with clear error
- **Graceful degradation**: One user's API failure → log error, continue with other users
- **Special case**: 409 null txnTimestamp → normal end-of-data, not an error
- **User-friendly messages**: All errors should be actionable (tell user what to fix)
- **Logging**: Use print statements (no complex framework needed)

### Cron Job Compatibility

- Single execution processes all users sequentially
- Returns exit code 0 (success) or 1 (any failures)
- No interactive input required
- No persistent state between runs (uses output file for incremental processing)
- Safe to run multiple times (idempotent for same time period)
