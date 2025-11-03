# Specification: Security and Manual Attendance Enhancements

## Goal
Enhance security by moving Myki credentials from config file to environment variables, and add support for manually specified attendance dates to track car commutes.

## User Stories
- As a user, I want my Myki credentials (username, card number) stored securely in environment variables rather than in the config file, so that sensitive data is not exposed in version control
- As a user, I want to manually record attendance dates when I drove to work instead of using PTV, so that my attendance calculations are accurate
- As a user, I want manual attendance dates displayed with a distinct visual appearance, so I can easily distinguish them from PTV-detected attendance

## Specific Requirements

**Credential Security Enhancement**
- Remove `mykiCardNumber` field from config file completely (breaking change, no backward compatibility)
- Config key (e.g., "koustubh") should be DIFFERENT from actual PTV username for security
- Environment variable pattern: `MYKI_<TYPE>_<CONFIG_KEY>` where TYPE is USERNAME, CARDNUMBER, or PASSWORD
- Config keys converted to UPPERCASE in environment variable names (e.g., "koustubh" becomes MYKI_USERNAME_KOUSTUBH)
- Optional `username` field in config for frontend display purposes only (fallback to config key if not provided)
- Extend existing `load_user_passwords()` function to load username and card number from environment variables
- Consider renaming `load_user_passwords()` to `load_user_credentials()` for clarity
- Raise clear error messages if required environment variables are missing

**Manual Attendance Configuration**
- Add optional `manualAttendanceDates` array field to user config (similar to `skipDates`)
- Field defaults to empty array if not specified
- Each user has their own `manualAttendanceDates` array in multi-user setups
- Manual dates stored as YYYY-MM-DD format strings (consistent with existing date format)
- Manual dates override `skipDates` if conflicts occur (manual takes precedence)
- Date format validation using YYYY-MM-DD regex pattern (same as skipDates validation)
- Date range validation to ensure manual dates fall within user's startDate and endDate range
- Invalid manual dates should raise errors (not warnings) to prevent silent failures

**Output JSON Structure Changes**
- Keep manual attendance dates SEPARATE from PTV-detected attendance in output JSON
- Add new top-level field `manualAttendanceDates` in user output (parallel to `attendanceDays`)
- Structure: `{"attendanceDays": ["2025-01-15"], "manualAttendanceDates": ["2025-01-17"]}`
- Include manual dates in statistics calculations (totalWorkingDays, daysAttended, attendancePercentage)
- Maintain existing `attendanceDays` field for PTV-detected attendance
- Sort manual dates chronologically in output

**Frontend Visualization - Calendar Color Scheme**
- Add new color constant `MANUAL_ATTENDANCE_COLOR` (suggest orange #fb923c or amber #f59e0b)
- Manual attendance dates displayed with encircled style (similar to regular attendance)
- Regular PTV attendance continues to use existing red color (#ef4444)
- Update CalendarView component to render manual dates with different color
- Update `tileClassName` function to detect manual dates and apply appropriate CSS class
- Handle click events on manual dates to show AttendanceDetails modal

**Frontend Visualization - AttendanceDetails Modal**
- Display "Manually recorded" text for manual attendance dates
- Do NOT show timestamp or station information for manual dates (not applicable)
- Show same date formatting as PTV attendance
- Keep existing modal layout and accessibility features
- Handle conditional rendering based on whether date is manual or PTV-detected

**Calculation Updates**
- Manual attendance dates counted in "days attended" statistics
- Manual dates included in total attendance percentage calculation
- Manual dates counted in monthly breakdown statistics
- Manual dates NOT counted as "days missed"
- Filter logic should combine manual dates with PTV dates for total attendance count

**Data Validation Logic**
- Validate manual dates format using same pattern as skipDates (YYYY-MM-DD)
- Validate manual dates fall within startDate to endDate range
- If date appears in both skipDates and manualAttendanceDates, manualAttendanceDates takes precedence
- Validate environment variables exist for username and card number during config load
- Provide clear error messages indicating which environment variables are missing

**Migration Requirements**
- Update `.env.example` with examples of new environment variable structure
- Update `SETUP.md` with comprehensive migration guide
- Provide example of old config format vs new config format
- Include migration checklist with step-by-step instructions
- Document breaking changes clearly in migration guide
- No automatic migration scripts (users must manually update configs)

## Visual Design

No visual assets provided. Based on existing codebase analysis:

**Calendar appearance for manual attendance:**
- Use orange (#fb923c) or amber (#f59e0b) encircled dates
- Maintain same encircled style as regular red attendance dates
- Ensure sufficient color contrast for accessibility
- Add distinct ARIA labels for screen readers

**AttendanceDetails modal for manual dates:**
- Same modal layout and structure as PTV attendance
- Show date in same format ("Month Day, Year")
- Replace timestamp section with "Manually recorded" text
- Omit station information section entirely for manual dates

## Existing Code to Leverage

**Environment variable loading pattern from `load_user_passwords()` in config_manager.py**
- Reuse pattern of constructing environment variable name from config key
- Follow uppercase conversion logic (username.upper())
- Maintain consistent error handling for missing environment variables
- Extend existing validation and error message structure
- Preserve logging pattern for loaded credentials

**Calendar encircled date styling from CalendarView.jsx**
- Reuse `.attended-day` CSS pattern with different color
- Follow same `tileClassName` logic for applying CSS classes
- Maintain existing hover effects and accessibility features
- Leverage `toLocaleDateString('en-CA')` for date formatting consistency
- Use same click handler pattern for modal trigger

**Date validation pattern from `validate_user_config()` in config_manager.py**
- Reuse `datetime.strptime(date, '%Y-%m-%d')` validation
- Follow same error message structure for invalid dates
- Apply same validation to manualAttendanceDates as skipDates
- Maintain consistent ValueError raising pattern

**AttendanceDetails modal structure from AttendanceDetails.jsx**
- Reuse modal wrapper, backdrop, and close button components
- Follow same accessibility patterns (focus trap, Escape key, ARIA labels)
- Maintain same responsive styling and layout
- Use conditional rendering to show different content for manual vs PTV dates
- Preserve keyboard navigation and click-outside-to-close behavior

**Statistics calculation pattern from output_manager.py**
- Extend `calculate_statistics()` to merge manual dates with attendance dates
- Combine manualAttendanceDates with attendanceDays before calculations
- Maintain existing monthly breakdown calculation logic
- Preserve attendance percentage formula and rounding rules
- Keep same return structure for statistics object

## Out of Scope

- UI interface for adding or editing manual attendance dates (config file editing only)
- Validation UI for date conflicts or warnings
- Automatic detection of manual vs PTV attendance
- Bulk import/export functionality for manual dates
- CSV import for bulk manual date entry
- Historical migration scripts or automated config conversion
- Calendar editing functionality (UI remains read-only)
- Admin UI for managing manual attendance dates
- Conflict detection warnings in the frontend UI
- Backward compatibility with old config format containing mykiCardNumber
