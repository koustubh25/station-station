# Task Breakdown: Security and Manual Attendance Enhancements

## Overview
Total Tasks: 8 Task Groups
Feature Type: Security Enhancement + Manual Attendance Feature
Breaking Changes: YES - Config format change (no backward compatibility)
Repositories: Backend (station-station) + Frontend (attendance-tracker)

## Task List

### Backend - Task Group 1: Credential Security Schema Changes
**Dependencies:** None
**Repository:** station-station
**Critical Path:** BLOCKS all other backend tasks

- [ ] 1.0 Complete credential security schema changes
  - [ ] 1.1 Write 2-8 focused tests for credential loading
    - Test environment variable loading pattern for username
    - Test environment variable loading pattern for card number
    - Test missing credential environment variable error handling
    - Test config key uppercase conversion (e.g., "koustubh" -> MYKI_USERNAME_KOUSTUBH)
    - Test display username fallback to config key when username field not provided
    - Limit to 2-8 critical tests maximum
  - [ ] 1.2 Update config schema in config_manager.py
    - Remove `mykiCardNumber` field from schema validation completely
    - Add optional `username` field for frontend display purposes only
    - Remove `mykiCardNumber` from example config structures in docstrings
    - Update validation logic to reject configs with `mykiCardNumber` present
  - [ ] 1.3 Extend load_user_passwords() function
    - Rename function to `load_user_credentials()` for clarity
    - Add username loading from `MYKI_USERNAME_<CONFIG_KEY>` environment variable
    - Add card number loading from `MYKI_CARDNUMBER_<CONFIG_KEY>` environment variable
    - Apply uppercase conversion to config key in variable names
    - Raise clear ValueError if MYKI_USERNAME_* is missing
    - Raise clear ValueError if MYKI_CARDNUMBER_* is missing
    - Maintain existing password loading logic
    - Update all function calls from load_user_passwords() to load_user_credentials()
  - [ ] 1.4 Add credential validation error messages
    - Include specific missing environment variable name in error messages
    - Example: "Missing environment variable: MYKI_USERNAME_KOUSTUBH"
    - Include instructions pointing to .env.example for reference
  - [ ] 1.5 Update .env.example file
    - Add MYKI_USERNAME_* variable examples
    - Add MYKI_CARDNUMBER_* variable examples
    - Include comments explaining the mapping pattern
    - Show example with multiple users (at least 2)
  - [ ] 1.6 Ensure credential security tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify environment variable loading works correctly
    - Verify error handling for missing credentials
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Config schema rejects `mykiCardNumber` field
- Credentials loaded from environment variables with correct naming pattern
- Clear error messages for missing credentials
- .env.example updated with examples

---

### Backend - Task Group 2: Manual Attendance Configuration
**Dependencies:** Task Group 1
**Repository:** station-station

- [ ] 2.0 Complete manual attendance configuration
  - [ ] 2.1 Write 2-8 focused tests for manual attendance
    - Test manualAttendanceDates array parsing and validation
    - Test date format validation (YYYY-MM-DD pattern)
    - Test date range validation (within startDate/endDate)
    - Test conflict resolution (manual takes precedence over skipDates)
    - Test empty array default when manualAttendanceDates not specified
    - Limit to 2-8 critical tests maximum
  - [ ] 2.2 Add manualAttendanceDates to config schema
    - Add optional `manualAttendanceDates` field (array of strings)
    - Default to empty array [] if not specified
    - Each user has independent manualAttendanceDates array
    - Update config validation in validate_user_config()
  - [ ] 2.3 Implement date format validation
    - Reuse existing YYYY-MM-DD validation pattern from skipDates
    - Use datetime.strptime(date, '%Y-%m-%d') for validation
    - Raise ValueError for invalid date formats (not warnings)
    - Include specific date and user in error messages
  - [ ] 2.4 Implement date range validation
    - Validate manual dates >= user's startDate
    - Validate manual dates <= user's endDate (or current date)
    - Raise ValueError for out-of-range dates (not warnings)
    - Include date, range, and user in error messages
  - [ ] 2.5 Implement conflict resolution logic
    - Add logic to detect dates in both manualAttendanceDates and skipDates
    - Manual attendance takes precedence over skip dates
    - Remove conflicting dates from effective skipDates
    - Log info message when conflicts are resolved
  - [ ] 2.6 Sort manual dates chronologically
    - Sort manualAttendanceDates array after validation
    - Maintain chronological order in output JSON
  - [ ] 2.7 Ensure manual attendance config tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify date validation and conflict resolution
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- Config schema accepts manualAttendanceDates array
- Date format and range validation works correctly
- Manual dates override skip dates in conflicts
- Dates sorted chronologically in output

---

### Backend - Task Group 3: Output JSON Structure Changes
**Dependencies:** Task Group 2
**Repository:** station-station

- [ ] 3.0 Complete output JSON structure changes
  - [ ] 3.1 Write 2-8 focused tests for JSON output
    - Test manualAttendanceDates appears as separate top-level field
    - Test attendanceDays remains separate from manual dates
    - Test statistics calculations include manual dates
    - Test empty manualAttendanceDates array when no manual dates specified
    - Limit to 2-8 critical tests maximum
  - [ ] 3.2 Update output_manager.py JSON structure
    - Add `manualAttendanceDates` as separate top-level field in user output
    - Keep existing `attendanceDays` field for PTV-detected attendance
    - Structure: {"attendanceDays": [...], "manualAttendanceDates": [...]}
    - Include manualAttendanceDates even when empty (consistency)
  - [ ] 3.3 Update statistics calculation in calculate_statistics()
    - Merge manualAttendanceDates with attendanceDays for total count
    - Include manual dates in daysAttended calculation
    - Include manual dates in attendancePercentage calculation
    - Include manual dates in monthly breakdown statistics
    - Do NOT count manual dates as daysMissed
  - [ ] 3.4 Update monthly breakdown logic
    - Combine manual and PTV dates when calculating monthly attendance
    - Maintain existing monthly grouping logic
    - Preserve existing return structure
  - [ ] 3.5 Ensure output JSON tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify JSON structure is correct
    - Verify statistics include manual dates
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- JSON output has separate manualAttendanceDates field
- Statistics calculations include manual dates in totals
- Monthly breakdown includes both manual and PTV dates

---

### Frontend - Task Group 4: Constants and Color Scheme
**Dependencies:** Backend Task Group 3 (for JSON structure)
**Repository:** attendance-tracker

- [ ] 4.0 Complete color constants and scheme
  - [ ] 4.1 Write 2-8 focused tests for constants
    - Test MANUAL_ATTENDANCE_COLOR constant is defined
    - Test color value is valid hex format
    - Test color contrast meets accessibility standards
    - Limit to 2-8 critical tests maximum (may be fewer for constants)
  - [ ] 4.2 Add MANUAL_ATTENDANCE_COLOR constant
    - Add to src/constants/config.js or create src/constants/colors.js
    - Define constant: MANUAL_ATTENDANCE_COLOR = '#fb923c' (orange)
    - Alternative: '#f59e0b' (amber) if orange too similar to red
    - Add JSDoc comment explaining purpose: "Color for manually recorded attendance dates"
  - [ ] 4.3 Document color scheme
    - Add comment block documenting full color scheme:
      - ATTENDED_DAY_COLOR = '#ef4444' (red) - PTV-detected attendance
      - MANUAL_ATTENDANCE_COLOR = '#fb923c' (orange) - Manual attendance
      - Skip dates: no marking (gap in calendar)
    - Export new constant for use in components
  - [ ] 4.4 Ensure color constant tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify constant is exported correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass (if tests needed)
- MANUAL_ATTENDANCE_COLOR constant defined
- Color scheme documented in code comments
- Constant exported and accessible to components

---

### Frontend - Task Group 5: Calendar Visualization
**Dependencies:** Task Group 4
**Repository:** attendance-tracker

- [ ] 5.0 Complete calendar visualization
  - [ ] 5.1 Write 2-8 focused tests for calendar rendering
    - Test manual attendance dates render with correct color class
    - Test manual dates have encircled style
    - Test manual dates are clickable (trigger modal)
    - Test tileClassName function applies correct CSS class
    - Test ARIA labels for manual dates include "Manual attendance"
    - Limit to 2-8 critical tests maximum
  - [ ] 5.2 Update CalendarView.jsx component
    - Import MANUAL_ATTENDANCE_COLOR constant
    - Parse manualAttendanceDates from userData JSON
    - Store in component state or derive from props
  - [ ] 5.3 Update tileClassName function
    - Add detection for manual attendance dates
    - Return 'manual-attendance-day' class for manual dates
    - Return 'attended-day' class for PTV dates
    - Maintain existing logic for other date types
    - Use toLocaleDateString('en-CA') for date comparison consistency
  - [ ] 5.4 Add CSS styling for manual dates
    - Create .manual-attendance-day CSS class
    - Apply encircled style similar to .attended-day
    - Use MANUAL_ATTENDANCE_COLOR for border/background
    - Ensure sufficient contrast for accessibility (WCAG AA)
    - Add hover effects matching existing attendance dates
  - [ ] 5.5 Update click handler for manual dates
    - Ensure onClick triggers AttendanceDetails modal for manual dates
    - Pass date and isManual flag to modal
    - Reuse existing modal trigger pattern
  - [ ] 5.6 Add ARIA labels for accessibility
    - Update ariaLabel function to detect manual dates
    - Use "Manual attendance on [date]" for manual dates
    - Use "Attended on [date]" for PTV dates
    - Ensure screen readers announce difference
  - [ ] 5.7 Ensure calendar visualization tests pass
    - Run ONLY the 2-8 tests written in 5.1
    - Verify manual dates render with orange circles
    - Verify click behavior works
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 5.1 pass
- Manual dates render with orange/amber encircled style
- Manual dates are clickable and trigger modal
- ARIA labels distinguish manual from PTV attendance
- Sufficient color contrast for accessibility

---

### Frontend - Task Group 6: Attendance Details Modal
**Dependencies:** Task Group 5
**Repository:** attendance-tracker

- [ ] 6.0 Complete attendance details modal
  - [ ] 6.1 Write 2-8 focused tests for modal content
    - Test modal shows "Manually recorded" for manual dates
    - Test modal does NOT show timestamp for manual dates
    - Test modal does NOT show station info for manual dates
    - Test modal shows correct date formatting
    - Test modal accessibility (focus trap, Escape key)
    - Limit to 2-8 critical tests maximum
  - [ ] 6.2 Update AttendanceDetails.jsx modal component
    - Add isManual prop or detect manual status from date
    - Implement conditional rendering based on isManual flag
    - Maintain existing modal structure (wrapper, backdrop, close button)
  - [ ] 6.3 Implement conditional content rendering
    - If isManual === true:
      - Display "Manually recorded" text
      - Omit timestamp section entirely
      - Omit station information section entirely
      - Show only date in same format: "Month Day, Year"
    - If isManual === false:
      - Show existing PTV attendance details (timestamp, stations)
      - Maintain current display logic
  - [ ] 6.4 Update modal styling
    - Reuse existing modal layout and responsive styles
    - Ensure manual content is properly aligned
    - Maintain consistent padding and spacing
  - [ ] 6.5 Preserve accessibility features
    - Keep focus trap behavior
    - Keep Escape key close functionality
    - Keep click-outside-to-close behavior
    - Keep keyboard navigation
    - Update ARIA labels to reflect manual vs PTV content
  - [ ] 6.6 Ensure modal tests pass
    - Run ONLY the 2-8 tests written in 6.1
    - Verify conditional rendering works correctly
    - Verify accessibility features maintained
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 6.1 pass
- Modal displays "Manually recorded" for manual dates
- No timestamp or station info shown for manual dates
- Same date formatting as PTV attendance
- All accessibility features maintained

---

### Frontend - Task Group 7: Data Processing and Calculations
**Dependencies:** Task Group 6
**Repository:** attendance-tracker

- [ ] 7.0 Complete data processing and calculations
  - [ ] 7.1 Write 2-8 focused tests for data processing
    - Test useFilteredData hook parses manualAttendanceDates correctly
    - Test calculations.js includes manual dates in attendance totals
    - Test attendance percentage includes manual dates
    - Test monthly stats include manual dates
    - Limit to 2-8 critical tests maximum
  - [ ] 7.2 Update useFilteredData.js hook
    - Parse manualAttendanceDates array from userData JSON
    - Handle empty manualAttendanceDates gracefully (default to [])
    - Validate manualAttendanceDates is array before processing
    - Make manualAttendanceDates available to components
  - [ ] 7.3 Update calculations.js utility
    - Import or accept manualAttendanceDates as parameter
    - Merge manualAttendanceDates with attendanceDays for total count
    - Update daysAttended calculation to include manual dates
    - Update attendancePercentage calculation to include manual dates
    - Update monthly breakdown to include manual dates
    - Do NOT count manual dates in daysMissed
  - [ ] 7.4 Update filtering logic
    - Ensure manual dates take precedence over skip dates
    - Filter out skip dates that conflict with manual dates
    - Maintain existing date filtering patterns
  - [ ] 7.5 Update dataFetcher.js validation
    - Validate JSON structure includes manualAttendanceDates field
    - Handle missing manualAttendanceDates field gracefully (backward compatibility)
    - Validate manualAttendanceDates is array type
    - Log warning if manualAttendanceDates is malformed
  - [ ] 7.6 Ensure data processing tests pass
    - Run ONLY the 2-8 tests written in 7.1
    - Verify manual dates parsed correctly
    - Verify calculations include manual dates
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 7.1 pass
- Manual dates parsed from JSON correctly
- Statistics calculations include manual dates
- Attendance percentage accounts for manual attendance
- Monthly breakdown includes both manual and PTV dates

---

### Documentation - Task Group 8: Migration Guide and Documentation
**Dependencies:** All previous task groups
**Repositories:** Both station-station and attendance-tracker

- [ ] 8.0 Complete documentation and migration guide
  - [ ] 8.1 Update backend SETUP.md (station-station repo)
    - Add "Migration Guide for Credential Security" section
    - Document breaking changes clearly:
      - Removal of mykiCardNumber from config
      - Move to environment variables required
      - No backward compatibility
    - Provide step-by-step migration instructions:
      1. Backup existing config.json
      2. Extract mykiCardNumber values from config
      3. Extract actual username if different from config key
      4. Add MYKI_USERNAME_* to .env for each user
      5. Add MYKI_CARDNUMBER_* to .env for each user
      6. Remove mykiCardNumber from config.json
      7. Optionally add username field for display
      8. Test credential loading with new setup
    - Show example of old config format vs new config format
    - Include migration checklist
    - Add troubleshooting section for common issues
  - [ ] 8.2 Update backend .env.example (station-station repo)
    - Add comprehensive examples with 2+ users
    - Include all three credential types:
      - MYKI_USERNAME_USER1=actual_username
      - MYKI_CARDNUMBER_USER1=1234567890
      - MYKI_PASSWORD_USER1=secret_password
    - Add comments explaining mapping pattern
    - Show uppercase conversion example
  - [ ] 8.3 Update backend README.md (station-station repo)
    - Add "Security Enhancements" section
    - Document environment variable approach
    - Link to SETUP.md for detailed migration guide
    - Update feature list to mention manual attendance
    - Add security rationale explanation
  - [ ] 8.4 Document manual attendance feature in backend
    - Add section in SETUP.md explaining manualAttendanceDates
    - Provide use case: "Track car commute days"
    - Show config example with manualAttendanceDates array
    - Document date format requirements (YYYY-MM-DD)
    - Document validation rules (format, range)
    - Document conflict resolution (manual overrides skip)
    - Explain separate storage in output JSON
  - [ ] 8.5 Update frontend README.md (attendance-tracker repo)
    - Add manual attendance to feature list
    - Document color coding:
      - Red circles: PTV-detected attendance
      - Orange circles: Manual attendance
    - Explain distinction in UI
    - Update screenshot if applicable (or note missing)
  - [ ] 8.6 Create migration checklist document
    - Create MIGRATION.md or add to SETUP.md
    - Provide printable/checkable task list:
      - [ ] Backup config.json
      - [ ] Extract mykiCardNumber values
      - [ ] Add MYKI_CARDNUMBER_* to .env
      - [ ] Add MYKI_USERNAME_* to .env if different from key
      - [ ] Remove mykiCardNumber from config.json
      - [ ] Test application starts without errors
      - [ ] Verify attendance tracking still works
      - [ ] Add manualAttendanceDates if needed
    - Include rollback instructions
  - [ ] 8.7 Document environment variable naming convention
    - Create reference table in documentation:
      | Config Key | Environment Variable | Example Value |
      |------------|---------------------|---------------|
      | koustubh   | MYKI_USERNAME_KOUSTUBH | koustubh25 |
      | koustubh   | MYKI_CARDNUMBER_KOUSTUBH | 1234567890 |
      | koustubh   | MYKI_PASSWORD_KOUSTUBH | secret |
    - Document uppercase conversion rule
    - Explain security separation (config key != actual username)

**Acceptance Criteria:**
- SETUP.md includes comprehensive migration guide
- .env.example shows all required environment variables
- README files updated in both repositories
- Manual attendance feature fully documented
- Migration checklist provides clear step-by-step process
- Security rationale explained
- Troubleshooting guidance provided

---

## Testing & Validation - Task Group 9: End-to-End Testing and Gap Analysis
**Dependencies:** Task Groups 1-8
**Repositories:** Both station-station and attendance-tracker

- [ ] 9.0 Review existing tests and fill critical gaps only
  - [ ] 9.1 Review tests from previous task groups
    - Review the 2-8 tests written by backend for credentials (Task 1.1)
    - Review the 2-8 tests written by backend for manual config (Task 2.1)
    - Review the 2-8 tests written by backend for JSON output (Task 3.1)
    - Review the 2-8 tests written by frontend for colors (Task 4.1)
    - Review the 2-8 tests written by frontend for calendar (Task 5.1)
    - Review the 2-8 tests written by frontend for modal (Task 6.1)
    - Review the 2-8 tests written by frontend for calculations (Task 7.1)
    - Total existing tests: approximately 14-56 tests
  - [ ] 9.2 Analyze test coverage gaps for this feature only
    - Identify critical end-to-end workflows that lack test coverage
    - Focus ONLY on gaps related to this spec's requirements:
      - Credential loading from environment variables end-to-end
      - Manual attendance full workflow (config -> output -> display)
      - Conflict resolution between manual and skip dates
      - Statistics accuracy with manual dates included
      - Migration path validation
    - Do NOT assess entire application test coverage
    - Prioritize integration tests over unit test gaps
  - [ ] 9.3 Write up to 10 additional strategic tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on integration points between backend and frontend
    - Suggested integration tests:
      - Full credential loading workflow (env vars -> config -> scraper)
      - Manual attendance end-to-end (config -> JSON -> UI rendering)
      - Conflict resolution integration test (manual overrides skip)
      - Statistics calculation with mixed manual + PTV dates
      - Frontend parsing of new JSON structure
      - Modal display for both manual and PTV dates
    - Do NOT write comprehensive coverage for all scenarios
    - Skip edge cases, performance tests unless business-critical
  - [ ] 9.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature
    - Expected total: approximately 24-66 tests maximum
    - Backend tests: credential loading, config validation, JSON output
    - Frontend tests: color constants, calendar rendering, modal, calculations
    - Integration tests: end-to-end workflows
    - Do NOT run entire application test suite
    - Verify all critical workflows pass
  - [ ] 9.5 Perform manual testing validation
    - Test credential loading with missing environment variables
    - Test manual attendance rendering with different date counts
    - Test conflict resolution (manual vs skip dates)
    - Test calendar click behavior for manual dates
    - Test modal content for manual vs PTV dates
    - Test statistics accuracy with manual dates
    - Test migration path with sample old config
  - [ ] 9.6 Document testing coverage
    - List which workflows are covered by automated tests
    - Note any gaps that require manual testing
    - Document test data setup requirements
    - Create sample test configs for manual testing

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 24-66 tests total)
- Critical user workflows for this feature are covered
- No more than 10 additional tests added when filling in testing gaps
- Testing focused exclusively on this spec's requirements
- Manual testing validates end-to-end functionality
- Test coverage documented

---

## Execution Order

Recommended implementation sequence:

**Phase 1: Backend Security Foundation (CRITICAL PATH)**
1. Task Group 1: Credential Security Schema Changes
   - BLOCKS: All other backend work
   - Breaking change - must be completed first
   - Estimated: High priority

**Phase 2: Backend Manual Attendance Logic**
2. Task Group 2: Manual Attendance Configuration
   - Depends on: Task Group 1
   - BLOCKS: Task Group 3
   - Estimated: Medium priority

3. Task Group 3: Output JSON Structure Changes
   - Depends on: Task Group 2
   - BLOCKS: All frontend work
   - Estimated: Medium priority

**Phase 3: Frontend Visual Updates**
4. Task Group 4: Constants and Color Scheme
   - Depends on: Task Group 3 (JSON structure)
   - BLOCKS: Task Group 5
   - Estimated: Low complexity

5. Task Group 5: Calendar Visualization
   - Depends on: Task Group 4
   - BLOCKS: Task Group 6
   - Estimated: Medium priority

6. Task Group 6: Attendance Details Modal
   - Depends on: Task Group 5
   - Can run in parallel with: Task Group 7
   - Estimated: Low complexity

7. Task Group 7: Data Processing and Calculations
   - Depends on: Task Group 5
   - Can run in parallel with: Task Group 6
   - Estimated: Medium priority

**Phase 4: Documentation and Testing**
8. Task Group 8: Documentation and Migration Guide
   - Depends on: Task Groups 1-7 (all implementation complete)
   - Can run in parallel with: Task Group 9
   - Estimated: High priority (user-facing)

9. Task Group 9: End-to-End Testing and Gap Analysis
   - Depends on: Task Groups 1-7 (all implementation complete)
   - Can run in parallel with: Task Group 8
   - Final validation before release
   - Estimated: High priority

---

## Breaking Changes Alert

**CRITICAL: This feature includes breaking changes**

- Config file format change (removal of `mykiCardNumber` field)
- No backward compatibility for old config format
- All users MUST migrate to new environment variable pattern
- Application will fail to start without migration
- Migration is manual - no automated scripts provided

**User Impact:**
- All existing users must update their configuration
- Requires editing both config.json and .env files
- Downtime during migration
- Clear migration guide must be provided

**Mitigation:**
- Comprehensive migration documentation (Task Group 8)
- Clear error messages for missing environment variables (Task Group 1)
- Example configurations in .env.example
- Step-by-step migration checklist

---

## Additional Notes

**Repository Context:**
- Backend repository: station-station (Python-based scraper)
- Frontend repository: attendance-tracker (React-based UI)
- Both repositories require changes for complete feature

**Security Improvements:**
- Actual usernames removed from config file
- Card numbers removed from config file
- All sensitive credentials in environment variables only
- Config file can be safely version controlled
- Reduced attack surface for credential exposure

**Testing Philosophy:**
- Focus on critical workflows, not exhaustive coverage
- Each task group writes 2-8 tests maximum during development
- Test gap analysis adds maximum of 10 additional tests
- Total expected: 24-66 tests for entire feature
- Manual testing validates end-to-end functionality

**Files to Modify (Estimated):**

Backend (station-station):
- config_manager.py
- output_manager.py
- myki_tracker.py or credential loader file
- .env.example
- SETUP.md
- README.md

Frontend (attendance-tracker):
- src/constants/config.js or src/constants/colors.js
- src/components/CalendarView.jsx
- src/components/AttendanceDetails.jsx
- src/utils/calculations.js
- src/hooks/useFilteredData.js
- src/utils/dataFetcher.js
- README.md

**Accessibility Considerations:**
- Orange color must have sufficient contrast (WCAG AA)
- ARIA labels distinguish manual from PTV attendance
- Screen readers announce "Manual attendance" vs "PTV attendance"
- Keyboard navigation maintained for all interactions
- Focus trap and Escape key behavior preserved in modal

**Performance Considerations:**
- Environment variable loading is one-time at startup (minimal impact)
- Frontend already handles multiple date arrays efficiently
- Date validation adds minimal overhead
- No significant performance impact expected
