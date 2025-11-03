# Migration Guide: Security & Manual Attendance Enhancement

This guide helps you migrate from the old configuration format to the new secure format that moves credentials to environment variables and adds manual attendance tracking.

## Breaking Changes

### 1. Credential Storage (**CRITICAL - Action Required**)

**Old Format** (Config file with credentials - DEPRECATED):
```json
{
  "koustubh": {
    "mykiUsername": "koustubh25",
    "mykiCardNumber": "308425279093478",
    "targetStation": "Heathmont Station",
    "startDate": "2025-04-15"
  }
}
```

**New Format** (Credentials in environment variables):

**config/myki_config.json** (formerly `myki_tracker_config.json`):
```json
{
  "koustubh": {
    "targetStation": "Heathmont Station",
    "startDate": "2025-04-15"
  }
}
```

**.env** (New file required):
```bash
MYKI_USERNAME_KOUSTUBH=koustubh25
MYKI_CARDNUMBER_KOUSTUBH=308425279093478
MYKI_PASSWORD_KOUSTUBH=your_password_here
```

**Why this change?**
- Security: Credentials no longer stored in version-controlled config files
- .env file is gitignored and never committed
- Separation of configuration from secrets

### 2. Config Key vs Myki Username

The config key (e.g., "koustubh") is now **separate** from your actual Myki username. This provides additional security by not exposing your real username in config files.

**Example**:
- Config key: `"koustubh"` (in config file)
- Actual Myki username: `"koustubh25"` (in .env file only)

### 3. Manual Attendance Support (Optional Feature)

You can now track days when you drove to work instead of using public transport.

**Add to config** (optional):
```json
{
  "koustubh": {
    "targetStation": "Heathmont Station",
    "startDate": "2025-04-15",
    "manualAttendanceDates": ["2025-05-10", "2025-05-15"]
  }
}
```

**Features**:
- Manual dates displayed in orange/amber in calendar
- PTV-detected dates displayed in red
- Statistics include both manual and PTV attendance
- Manual dates override skip dates if conflicts exist

## Migration Steps

### Step 1: Create .env File

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Set file permissions (recommended):
   ```bash
   chmod 600 .env
   ```

3. Edit `.env` and add your credentials:
   ```bash
   # For each user in your config, add THREE environment variables:
   MYKI_USERNAME_{KEY}=your_actual_myki_username
   MYKI_CARDNUMBER_{KEY}=your_card_number
   MYKI_PASSWORD_{KEY}=your_password

   # Replace {KEY} with your config key in UPPERCASE
   # Example for config key "koustubh":
   MYKI_USERNAME_KOUSTUBH=koustubh25
   MYKI_CARDNUMBER_KOUSTUBH=308425279093478
   MYKI_PASSWORD_KOUSTUBH=your_password_here
   ```

**Important Notes**:
- Use **UPPERCASE** for the config key in environment variable names
- Replace underscores, dots, and hyphens in config keys with underscores
  - Config key `"john.doe"` → `MYKI_USERNAME_JOHN_DOE`
  - Config key `"jane-smith"` → `MYKI_USERNAME_JANE_SMITH`

### Step 2: Update Config File

1. Open `config/myki_config.json` (formerly `myki_tracker_config.json`)

2. Remove credential fields (if present):
   - Remove `"mykiUsername"` field
   - Remove `"mykiCardNumber"` field

3. Keep only these fields:
   - `"targetStation"` (required)
   - `"startDate"` (required)
   - `"endDate"` (optional)
   - `"skipDates"` (optional)
   - `"manualAttendanceDates"` (optional - new feature)
   - `"username"` (optional - display name for frontend)

**Example cleaned config**:
```json
{
  "koustubh": {
    "username": "Koustubh Gaikwad",
    "targetStation": "Heathmont Station",
    "startDate": "2025-04-15",
    "endDate": "2025-12-31",
    "skipDates": ["2025-05-01", "2025-05-02"],
    "manualAttendanceDates": ["2025-05-10"]
  }
}
```

### Step 3: Verify Migration

Run configuration validation:
```bash
python3 -m pytest tests/test_credential_security.py -v
```

All tests should pass. If you see errors about missing environment variables, check that:
1. `.env` file exists in project root
2. Environment variable names match the pattern `MYKI_USERNAME_{KEY}` exactly
3. Config key is converted to UPPERCASE in environment variable names

### Step 4: Test the Application

Run the tracker:
```bash
./docker-run.sh
```

Or for local testing:
```bash
python3 src/run_myki_workflow.py
```

Check the output for:
- ✓ Credentials loaded successfully
- ✓ No warnings about missing environment variables
- ✓ Attendance data processed correctly

## Troubleshooting

### Error: "Missing required environment variables"

**Problem**: Environment variables not found.

**Solution**:
1. Verify `.env` file exists in project root directory
2. Check variable names use UPPERCASE for config key
3. Ensure no typos in environment variable names
4. For Docker: Restart containers after modifying .env

### Error: "Field 'mykiCardNumber' is not allowed in config"

**Problem**: Old credential format still in config file.

**Solution**:
Remove `"mykiCardNumber"` and `"mykiUsername"` fields from config file. Move these values to `.env` file instead.

### Manual Attendance Dates Not Showing

**Problem**: Manual dates not appearing in calendar or statistics.

**Solution**:
1. Verify date format is `"YYYY-MM-DD"` (ISO format)
2. Check dates are within `startDate` to `endDate` range
3. Ensure `manualAttendanceDates` is an array: `["2025-05-10"]` not `"2025-05-10"`
4. Regenerate output JSON: `python3 src/run_myki_workflow.py`

### Config Key Naming Rules

When choosing config keys:
- ✅ Use lowercase: `"koustubh"`, `"john"`
- ✅ Use underscores for spaces: `"john_doe"`
- ❌ Avoid special characters except underscore and dot
- ❌ Don't use uppercase (case-insensitive when converted to env vars)

Environment variable conversion:
- `"koustubh"` → `MYKI_USERNAME_KOUSTUBH`
- `"john.doe"` → `MYKI_USERNAME_JOHN_DOE`
- `"jane_smith"` → `MYKI_USERNAME_JANE_SMITH`

## JSON Output Changes

The JSON output structure now includes manual attendance:

**New field**:
```json
{
  "koustubh": {
    "attendanceDays": ["2025-05-12", "2025-05-13"],
    "manualAttendanceDates": ["2025-05-10", "2025-05-15"],
    "statistics": {
      "daysAttended": 4
    }
  }
}
```

**Changes**:
- `manualAttendanceDates`: Array of manually recorded attendance dates (new)
- `attendanceDays`: Only contains PTV-detected attendance (unchanged)
- `statistics.daysAttended`: Now includes both PTV + manual attendance

## Frontend Changes

The web frontend now displays:
- **Red circles**: PTV-detected attendance days
- **Orange/amber circles**: Manual attendance days
- **Modal labels**: "PTV Attendance" vs "Manual Attendance"
- **No timestamp**: Manual attendance entries don't show time (since you drove)

## Rollback Instructions

If you need to rollback (not recommended for security):

1. **Keep your .env file** (for future use)
2. Temporarily add credentials back to config:
   ```json
   {
     "koustubh": {
       "mykiUsername": "koustubh25",
       "mykiCardNumber": "308425279093478",
       "targetStation": "Heathmont Station",
       "startDate": "2025-04-15"
     }
   }
   ```
3. This will only work with old code - **the new version doesn't support this format**

## Security Best Practices

After migration:

1. ✓ Verify `.env` is in `.gitignore`
2. ✓ Never commit `.env` to version control
3. ✓ Use `chmod 600 .env` to restrict file permissions
4. ✓ Use strong, unique passwords
5. ✓ Rotate passwords periodically
6. ✓ Don't share your `.env` file

## Need Help?

- Review `.env.example` for correct format
- Check test files in `tests/` for working examples
- See config examples in `config/myki_tracker_config.example.json`
- Open an issue on GitHub for additional support
