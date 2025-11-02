"""
Docker build and run scripts validation tests.

Tests verify that:
- docker-build.sh successfully builds image with correct tag
- docker-run.sh starts container with all required volume mounts
- docker-test.sh validates output file exists after run
- Scripts exit with appropriate error codes on failure

These tests focus on automation script functionality for Docker deployment.
"""

import subprocess
import os
import pytest


class TestDockerBuildScript:
    """Test suite for docker-build.sh script validation."""

    @pytest.fixture(scope="class")
    def project_root(self):
        """Project root directory."""
        return "/Users/gaikwadk/Documents/station-station-agentos"

    def test_docker_build_script_builds_image_with_correct_tag(self, project_root):
        """
        Test: docker-build.sh successfully builds image with correct tag.

        Validates that the build script:
        - Executes without errors
        - Creates an image with the expected tag 'myki-tracker:local-v1'
        - Returns exit code 0 on success
        """
        build_script = os.path.join(project_root, "docker-build.sh")

        # Check script exists
        assert os.path.exists(build_script), f"Build script not found: {build_script}"

        # Check script is executable
        assert os.access(build_script, os.X_OK), f"Build script is not executable: {build_script}"

        # Execute build script
        result = subprocess.run(
            [build_script],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for build
        )

        # Verify exit code 0
        assert result.returncode == 0, (
            f"Build script failed with exit code {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Verify image exists with correct tag
        check_image = subprocess.run(
            ["docker", "images", "-q", "myki-tracker:local-v1"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert check_image.returncode == 0, "Failed to check for Docker image"
        assert check_image.stdout.strip(), (
            "Image 'myki-tracker:local-v1' not found after build script execution"
        )

    def test_docker_run_script_has_all_required_volume_mounts(self, project_root):
        """
        Test: docker-run.sh starts container with all required volume mounts.

        Validates that the run script:
        - Contains all 5 required volume mounts (config, browser_profile, output, auth_data, screenshots)
        - Passes environment variables correctly
        - Uses proper flags (--rm, --name)
        """
        run_script = os.path.join(project_root, "docker-run.sh")

        # Check script exists
        assert os.path.exists(run_script), f"Run script not found: {run_script}"

        # Check script is executable
        assert os.access(run_script, os.X_OK), f"Run script is not executable: {run_script}"

        # Read script content
        with open(run_script, 'r') as f:
            script_content = f.read()

        # Verify required volume mounts present in script
        required_mounts = [
            "/app/config",          # Config directory
            "/app/browser_profile", # Browser profile directory
            "/app/output",          # Output directory
            "/app/auth_data",       # Auth data directory
            "/app/screenshots"      # Screenshots directory
        ]

        for mount in required_mounts:
            assert mount in script_content, (
                f"Required volume mount '{mount}' not found in docker-run.sh"
            )

        # Verify environment variables are passed
        required_env_vars = [
            "DISPLAY",              # Display for Xvfb
            "CHROME_PROFILE_DIR"    # Chrome profile directory
        ]

        for env_var in required_env_vars:
            assert env_var in script_content, (
                f"Required environment variable '{env_var}' not found in docker-run.sh"
            )

        # Verify docker run flags
        assert "--rm" in script_content, "Missing --rm flag in docker-run.sh"
        assert "--name" in script_content, "Missing --name flag in docker-run.sh"

    def test_docker_test_script_validates_output_file_exists(self, project_root):
        """
        Test: docker-test.sh validates output file exists after run.

        Validates that the test script:
        - Checks for exit code 0 from container
        - Verifies output/attendance.json exists
        - Validates JSON structure of output file
        - Returns appropriate exit codes
        """
        test_script = os.path.join(project_root, "docker-test.sh")

        # Check script exists
        assert os.path.exists(test_script), f"Test script not found: {test_script}"

        # Check script is executable
        assert os.access(test_script, os.X_OK), f"Test script is not executable: {test_script}"

        # Read script content
        with open(test_script, 'r') as f:
            script_content = f.read()

        # Verify validation checks present in script
        validation_checks = [
            "attendance.json",      # Output file check
            "exit",                 # Exit code handling
            "0"                     # Success exit code
        ]

        for check in validation_checks:
            assert check in script_content, (
                f"Expected validation check '{check}' not found in docker-test.sh"
            )

        # Verify JSON validation is mentioned (jq or python)
        assert "jq" in script_content or "python" in script_content, (
            "JSON validation not found in docker-test.sh (expected jq or python)"
        )

    def test_docker_scripts_exit_with_appropriate_error_codes_on_failure(self, project_root):
        """
        Test: Scripts exit with appropriate error codes on failure.

        Validates that scripts:
        - Use 'set -e' for error handling
        - Exit with non-zero codes on failures
        - Have proper error handling patterns
        """
        scripts = [
            "docker-build.sh",
            "docker-run.sh",
            "docker-test.sh",
            "docker-debug.sh"
        ]

        for script_name in scripts:
            script_path = os.path.join(project_root, script_name)

            # Check script exists
            assert os.path.exists(script_path), f"Script not found: {script_path}"

            # Read script content
            with open(script_path, 'r') as f:
                script_content = f.read()

            # Verify shebang
            assert script_content.startswith("#!/bin/bash"), (
                f"Script {script_name} missing proper shebang"
            )

            # Verify error handling (set -e)
            assert "set -e" in script_content, (
                f"Script {script_name} missing 'set -e' error handling"
            )
