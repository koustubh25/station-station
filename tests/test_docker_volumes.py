"""
Docker volume mounts and permissions tests for Myki Tracker containerization.

Tests verify that:
- All required directories exist after container starts
- Chrome profile directory is writable by app user (UID 1000)
- Output files can be created in /app/output directory
- Config file is readable from /app/config directory

These tests focus on critical volume mount and permission requirements.
"""

import subprocess
import pytest
import os
import tempfile
import json


class TestDockerVolumeMounts:
    """Test suite for Docker volume mount and permission validation."""

    @pytest.fixture(scope="class")
    def docker_image_name(self):
        """Docker image name for testing."""
        return "myki-tracker:test-volumes"

    @pytest.fixture(scope="class")
    def build_docker_image(self, docker_image_name):
        """Build Docker image once for all tests, or skip if already built."""
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
                cwd="/Users/gaikwadk/Documents/station-station-agentos",
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

    def test_required_directories_exist(self, build_docker_image):
        """
        Test: All required directories exist after container starts.

        Validates that the Dockerfile creates all necessary directories:
        - /app/config (for configuration files)
        - /app/browser_profile (for Chrome profile)
        - /app/output (for attendance.json results)
        - /app/auth_data (for session files)
        - /app/screenshots (for debugging screenshots)
        """
        test_script = """
        # Check if all required directories exist
        DIRS="/app/config /app/browser_profile /app/output /app/auth_data /app/screenshots"
        MISSING=""

        for dir in $DIRS; do
            if [ ! -d "$dir" ]; then
                MISSING="$MISSING $dir"
            fi
        done

        if [ -n "$MISSING" ]; then
            echo "FAILED: Missing directories:$MISSING"
            exit 1
        else
            echo "SUCCESS: All required directories exist"
            exit 0
        fi
        """

        # Override entrypoint to run our test script directly
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        assert result.returncode == 0, (
            f"Required directories check failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: All required directories exist" in result.stdout

    def test_chrome_profile_directory_writable(self, build_docker_image):
        """
        Test: Chrome profile directory is writable by app user (UID 1000).

        Validates that the app user can write to /app/browser_profile,
        which is critical for Chrome to update cookies, preferences, and session data.
        """
        test_script = """
        # Verify current user
        echo "Current user: $(whoami) (UID: $(id -u), GID: $(id -g))"

        # Check directory ownership
        ls -ld /app/browser_profile

        # Test write permission
        TEST_FILE="/app/browser_profile/test_write.txt"
        if echo "test content" > "$TEST_FILE" 2>&1; then
            echo "SUCCESS: Can write to browser_profile directory"
            rm -f "$TEST_FILE"
            exit 0
        else
            echo "FAILED: Cannot write to browser_profile directory"
            exit 1
        fi
        """

        # Override entrypoint to run our test script directly
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        assert result.returncode == 0, (
            f"Browser profile write permission check failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: Can write to browser_profile directory" in result.stdout

    def test_output_directory_writable(self, build_docker_image):
        """
        Test: Output files can be created in /app/output directory.

        Validates that the app user can create files in /app/output,
        which is required for generating attendance.json output file.
        """
        test_script = """
        # Test creating a JSON file in output directory (simulating attendance.json)
        OUTPUT_FILE="/app/output/test_output.json"

        # Create a simple JSON file
        cat > "$OUTPUT_FILE" << 'EOF'
{
    "test": "data",
    "timestamp": "2025-11-02"
}
EOF

        if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
            echo "SUCCESS: Can create files in output directory"
            # Verify it's valid JSON
            if python -m json.tool "$OUTPUT_FILE" > /dev/null 2>&1; then
                echo "SUCCESS: Created file is valid JSON"
                rm -f "$OUTPUT_FILE"
                exit 0
            else
                echo "FAILED: Created file is not valid JSON"
                exit 1
            fi
        else
            echo "FAILED: Cannot create files in output directory"
            exit 1
        fi
        """

        # Override entrypoint to run our test script directly
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--entrypoint", "/bin/bash",
                build_docker_image,
                "-c", test_script
            ],
            capture_output=True,
            text=True,
            timeout=20
        )

        assert result.returncode == 0, (
            f"Output directory write permission check failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )
        assert "SUCCESS: Can create files in output directory" in result.stdout
        assert "SUCCESS: Created file is valid JSON" in result.stdout

    def test_config_directory_readable_with_mounted_file(self, build_docker_image):
        """
        Test: Config file is readable from /app/config directory.

        Validates that configuration files can be read from the config directory,
        testing with a mounted config file to simulate runtime behavior.
        """
        # Create a temporary config file to mount
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")

            # Create a simple test config
            test_config = {
                "users": [
                    {"username": "testuser", "employee_id": "12345"}
                ],
                "output_file": "output/attendance.json"
            }

            with open(config_path, 'w') as f:
                json.dump(test_config, f, indent=2)

            # Test script to read the mounted config
            test_script = """
            CONFIG_FILE="/app/config/test_config.json"

            # Check if file exists
            if [ ! -f "$CONFIG_FILE" ]; then
                echo "FAILED: Config file not found at $CONFIG_FILE"
                exit 1
            fi

            # Check if readable
            if [ ! -r "$CONFIG_FILE" ]; then
                echo "FAILED: Config file is not readable"
                exit 1
            fi

            # Try to read and parse JSON
            if python -m json.tool "$CONFIG_FILE" > /dev/null 2>&1; then
                echo "SUCCESS: Config file is readable and valid JSON"
                cat "$CONFIG_FILE"
                exit 0
            else
                echo "FAILED: Config file is not valid JSON"
                exit 1
            fi
            """

            # Override entrypoint to run our test script directly
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{temp_dir}:/app/config:ro",  # Mount as read-only
                    "--entrypoint", "/bin/bash",
                    build_docker_image,
                    "-c", test_script
                ],
                capture_output=True,
                text=True,
                timeout=20
            )

            assert result.returncode == 0, (
                f"Config file read permission check failed:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )
            assert "SUCCESS: Config file is readable and valid JSON" in result.stdout
            assert "testuser" in result.stdout, "Config content should be readable"
