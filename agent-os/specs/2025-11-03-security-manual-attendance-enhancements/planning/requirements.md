# Spec Requirements: Security and Manual Attendance Enhancements

## Initial Description

Security and Manual Attendance Enhancements for Station Station

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

---

## Requirements Discussion

### First Round Questions

**Q1: Credential Security - Config key vs username**
I assume the config key (e.g., "koustubh") should be DIFFERENT from the actual Myki username for security purposes. So the relationship would be: config key "koustubh" -> environment variable MYKI_USERNAME_KOUSTUBH="koustubh25" where "koustubh25" is the actual PTV login username. Is that correct?

**Answer:** NO - Config key should be DIFFERENT from actual username. Example: config key = "koustubh", actual PTV username = "koustubh25". Relationship established via `MYKI_USERNAME_KOUSTUBH=koustubh25`. Security concern: actual username should NOT be exposed in config file.

**Q2: Username display field**
Should the optional `username` field in the config (for frontend display) default to the config key if not provided? For example, if the config key is "koustubh" but no `username` field exists, should the frontend display "koustubh"?

**Answer:** Optional with fallback to config key if not provided.

**Q3: Backward compatibility for existing configs**
Should we maintain backward compatibility with existing config files that have `mykiCardNumber` in them? I'm thinking we could detect if `mykiCardNumber` exists during load and issue a warning, then fall back to reading from environment variables.

**Answer:** NO backward compatibility. Do NOT want `mykiCardNumber` in config file at all. Security concern - must be removed completely.

**Q4: Load function extension**
Should we extend the existing `load_user_passwords()` function to also load usernames and card numbers from environment variables? This would make it a more general credential loader function.

**Answer:** YES - extend `load_user_passwords()` to also load username and card number. May want to rename function since it now loads more than just passwords.

**Q5: Manual attendance field naming**
I assume we should name the new field `manualAttendanceDates` to match the naming convention of `skipDates`. It should be optional and default to an empty array if not specified. Is that correct?

**Answer:** YES - name it `manualAttendanceDates`, optional, default to empty array.

**Q6: Manual vs PTV attendance in output**
Should manual attendance dates and PTV-detected attendance dates be kept SEPARATE in the output JSON (e.g., two different arrays) so the frontend can distinguish and potentially mark them differently, or should they be merged into a single attendance array?

**Answer:** Keep them SEPARATE in output JSON so they can be marked with different color in GUI.

**Q7: Display information for manual attendance**
What text or label should be shown in the AttendanceDetails modal when a user clicks on a manually recorded attendance date? Should it say "Manually recorded" or "No PTV data - manual entry"? Should it be marked with a different color/style in the calendar?

**Answer:** Show "Manually recorded" text. Mark with DIFFERENT color but use similar style (encircled date). Use different color than regular attendance.

**Q8: Conflict resolution**
If a date appears in BOTH `skipDates` AND `manualAttendanceDates`, which should take precedence? I'm assuming `manualAttendanceDates` should override `skipDates` since it's more specific user input.

**Answer:** `manualAttendanceDates` should take precedence over `skipDates`.

**Q9: Date validation**
Should we validate that dates in `manualAttendanceDates` are in YYYY-MM-DD format and fall within the user's startDate/endDate range? Should invalid dates be rejected with an error or just logged as warnings?

**Answer:** YES - validate dates are YYYY-MM-DD format and fall within startDate/endDate range.

**Q10: Documentation updates**
Should we update the `.env.example` file to include examples of the new environment variable structure (MYKI_USERNAME_*, MYKI_CARDNUMBER_*)? Should we add migration instructions to SETUP.md for existing users?

**Answer:** YES - update `.env.example` and `SETUP.md` with comprehensive migration instructions.

**Q11: Multi-user manual attendance**
In a multi-user setup, I assume each user should have their own `manualAttendanceDates` array in their user config section. Is that correct?

**Answer:** YES - each user should have their own `manualAttendanceDates` array.

**Q12: Scope exclusions**
Are there any features we should explicitly NOT implement? For example, should there be a UI for editing manual attendance dates, or is editing the config file directly acceptable?

**Answer:** NO UI for editing needed. UI should be READ-ONLY.

### Existing Code to Reference

No similar existing features identified for reference. This is an enhancement to the existing credential management and attendance tracking system.

### Follow-up Questions

None - all requirements clearly specified in first round.

---

## Visual Assets

### Files Provided:

No visual assets provided.

### Visual Insights:

Based on existing codebase analysis:
- Current implementation uses red circles (`ATTENDED_DAY_COLOR = '#ef4444'`) for PTV-detected attendance
- Manual attendance should use a DIFFERENT color with similar encircled style
- Suggested color: Orange (#fb923c) or amber (#f59e0b) to differentiate from regular attendance red
- AttendanceDetails modal should display different content for manual vs PTV attendance

---

## Requirements Summary

### Functional Requirements

**Credential Security:**
- Remove `mykiCardNumber` from config file completely (breaking change)
- Remove actual Myki username from config file (breaking change)
- Store actual credentials only in environment variables using mapping pattern:
  - `MYKI_USERNAME_<CONFIG_KEY>` = actual PTV username
  - `MYKI_CARDNUMBER_<CONFIG_KEY>` = actual card number
  - `MYKI_PASSWORD_<CONFIG_KEY>` = password (already exists)
- Config key serves as identifier but is NOT the actual username
- Optional `username` field in config for frontend display (fallback to config key if not provided)

**Manual Attendance Dates:**
- New optional field `manualAttendanceDates` in user config (array of YYYY-MM-DD strings)
- Defaults to empty array if not specified
- Each user has their own `manualAttendanceDates` array in multi-user setups
- Manual dates override `skipDates` if conflicts occur
- Manual dates are validated to be within user's startDate/endDate range
- Manual dates are validated for YYYY-MM-DD format

**Data Output Structure:**
- Keep manual attendance dates SEPARATE from PTV-detected attendance in output JSON
- Structure example:
  ```json
  {
    "attendanceDates": ["2025-01-15", "2025-01-16"],
    "manualAttendanceDates": ["2025-01-17"]
  }
  ```

**Frontend Visualization:**
- Manual attendance dates displayed with DIFFERENT color (suggest orange/amber)
- Use similar encircled style as regular attendance
- AttendanceDetails modal shows "Manually recorded" for manual dates
- No timestamp or station info shown for manual dates
- UI remains READ-ONLY (no editing interface)

**Calculations:**
- Manual attendance dates included in total attendance percentage
- Manual dates counted in "days attended" statistics
- Manual dates NOT counted in "days missed"

### Reusability Opportunities

**Existing patterns to leverage:**
- Extend existing `load_user_passwords()` function pattern to load all credentials
- Reuse existing environment variable loading mechanism
- Follow existing `skipDates` array pattern for `manualAttendanceDates`
- Reuse calendar encircled date styling (just different color)
- Extend existing AttendanceDetails modal with conditional content

### Scope Boundaries

**In Scope:**
- Backend (station-station repo):
  - Remove `mykiCardNumber` from config schema
  - Extend credential loading to include username and card number
  - Potentially rename `load_user_passwords()` to `load_user_credentials()`
  - Add `manualAttendanceDates` support in config
  - Validate manual dates (format and range)
  - Keep manual dates separate in output JSON
  - Implement conflict resolution (manual overrides skip)
  - Update `.env.example` with new variable examples
  - Update `SETUP.md` with migration guide

- Frontend (attendance-tracker repo):
  - Add new color constant for manual attendance (e.g., `MANUAL_ATTENDANCE_COLOR`)
  - Update CalendarView to render manual dates with different color
  - Update AttendanceDetails modal to handle manual dates
  - Update calculations to include manual dates
  - Update filtering logic to respect manual date overrides
  - No changes to user selector (username display already handled)

**Out of Scope:**
- UI interface for adding/editing manual attendance dates
- Validation UI for date conflicts
- Automatic detection of manual vs PTV attendance
- Bulk import/export of manual dates
- Historical migration scripts (users must manually update configs)
- Calendar editing functionality (remains read-only)

**Future Enhancements (mentioned but deferred):**
- Admin UI for managing manual attendance dates
- CSV import for bulk manual date entry
- Conflict detection warnings in UI

### Technical Considerations

**Breaking Changes:**
- Config file format change (removal of `mykiCardNumber` field)
- No backward compatibility for old config format
- Requires manual migration by all users
- All existing configs must be updated and secrets moved to `.env`

**Migration Strategy:**
- Document clear migration steps in `SETUP.md`
- Update `.env.example` with all required variables
- Provide example of old vs new config format
- Include checklist for migration:
  1. Extract `mykiCardNumber` values from config
  2. Add to `.env` as `MYKI_CARDNUMBER_<KEY>=value`
  3. Extract actual username if different from config key
  4. Add to `.env` as `MYKI_USERNAME_<KEY>=value`
  5. Remove `mykiCardNumber` from config
  6. Optionally add `username` field for display
  7. Test credential loading
  8. Verify attendance tracking still works

**Environment Variable Naming Convention:**
- Pattern: `MYKI_<CREDENTIAL_TYPE>_<CONFIG_KEY>`
- Examples:
  - `MYKI_USERNAME_KOUSTUBH=koustubh25`
  - `MYKI_CARDNUMBER_KOUSTUBH=12321`
  - `MYKI_PASSWORD_KOUSTUBH=secret123`
- Config key converted to UPPERCASE in environment variable names
- Maintains consistency with existing password pattern

**Frontend Color Scheme:**
- Regular attendance: Red (#ef4444) - already exists
- Manual attendance: Orange (#fb923c) or Amber (#f59e0b) - to be added
- Skip dates: No marking (gap in calendar)
- Both attendance types use encircled date style

**Data Validation:**
- Date format validation: YYYY-MM-DD regex pattern
- Date range validation: must be >= startDate and <= endDate (or current date)
- Conflict resolution: manual dates take precedence over skip dates
- Invalid dates should raise errors (not warnings) to prevent silent failures

**Backend Files to Modify (station-station repo):**
- `config_manager.py` - config loading and validation
- `credential_loader.py` or equivalent - extend to load username/cardnumber
- `output_manager.py` - separate manual dates in output JSON
- `myki_tracker.py` - conflict resolution logic
- `.env.example` - add new variable examples
- `SETUP.md` - migration instructions
- `README.md` - update documentation

**Frontend Files to Modify (attendance-tracker repo):**
- `src/constants/config.js` - add MANUAL_ATTENDANCE_COLOR constant
- `src/components/CalendarView.jsx` - render manual dates with different color
- `src/components/AttendanceDetails.jsx` - handle manual date display
- `src/utils/calculations.js` - include manual dates in calculations
- `src/hooks/useFilteredData.js` - handle manual date filtering
- `src/utils/dataFetcher.js` - validate new JSON structure
- `README.md` - update feature list

**Testing Considerations:**
- Test credential loading with new environment variables
- Test manual date validation (format and range)
- Test conflict resolution (manual vs skip dates)
- Test frontend rendering with separate manual dates array
- Test calculations include manual dates correctly
- Test migration path with sample old config

**Security Improvements:**
- Actual usernames no longer exposed in config file
- Card numbers no longer exposed in config file
- All sensitive credentials now in environment variables
- Config file can be safely committed to version control (if desired)
- Reduced attack surface for credential exposure

**Performance Considerations:**
- No significant performance impact expected
- Environment variable loading is one-time at startup
- Frontend already handles multiple date arrays efficiently
- Validation adds minimal overhead

**Accessibility Considerations:**
- Manual dates should have distinct ARIA labels
- Color difference alone not sufficient (use text labels)
- Screen readers should announce "Manual attendance" vs "PTV attendance"
- Maintain keyboard navigation for all date interactions

**Documentation Requirements:**
- Clear migration guide with examples
- Environment variable reference table
- Security rationale explanation
- Manual attendance use case documentation
- Troubleshooting section for common migration issues
- Screenshots of before/after config structure
