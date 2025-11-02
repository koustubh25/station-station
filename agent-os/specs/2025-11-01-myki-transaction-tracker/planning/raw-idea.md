# Raw Idea

**Feature: Myki Transaction Tracker - Work Attendance Monitor**

Description:
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
