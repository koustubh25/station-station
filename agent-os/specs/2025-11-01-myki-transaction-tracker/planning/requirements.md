# Spec Requirements: Myki Transaction Tracker - Work Attendance Monitor

## Initial Description

Build a system that uses the authenticated Myki API client to track work attendance by monitoring "Touch off" events at a specific station.

Key Requirements:
1. Use the authenticated API client from the myki-authentication-bypass spec
2. Call the transactions endpoint: `POST https://mykiapi.ptv.vic.gov.au/v2/myki/transactions?page={page}`
3. Parse transaction data looking for:
   - transactionType: "Touch off"
   - description: matches target station name (e.g., "Heathmont Station")
4. Generate JSON output file tracking work attendance days
5. Implement pagination to handle large date ranges
6. Track the latest processed transaction date to avoid re-querying same data
7. Designed to run as a cron job
8. Output indicates if user attended work on specific days (touched off >= 1 time at target station)

Technical Details:
- Request requires myki card number in POST body: {"mykiCardNumber":"123456789012345"}
- Response format includes: transactionType, serviceType, transactionDateTime, zone, description, etc.
- Need to handle pagination via ?page=0, ?page=1, etc.
- Store latest processed date in output file for incremental updates

Dependencies:
- Requires completed myki-authentication-bypass spec (authentication tokens, API client)

## Requirements Discussion

### First Round Questions

**Q1: Multi-User Configuration - Will the system track attendance for a single user or support multiple users?**

**Answer:** Multiple users

Follow-up: How should multiple users be configured?
- Use JSON config file for all fields EXCEPT passwords
- Passwords stored in environment variables with pattern: `MYKI_PASSWORD_{username}`
- Username is the key in the JSON structure

Example config.json:
```json
{
  "users": {
    "koustubh": {
      "mykiCardNumber": "123456789012345",
      "targetStation": "Heathmont Station",
      "skipDates": ["2025-03-15", "2025-06-20"],
      "startDate": "2025-04-15",
      "endDate": "2025-06-15"
    }
  }
}
```

Environment variable for password: `MYKI_PASSWORD_KOUSTUBH`

**Q2: Output File Structure - Should the system generate one JSON file per user or combine all users in a single file?**

**Answer:** One combined JSON file
- Use username as the key (e.g., "koustubh", NOT "user1")
- Structure with username keys for each user's data

**Q3: Skip Dates Configuration - Should skip dates be configurable per user?**

**Answer:** Yes, skip dates are configurable per user
- Format: JSON array in the config file (e.g., `["2025-03-15", "2025-06-20"]`)

**Q4: Public Holiday Integration - Should the system automatically exclude public holidays from working days?**

**Answer:** Yes, automatically exclude public holidays
- Use Python `holidays` package: https://pypi.org/project/holidays/
- Location: Melbourne, Victoria, Australia

**Q5: Station Name Matching - Should station name matching be exact or fuzzy?**

**Answer:** Exact match (case-sensitive)

**Q6: Working Days Definition - What constitutes a "working day" for attendance calculation?**

**Answer:** Monday-Friday, excluding public holidays and skip dates

**Q7: Cron Job Execution - Should the cron job run separately for each user or process all users in one execution?**

**Answer:** Single job processing all users sequentially

**Q8: Pagination Safety - Should there be a maximum page limit to prevent infinite loops?**

**Answer:** Yes, implement 5-page safety limit
- **IMPORTANT**: If API returns `{"code":409,"message":"txnTimestamp: Expected a non-empty value. Got: null"}` when page > 0, treat this as NORMAL (not an error)
- This error means no more pages available
- Continue program execution normally when this occurs

**Q9: Date Range Filtering - Should filtering be done via API parameters or client-side?**

**Answer:** Client-side filtering
- Fetch all transactions from the API
- Filter by date range in code after receiving response

**Q10: Frontend Integration - How should the backend make data available to the frontend?**

**Answer:** Write to JSON file
- Frontend reads the file directly
- Return JSON as-is (no transformation needed)

### Existing Code to Reference

**Similar Features Identified:**
- Myki Authentication Bypass spec: Authentication tokens, API client setup
- Path: Expected at `/Users/gaikwadk/Documents/station-station-agentos/agent-os/specs/myki-authentication-bypass/` (or similar)
- Reuse: Authenticated session handling, API client patterns, header/cookie management

No other similar features identified for reference.

### Follow-up Questions

None required - all requirements clarified.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A - No visual files found in planning folder.

## Requirements Summary

### Functional Requirements

**Core Functionality:**
- Fetch Myki transaction data from authenticated API endpoint
- Support multiple users with individual configurations
- Parse transactions to identify "Touch off" events at designated work stations
- Calculate work attendance based on working days (Mon-Fri, excluding holidays/skip dates)
- Generate combined JSON output file with attendance data for all users
- Track latest processed transaction date for incremental updates
- Support pagination with safety limits
- Handle API pagination end-of-data error gracefully

**User Actions Enabled:**
- Configure multiple users with individual Myki credentials and settings
- Define target work stations per user
- Specify custom skip dates per user
- Set date ranges for attendance tracking
- Automated cron-based execution for daily updates

**Data to be Managed:**
- User configurations (card numbers, target stations, skip dates, date ranges)
- User passwords (stored securely in environment variables)
- Transaction history from Myki API
- Attendance records (daily touch-off events)
- Latest processed transaction timestamps
- Public holiday calendar for Melbourne, VIC

### Reusability Opportunities

**Components that might exist already:**
- Authentication client from myki-authentication-bypass spec
- Session management and API header handling
- Cookie and token extraction patterns

**Backend patterns to investigate:**
- HTTP client setup with authentication headers
- API response parsing logic
- Error handling for API failures

**Similar features to model after:**
- Myki authentication bypass spec for API client architecture

### Scope Boundaries

**In Scope:**
- Multi-user configuration via JSON file
- Password management via environment variables (pattern: `MYKI_PASSWORD_{username}`)
- Fetching transaction data from Myki API using authenticated client
- Parsing "Touch off" events for designated stations
- Exact station name matching (case-sensitive)
- Working day calculation (Mon-Fri, excluding public holidays and skip dates)
- Public holiday integration using Python `holidays` package for Melbourne, VIC
- Pagination handling with 5-page safety limit
- Graceful handling of pagination end-of-data error (409 with null txnTimestamp)
- Client-side date range filtering
- Combined JSON output file with username-keyed data structure
- Tracking latest processed transaction date
- Cron job support (single execution processing all users sequentially)
- Frontend integration via direct JSON file reading

**Out of Scope:**
- Cron job configuration/setup (not handled by this spec)
- Frontend implementation (separate concern)
- User authentication/login system
- Fuzzy station name matching
- Weekend or custom working day definitions
- Real-time notifications
- Data visualization
- Multi-city or multi-region support (only Melbourne, VIC)
- Backward compatibility for legacy data formats

### Technical Considerations

**Integration Points:**
- Myki API endpoint: `POST https://mykiapi.ptv.vic.gov.au/v2/myki/transactions?page={page}`
- Authentication client from myki-authentication-bypass spec
- Python `holidays` package for public holiday data
- Environment variables for password storage
- JSON configuration file for user settings
- JSON output file for frontend consumption

**Existing System Constraints:**
- Depends on completed myki-authentication-bypass spec
- Must maintain authenticated session across API calls
- API requires mykiCardNumber in POST body
- Pagination via query parameter: `?page=0`, `?page=1`, etc.
- API response includes: transactionType, serviceType, transactionDateTime, zone, description

**Technology Preferences:**
- Python 3.x (per product tech stack)
- Python `holidays` package for public holiday detection
- JSON for configuration and output
- Environment variables for secrets management

**Similar Code Patterns to Follow:**
- Authentication and API client patterns from myki-authentication-bypass spec
- DRY principle (avoid code duplication)
- Small, focused functions
- Automated code formatting
- No backward compatibility concerns unless explicitly required

### Design Decisions and Assumptions

**Configuration Architecture:**
- JSON file stores non-sensitive data (card numbers, stations, dates)
- Environment variables store passwords with naming convention: `MYKI_PASSWORD_{USERNAME}` (uppercase username)
- Username serves as the unique identifier across config and output

**Error Handling:**
- API error `{"code":409,"message":"txnTimestamp: Expected a non-empty value. Got: null"}` when page > 0 is NORMAL
- This specific error indicates end of pagination, not a failure condition
- Program should continue execution normally when this occurs
- Other API errors should be handled as actual failures

**Pagination Strategy:**
- Start at page=0, increment sequentially
- Maximum 5 pages per user (safety limit)
- Stop early if pagination end-of-data error is encountered
- All transaction data fetched first, then filtered client-side

**Working Day Logic:**
- Monday through Friday only
- Exclude public holidays (Melbourne, Victoria, Australia)
- Exclude user-specific skip dates
- Attendance = at least 1 "Touch off" at target station on a working day

**Data Output:**
- Single JSON file for all users
- Username-keyed structure (e.g., "koustubh" as key)
- Include latest processed transaction date per user for incremental updates
- Frontend reads file directly without transformation

**Execution Model:**
- Designed for cron job execution
- Process all users sequentially in single execution
- No parallel/concurrent processing required
