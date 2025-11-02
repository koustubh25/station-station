#!/bin/bash
# Docker health check validation script for Myki Transaction Tracker
# Purpose: Validate container output, session data, and completion status
# Returns: 0 if all checks pass, 1 if any fail

# Note: Not using 'set -e' because we want to continue checking all validation steps
# even if some fail. The script will exit with code 1 at the end if any checks failed.

# Logging functions
log() {
    echo "[HEALTH CHECK] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[HEALTH CHECK ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_success() {
    echo "[HEALTH CHECK SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

# Banner
log "=========================================="
log "Myki Tracker Docker Health Check"
log "=========================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configuration
OUTPUT_FILE="${OUTPUT_FILE:-$SCRIPT_DIR/output/attendance.json}"
AUTH_DATA_DIR="${AUTH_DATA_DIR:-$SCRIPT_DIR/auth_data}"
CONFIG_FILE="${CONFIG_FILE:-$SCRIPT_DIR/config/myki_config.json}"
CONTAINER_NAME="${CONTAINER_NAME:-myki-tracker-run}"

# Health check results
CHECKS_PASSED=0
CHECKS_FAILED=0
HEALTH_ERRORS=()

# Check 1: Container exit code is 0
log "Check 1: Verifying container exit code"

# Get the last container's exit code if it exists
CONTAINER_EXIT_CODE=$(docker inspect "$CONTAINER_NAME" --format='{{.State.ExitCode}}' 2>/dev/null || echo "N/A")
# Trim whitespace/newlines
CONTAINER_EXIT_CODE=$(echo "$CONTAINER_EXIT_CODE" | tr -d '\n\r' | xargs)

if [ "$CONTAINER_EXIT_CODE" = "N/A" ]; then
    log "INFO: Container not found or already removed (--rm flag used)"
    log "INFO: Skipping container exit code check (will validate via output file instead)"
elif [ "$CONTAINER_EXIT_CODE" = "0" ]; then
    log_success "PASS: Container exit code is 0 (success)"
    ((CHECKS_PASSED++))
else
    log_error "FAIL: Container exit code is $CONTAINER_EXIT_CODE (expected 0)"
    HEALTH_ERRORS+=("Container exit code: $CONTAINER_EXIT_CODE (expected 0)")
    ((CHECKS_FAILED++))
fi

# Check 2: output/attendance.json exists and is valid JSON
log "Check 2: Verifying output/attendance.json exists and is valid JSON"

if [ -f "$OUTPUT_FILE" ]; then
    log_success "PASS: Output file exists at $OUTPUT_FILE"
    ((CHECKS_PASSED++))

    # Validate JSON structure
    if command -v jq &> /dev/null; then
        if jq empty "$OUTPUT_FILE" 2>/dev/null; then
            log_success "PASS: Output file is valid JSON (verified with jq)"
            ((CHECKS_PASSED++))
        else
            log_error "FAIL: Output file is not valid JSON"
            HEALTH_ERRORS+=("Output file is not valid JSON")
            ((CHECKS_FAILED++))
        fi
    else
        # Fallback to Python for JSON validation
        if python3 -c "import json; json.load(open('$OUTPUT_FILE'))" 2>/dev/null; then
            log_success "PASS: Output file is valid JSON (verified with Python)"
            ((CHECKS_PASSED++))
        else
            log_error "FAIL: Output file is not valid JSON"
            HEALTH_ERRORS+=("Output file is not valid JSON")
            ((CHECKS_FAILED++))
        fi
    fi
else
    log_error "FAIL: Output file not found at $OUTPUT_FILE"
    HEALTH_ERRORS+=("Output file not found: $OUTPUT_FILE")
    ((CHECKS_FAILED++))
fi

# Check 3: auth_data/session_*.json files exist for each configured user
log "Check 3: Verifying session files exist for configured users"

# Get configured users from config file
if [ -f "$CONFIG_FILE" ]; then
    # Extract usernames from config
    if command -v jq &> /dev/null; then
        CONFIGURED_USERS=$(jq -r '.users | keys[]' "$CONFIG_FILE" 2>/dev/null || echo "")
    else
        # Fallback to Python
        CONFIGURED_USERS=$(python3 -c "import json; data=json.load(open('$CONFIG_FILE')); print('\n'.join(data.get('users', {}).keys()))" 2>/dev/null || echo "")
    fi

    if [ -n "$CONFIGURED_USERS" ]; then
        USER_COUNT=$(echo "$CONFIGURED_USERS" | wc -l)
        log "Found $USER_COUNT configured user(s) in config file"

        # Check for session files
        SESSION_FILES_FOUND=0
        for username in $CONFIGURED_USERS; do
            SESSION_FILE="$AUTH_DATA_DIR/session_${username}.json"
            if [ -f "$SESSION_FILE" ]; then
                log "  - Session file found for user: $username"
                ((SESSION_FILES_FOUND++))
            else
                log "  - Session file NOT found for user: $username"
            fi
        done

        if [ $SESSION_FILES_FOUND -eq $USER_COUNT ]; then
            log_success "PASS: Session files found for all $USER_COUNT configured user(s)"
            ((CHECKS_PASSED++))
        else
            log_error "FAIL: Session files found for $SESSION_FILES_FOUND/$USER_COUNT users"
            HEALTH_ERRORS+=("Missing session files for $(($USER_COUNT - $SESSION_FILES_FOUND)) user(s)")
            ((CHECKS_FAILED++))
        fi
    else
        log_error "FAIL: No users configured in config file"
        HEALTH_ERRORS+=("No users found in config file")
        ((CHECKS_FAILED++))
    fi
else
    log_error "FAIL: Config file not found at $CONFIG_FILE"
    HEALTH_ERRORS+=("Config file not found: $CONFIG_FILE")
    ((CHECKS_FAILED++))
fi

# Check 4: attendance.json contains expected fields (metadata, user data)
log "Check 4: Verifying attendance.json contains expected fields"

if [ -f "$OUTPUT_FILE" ]; then
    FIELDS_VALID=true

    # Check for 'metadata' field
    if command -v jq &> /dev/null; then
        if jq -e '.metadata' "$OUTPUT_FILE" > /dev/null 2>&1; then
            log "  - Field 'metadata' found"
        else
            log_error "  - Field 'metadata' NOT found"
            FIELDS_VALID=false
        fi

        # Check that file has at least one user key (any key except 'metadata')
        USER_COUNT=$(jq 'keys | map(select(. != "metadata")) | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        if [ "$USER_COUNT" -gt 0 ]; then
            log "  - Found $USER_COUNT user(s) in output file"
        else
            log_error "  - No user data found in output file"
            FIELDS_VALID=false
        fi
    else
        # Fallback to Python
        if python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); assert 'metadata' in data" 2>/dev/null; then
            log "  - Field 'metadata' found"
        else
            log_error "  - Field 'metadata' NOT found"
            FIELDS_VALID=false
        fi

        USER_COUNT=$(python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); print(len([k for k in data.keys() if k != 'metadata']))" 2>/dev/null || echo "0")
        if [ "$USER_COUNT" -gt 0 ]; then
            log "  - Found $USER_COUNT user(s) in output file"
        else
            log_error "  - No user data found in output file"
            FIELDS_VALID=false
        fi
    fi

    if [ "$FIELDS_VALID" = true ]; then
        log_success "PASS: Output file contains expected fields (metadata, user data)"
        ((CHECKS_PASSED++))
    else
        log_error "FAIL: Output file missing required fields"
        HEALTH_ERRORS+=("Output file missing required fields (metadata, user data)")
        ((CHECKS_FAILED++))
    fi
else
    log "SKIP: Output file validation skipped (file does not exist)"
fi

# Check 5: Success message appears in logs
log "Check 5: Checking for success message in container logs"

# Try to get logs from the container
if docker logs "$CONTAINER_NAME" > /dev/null 2>&1; then
    CONTAINER_LOGS=$(docker logs "$CONTAINER_NAME" 2>&1)

    # Look for success message
    if echo "$CONTAINER_LOGS" | grep -q "COMPLETED SUCCESSFULLY"; then
        log_success "PASS: Success message found in container logs"
        ((CHECKS_PASSED++))
    else
        log_error "FAIL: Success message not found in container logs"
        HEALTH_ERRORS+=("Container logs do not contain success message")
        ((CHECKS_FAILED++))
    fi
else
    log "INFO: Container not found or logs not available (container may have been removed)"
    log "INFO: Skipping log check"
fi

# Display health check summary
log ""
log "=========================================="
log "Health Check Summary"
log "=========================================="
log "Checks Passed: $CHECKS_PASSED"
log "Checks Failed: $CHECKS_FAILED"
log ""

if [ $CHECKS_FAILED -eq 0 ]; then
    log_success "HEALTH CHECK RESULT: PASS"
    log_success "All health checks passed successfully!"
    log ""
    log "Output file: $OUTPUT_FILE"
    log "Session files: $AUTH_DATA_DIR/session_*.json"
    exit 0
else
    log_error "HEALTH CHECK RESULT: FAIL"
    log_error "Some health checks failed:"
    log ""
    for ERROR in "${HEALTH_ERRORS[@]}"; do
        log_error "  - $ERROR"
    done
    log ""
    log_error "Please review the errors above and check container logs for details"
    exit 1
fi
