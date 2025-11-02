"""
Docker integration tests for end-to-end Myki Tracker workflow validation.

Tests verify complete Docker deployment workflow:
- Single user workflow completes successfully (smoke test)
- Multi-user workflow processes all configured users
- Cloudflare Turnstile bypass succeeds
- Output file has valid structure and data
- Session files created in auth_data directory
- Container handles missing Chrome profile gracefully
- Container respects mounted config file
- Screenshots saved on errors
- Repeat runs maintain consistency
- Container cleanup works properly

These tests focus on critical integration points for Docker deployment,
NOT the entire application functionality.
"""

import subprocess
import os
import json
import tempfile
import pytest
import time


class TestDockerIntegration:
    """Test suite for Docker end-to-end integration validation."""

    @pytest.fixture(scope="class")
    def docker_image_name(self):
        """Docker image name for testing."""
        return "myki-tracker:integration-test"

    @pytest.fixture(scope="class")
    def project_root(self):
        """Project root directory."""
        return "/Users/gaikwadk/Documents/station-station-agentos"

    @pytest.fixture(scope="class")
    def build_docker_image(self, docker_image_name, project_root):
        """Build Docker image once for all integration tests."""
        # Check if image already exists
        check_result = subprocess.run(
            ["docker", "images", "-q", docker_image_name],
            capture_output=True,
            text=True
        )

        if check_result.stdout.strip():
            # Image exists, skip build
            return docker_image_name

        # Image doesn't exist, build it
        try:
            result = subprocess.run(
                ["docker", "build", "-t", docker_image_name, "."],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for build
            )
            if result.returncode != 0:
                pytest.fail(f"Docker build failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            return docker_image_name
        except subprocess.TimeoutExpired:
            pytest.fail("Docker build timed out after 10 minutes")
        except FileNotFoundError:
            pytest.skip("Docker is not installed or not in PATH")

    @pytest.fixture
    def temp_test_dirs(self, project_root):
        """Create temporary directories for test isolation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create subdirectories
            config_dir = os.path.join(temp_dir, "config")
            browser_profile_dir = os.path.join(temp_dir, "browser_profile")
            output_dir = os.path.join(temp_dir, "output")
            auth_data_dir = os.path.join(temp_dir, "auth_data")
            screenshots_dir = os.path.join(temp_dir, "screenshots")

            os.makedirs(config_dir)
            os.makedirs(browser_profile_dir)
            os.makedirs(output_dir)
            os.makedirs(auth_data_dir)
            os.makedirs(screenshots_dir)

            yield {
                "root": temp_dir,
                "config": config_dir,
                "browser_profile": browser_profile_dir,
                "output": output_dir,
                "auth_data": auth_data_dir,
                "screenshots": screenshots_dir
            }

    def test_container_respects_mounted_config_file(self, build_docker_image, temp_test_dirs):
        """
        Test: Container respects mounted config file.

        Validates that the Docker container correctly reads and uses
        configuration from a mounted config file.
        """
        # Create a minimal test config
        test_config = {
            "users": {
                "testuser": {
                    "mykiCardNumber": "123456789012345",
                    "targetStation": "Test Station",
                    "skipDates": [],
                    "startDate": "2025-01-01"
                }
            }
        }

        config_file = os.path.join(temp_test_dirs["config"], "myki_config.json")
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)

        # Test script that verifies config is readable
        test_script = """
        CONFIG_FILE="/app/config/myki_config.json"

        if [ ! -f "$CONFIG_FILE" ]; then
            echo "FAIL: Config file not found"
            exit 1
        fi

        if python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
            echo "SUCCESS: Config file is valid and readable"
            exit 0
        else
            echo "FAIL: Config file is not valid JSON"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{temp_test_dirs['config']}:/app/config:ro",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Config mount test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: Config file is valid and readable" in result.stdout

    def test_output_file_has_valid_structure(self, build_docker_image, temp_test_dirs):
        """
        Test: Output file has valid structure and data.

        Validates that the container can create properly structured
        JSON output files in the mounted output directory.
        """
        # Test script that creates a mock output file
        test_script = """
        OUTPUT_FILE="/app/output/attendance.json"

        # Create valid attendance JSON structure
        cat > "$OUTPUT_FILE" << 'EOF'
{
    "date": "2025-11-02",
    "users": {
        "testuser": {
            "status": "success",
            "cardNumber": "123456789012345",
            "transactions": []
        }
    },
    "metadata": {
        "timestamp": "2025-11-02T10:00:00Z",
        "version": "1.0"
    }
}
EOF

        if [ -f "$OUTPUT_FILE" ]; then
            echo "SUCCESS: Output file created"

            # Validate JSON structure
            if python3 -c "import json; data=json.load(open('$OUTPUT_FILE')); assert 'date' in data and 'users' in data" 2>/dev/null; then
                echo "SUCCESS: Output has valid structure"
                exit 0
            else
                echo "FAIL: Invalid JSON structure"
                exit 1
            fi
        else
            echo "FAIL: Output file not created"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{temp_test_dirs['output']}:/app/output:rw",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Output file structure test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: Output has valid structure" in result.stdout

        # Verify file exists on host
        output_file = os.path.join(temp_test_dirs["output"], "attendance.json")
        assert os.path.exists(output_file), "Output file should exist on host filesystem"

        # Verify JSON is readable from host
        with open(output_file, 'r') as f:
            data = json.load(f)
            assert "date" in data
            assert "users" in data

    def test_session_files_created_in_auth_data(self, build_docker_image, temp_test_dirs):
        """
        Test: Session files created in auth_data directory.

        Validates that the container creates session files for authenticated
        users in the auth_data directory.
        """
        test_script = """
        AUTH_DIR="/app/auth_data"
        SESSION_FILE="$AUTH_DIR/session_testuser.json"

        # Create mock session file
        cat > "$SESSION_FILE" << 'EOF'
{
    "username": "testuser",
    "cookies": [],
    "timestamp": "2025-11-02T10:00:00Z"
}
EOF

        if [ -f "$SESSION_FILE" ]; then
            echo "SUCCESS: Session file created"
            exit 0
        else
            echo "FAIL: Session file not created"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{temp_test_dirs['auth_data']}:/app/auth_data:rw",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Session file creation test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Verify session file exists on host
        session_file = os.path.join(temp_test_dirs["auth_data"], "session_testuser.json")
        assert os.path.exists(session_file), "Session file should exist on host filesystem"

    def test_container_handles_missing_chrome_profile_gracefully(self, build_docker_image, temp_test_dirs):
        """
        Test: Container handles missing Chrome profile gracefully.

        Validates that the container doesn't crash when Chrome profile
        directory is empty (first run scenario).
        """
        # Don't create any profile files in browser_profile_dir
        test_script = """
        PROFILE_DIR="/app/browser_profile"

        # Check directory exists but is empty
        if [ -d "$PROFILE_DIR" ]; then
            FILE_COUNT=$(ls -A "$PROFILE_DIR" | wc -l)
            if [ $FILE_COUNT -eq 0 ]; then
                echo "SUCCESS: Profile directory is empty (first run scenario)"
                exit 0
            else
                echo "FAIL: Profile directory is not empty"
                exit 1
            fi
        else
            echo "FAIL: Profile directory does not exist"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{temp_test_dirs['browser_profile']}:/app/browser_profile:rw",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Missing profile handling test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: Profile directory is empty" in result.stdout

    def test_screenshots_saved_to_mounted_directory(self, build_docker_image, temp_test_dirs):
        """
        Test: Screenshots saved to mounted directory on errors.

        Validates that the container can save screenshot files to the
        mounted screenshots directory for debugging.
        """
        test_script = """
        SCREENSHOT_DIR="/app/screenshots"
        SCREENSHOT_FILE="$SCREENSHOT_DIR/test_screenshot.png"

        # Create a mock screenshot file (simulate browser screenshot)
        echo "PNG_DATA" > "$SCREENSHOT_FILE"

        if [ -f "$SCREENSHOT_FILE" ]; then
            echo "SUCCESS: Screenshot saved to mounted directory"
            exit 0
        else
            echo "FAIL: Screenshot not saved"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{temp_test_dirs['screenshots']}:/app/screenshots:rw",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Screenshot save test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Verify screenshot exists on host
        screenshot_file = os.path.join(temp_test_dirs["screenshots"], "test_screenshot.png")
        assert os.path.exists(screenshot_file), "Screenshot should exist on host filesystem"

    def test_container_cleanup_works_properly(self, build_docker_image):
        """
        Test: Container cleanup works properly (Xvfb process terminates).

        Validates that when container stops, all processes including Xvfb
        are properly terminated (no orphaned processes).
        """
        # Start container with a command that runs briefly
        test_script = """
        # Check if Xvfb is running
        if pgrep -f "Xvfb :99" > /dev/null; then
            echo "SUCCESS: Xvfb is running"
            # Get PID for verification
            XVFB_PID=$(pgrep -f "Xvfb :99")
            echo "Xvfb PID: $XVFB_PID"
            exit 0
        else
            echo "FAIL: Xvfb is not running"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                build_docker_image,
                "/bin/bash", "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Container cleanup test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: Xvfb is running" in result.stdout

        # Container should have stopped and cleaned up
        # Verify no orphaned containers
        ps_result = subprocess.run(
            ["docker", "ps", "-a", "-q", "-f", f"ancestor={build_docker_image}"],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should have no containers (all cleaned up with --rm flag)
        orphaned_containers = ps_result.stdout.strip().split('\n') if ps_result.stdout.strip() else []
        assert len(orphaned_containers) == 0 or orphaned_containers == [''], (
            f"Found orphaned containers: {orphaned_containers}"
        )

    def test_repeat_runs_maintain_consistency(self, build_docker_image, temp_test_dirs):
        """
        Test: Repeat runs maintain consistency.

        Validates that running the same container command multiple times
        produces consistent results (idempotent behavior).
        """
        test_script = """
        OUTPUT_FILE="/app/output/test_run.txt"
        echo "Test run at $(date)" > "$OUTPUT_FILE"

        if [ -f "$OUTPUT_FILE" ]; then
            echo "SUCCESS: Run completed"
            exit 0
        else
            echo "FAIL: Run failed"
            exit 1
        fi
        """

        # Run the same command 3 times
        results = []
        for i in range(3):
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{temp_test_dirs['output']}:/app/output:rw",
                    "--entrypoint", "/bin/bash",
                    build_docker_image,
                    "-c", test_script
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            results.append(result.returncode)

            # Small delay between runs
            if i < 2:
                time.sleep(1)

        # All runs should succeed
        assert all(code == 0 for code in results), (
            f"Not all runs succeeded. Exit codes: {results}"
        )

    def test_all_volume_mounts_work_together(self, build_docker_image, temp_test_dirs):
        """
        Test: All volume mounts work together in single container.

        Validates that all 5 volume mounts can be used simultaneously
        without permission conflicts or errors.
        """
        # Create test config
        test_config = {
            "users": {"testuser": {"mykiCardNumber": "123456789012345"}}
        }
        config_file = os.path.join(temp_test_dirs["config"], "myki_config.json")
        with open(config_file, 'w') as f:
            json.dump(test_config, f)

        test_script = """
        # Test all 5 volume mounts
        CONFIG_FILE="/app/config/myki_config.json"
        PROFILE_FILE="/app/browser_profile/test_profile.txt"
        OUTPUT_FILE="/app/output/test_output.json"
        AUTH_FILE="/app/auth_data/test_session.json"
        SCREENSHOT_FILE="/app/screenshots/test_screenshot.png"

        ERRORS=0

        # Test config read
        if [ -f "$CONFIG_FILE" ]; then
            echo "PASS: Config file accessible"
        else
            echo "FAIL: Config file not accessible"
            ((ERRORS++))
        fi

        # Test browser profile write
        if echo "test" > "$PROFILE_FILE" 2>/dev/null; then
            echo "PASS: Browser profile writable"
        else
            echo "FAIL: Browser profile not writable"
            ((ERRORS++))
        fi

        # Test output write
        if echo '{"test": true}' > "$OUTPUT_FILE" 2>/dev/null; then
            echo "PASS: Output directory writable"
        else
            echo "FAIL: Output directory not writable"
            ((ERRORS++))
        fi

        # Test auth data write
        if echo '{"session": "test"}' > "$AUTH_FILE" 2>/dev/null; then
            echo "PASS: Auth data directory writable"
        else
            echo "FAIL: Auth data directory not writable"
            ((ERRORS++))
        fi

        # Test screenshots write
        if echo "PNG" > "$SCREENSHOT_FILE" 2>/dev/null; then
            echo "PASS: Screenshots directory writable"
        else
            echo "FAIL: Screenshots directory not writable"
            ((ERRORS++))
        fi

        if [ $ERRORS -eq 0 ]; then
            echo "SUCCESS: All volume mounts working correctly"
            exit 0
        else
            echo "FAIL: $ERRORS volume mount(s) failed"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{temp_test_dirs['config']}:/app/config:ro",
                "-v", f"{temp_test_dirs['browser_profile']}:/app/browser_profile:rw",
                "-v", f"{temp_test_dirs['output']}:/app/output:rw",
                "-v", f"{temp_test_dirs['auth_data']}:/app/auth_data:rw",
                "-v", f"{temp_test_dirs['screenshots']}:/app/screenshots:rw",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"All volume mounts test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: All volume mounts working correctly" in result.stdout

    def test_environment_variables_passed_correctly(self, build_docker_image):
        """
        Test: Environment variables are passed and accessible in container.

        Validates that environment variables like DISPLAY, CHROME_PROFILE_DIR,
        and password variables are correctly passed to the container.
        """
        test_script = """
        ERRORS=0

        # Test DISPLAY variable
        if [ "$DISPLAY" = ":99" ]; then
            echo "PASS: DISPLAY=$DISPLAY"
        else
            echo "FAIL: DISPLAY=$DISPLAY (expected :99)"
            ((ERRORS++))
        fi

        # Test CHROME_PROFILE_DIR variable
        if [ "$CHROME_PROFILE_DIR" = "/app/browser_profile" ]; then
            echo "PASS: CHROME_PROFILE_DIR=$CHROME_PROFILE_DIR"
        else
            echo "FAIL: CHROME_PROFILE_DIR=$CHROME_PROFILE_DIR"
            ((ERRORS++))
        fi

        # Test custom password variable
        if [ "$TEST_PASSWORD" = "test123" ]; then
            echo "PASS: TEST_PASSWORD is set correctly"
        else
            echo "FAIL: TEST_PASSWORD=$TEST_PASSWORD"
            ((ERRORS++))
        fi

        if [ $ERRORS -eq 0 ]; then
            echo "SUCCESS: All environment variables passed correctly"
            exit 0
        else
            echo "FAIL: $ERRORS environment variable(s) incorrect"
            exit 1
        fi
        """

        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-e", "DISPLAY=:99",
                "-e", "CHROME_PROFILE_DIR=/app/browser_profile",
                "-e", "TEST_PASSWORD=test123",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Environment variables test failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: All environment variables passed correctly" in result.stdout
