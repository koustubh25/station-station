# Feature Description

Security and Manual Attendance Enhancements for Station Station

## Requirements

### 1. Credential Security Enhancement

- Move Myki username and card number from config file to environment variables (similar to password)
- Add a `username` field in config file for frontend display purposes only
- Use a mapping pattern where config key (e.g., "koustubh") maps to environment variables:
  - MYKI_USERNAME_KOUSTUBH=koustubh25
  - MYKI_CARDNUMBER_KOUSTUBH=12321

Example config structure:
```json
{
  "users": {
    "koustubh": {
      "targetStation": "Southern Cross Station",
      "skipDates": ["2025-03-15", "2025-06-20"],
      "startDate": "2025-04-15"
    }
  }
}
```

### 2. Manual Attendance Dates

- Add support for manually specified attendance dates (for days when user drove to work instead of using PTV)
- New array field similar to `skipDates` (e.g., `manualAttendanceDates`)
- Frontend should display these dates with red circles, identical to PTV-detected attendance days
- Should be included in attendance percentage calculations
