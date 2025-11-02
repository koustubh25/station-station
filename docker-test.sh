#!/bin/bash
# Docker test script for Myki Transaction Tracker
# Purpose: Run container and validate output automatically
# Output: PASS/FAIL validation summary with exit code

set -e  # Exit on any error

# Logging function for structured output
log() {
    echo "[TEST] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

log_error() {
    echo "[TEST ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2
}

log_success() {
    echo "[TEST SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

# Banner
log "=================================="
log "Myki Tracker Docker Validation Test"
log "=================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configuration
OUTPUT_FILE="$SCRIPT_DIR/output/attendance.json"
AUTH_DATA_DIR="$SCRIPT_DIR/auth_data"
RUN_SCRIPT="$SCRIPT_DIR/docker-run.sh"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
VALIDATION_ERRORS=()

# Cleanup old output files before test
log "Cleaning up old output files..."
rm -f "$OUTPUT_FILE"
rm -f "$AUTH_DATA_DIR"/session_*.json

# Step 1: Run the container
log "Step 1: Running Docker container via docker-run.sh"
log "Executing: $RUN_SCRIPT"

if [ ! -f "$RUN_SCRIPT" ]; then
    log_error "docker-run.sh not found at $RUN_SCRIPT"
    exit 1
fi

# Run container and capture exit code
set +e  # Temporarily disable exit on error to capture exit code
"$RUN_SCRIPT"
CONTAINER_EXIT_CODE=$?
set -e  # Re-enable exit on error

log "Container exit code: $CONTAINER_EXIT_CODE"

# Step 2: Check container exit code
log "Step 2: Validating container exit code"

if [ $CONTAINER_EXIT_CODE -eq 0 ]; then
    log_success "PASS: Container exit code is 0 (success)"
    ((TESTS_PASSED++))
else
    log_error "FAIL: Container exit code is $CONTAINER_EXIT_CODE (expected 0)"
    VALIDATION_ERRORS+=("Container exit code: $CONTAINER_EXIT_CODE (expected 0)")
    ((TESTS_FAILED++))
fi

# Step 3: Check output file exists
log "Step 3: Checking output file exists"

if [ -f "$OUTPUT_FILE" ]; then
    log_success "PASS: Output file exists at $OUTPUT_FILE"
    ((TESTS_PASSED++))
else
    log_error "FAIL: Output file not found at $OUTPUT_FILE"
    VALIDATION_ERRORS+=("Output file not found: $OUTPUT_FILE")
    ((TESTS_FAILED++))
fi

# Step 4: Validate JSON structure
log "Step 4: Validating JSON structure of output file"

if [ -f "$OUTPUT_FILE" ]; then
    # Check if jq is available for JSON validation
    if command -v jq &> /dev/null; then
        if jq empty "$OUTPUT_FILE" 2>/dev/null; then
            log_success "PASS: Output file is valid JSON"
            ((TESTS_PASSED++))

            # Check for expected fields
            if jq -e '.date' "$OUTPUT_FILE" > /dev/null 2>&1; then
                log_success "PASS: Output file contains 'date' field"
                ((TESTS_PASSED++))
            else
                log_error "FAIL: Output file missing 'date' field"
                VALIDATION_ERRORS+=("Output file missing 'date' field")
                ((TESTS_FAILED++))
            fi

            if jq -e '.users' "$OUTPUT_FILE" > /dev/null 2>&1; then
                log_success "PASS: Output file contains 'users' field"
                ((TESTS_PASSED++))
            else
                log_error "FAIL: Output file missing 'users' field"
                VALIDATION_ERRORS+=("Output file missing 'users' field")
                ((TESTS_FAILED++))
            fi
        else
            log_error "FAIL: Output file is not valid JSON"
            VALIDATION_ERRORS+=("Output file is not valid JSON")
            ((TESTS_FAILED++))
        fi
    else
        # Fallback to Python for JSON validation if jq not available
        log "jq not available, using Python for JSON validation"
        if python3 -c "import json; json.load(open('$OUTPUT_FILE'))" 2>/dev/null; then
            log_success "PASS: Output file is valid JSON (validated with Python)"
            ((TESTS_PASSED++))

            # Check for expected fields using Python
            if python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); assert 'date' in data" 2>/dev/null; then
                log_success "PASS: Output file contains 'date' field"
                ((TESTS_PASSED++))
            else
                log_error "FAIL: Output file missing 'date' field"
                VALIDATION_ERRORS+=("Output file missing 'date' field")
                ((TESTS_FAILED++))
            fi

            if python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); assert 'users' in data" 2>/dev/null; then
                log_success "PASS: Output file contains 'users' field"
                ((TESTS_PASSED++))
            else
                log_error "FAIL: Output file missing 'users' field"
                VALIDATION_ERRORS+=("Output file missing 'users' field")
                ((TESTS_FAILED++))
            fi
        else
            log_error "FAIL: Output file is not valid JSON"
            VALIDATION_ERRORS+=("Output file is not valid JSON")
            ((TESTS_FAILED++))
        fi
    fi
else
    log "SKIP: JSON validation skipped (output file does not exist)"
fi

# Step 5: Check for session files
log "Step 5: Checking for session files in auth_data directory"

SESSION_FILES=("$AUTH_DATA_DIR"/session_*.json)
if [ -e "${SESSION_FILES[0]}" ]; then
    SESSION_COUNT=$(ls -1 "$AUTH_DATA_DIR"/session_*.json 2>/dev/null | wc -l)
    log_success "PASS: Found $SESSION_COUNT session file(s) in $AUTH_DATA_DIR"
    ((TESTS_PASSED++))

    # List session files
    for SESSION_FILE in "$AUTH_DATA_DIR"/session_*.json; do
        if [ -f "$SESSION_FILE" ]; then
            log "  - $(basename "$SESSION_FILE")"
        fi
    done
else
    log_error "FAIL: No session files found in $AUTH_DATA_DIR"
    VALIDATION_ERRORS+=("No session files found in $AUTH_DATA_DIR")
    ((TESTS_FAILED++))
fi

# Step 6: Display validation summary
log ""
log "=================================="
log "Validation Summary"
log "=================================="
log "Tests Passed: $TESTS_PASSED"
log "Tests Failed: $TESTS_FAILED"
log ""

if [ $TESTS_FAILED -eq 0 ]; then
    log_success "VALIDATION RESULT: PASS"
    log_success "All validation checks passed successfully!"
    log ""
    log "Output file: $OUTPUT_FILE"
    log "Session files: $AUTH_DATA_DIR/session_*.json"
    exit 0
else
    log_error "VALIDATION RESULT: FAIL"
    log_error "Some validation checks failed:"
    log ""
    for ERROR in "${VALIDATION_ERRORS[@]}"; do
        log_error "  - $ERROR"
    done
    log ""
    log_error "Please check container logs and output files for details"
    exit 1
fi
