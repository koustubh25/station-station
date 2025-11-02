"""
Docker image validation tests for Myki Tracker containerization.

Tests verify that the Docker image:
- Builds successfully without errors
- Contains Python 3.9+
- Has Google Chrome Stable installed (NOT Chromium)
- Has Xvfb installed and can start display :99

These tests focus on critical build success criteria for Docker deployment.
"""

import subprocess
import pytest


class TestDockerImageBuild:
    """Test suite for Docker image build validation."""

    @pytest.fixture(scope="class")
    def docker_image_name(self):
        """Docker image name for testing."""
        return "myki-tracker:test-build"

    @pytest.fixture(scope="class")
    def build_docker_image(self, docker_image_name):
        """Build Docker image once for all tests."""
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

    def test_docker_image_builds_successfully(self, build_docker_image):
        """
        Test: Docker image builds successfully without errors.

        Validates that the Dockerfile can be built without failures,
        which is the foundation for all Docker deployment functionality.
        """
        # If we got here, build_docker_image fixture succeeded
        assert build_docker_image == "myki-tracker:test-build"

    def test_python_version_installed(self, build_docker_image):
        """
        Test: Python 3.9+ is installed and accessible.

        Verifies that the correct Python version is available in the container
        for running the Myki tracker workflow.
        """
        result = subprocess.run(
            ["docker", "run", "--rm", build_docker_image, "python", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Python check failed: {result.stderr}"

        # Extract version number (e.g., "Python 3.9.18" -> "3.9")
        version_output = result.stdout.strip()
        assert "Python 3." in version_output, f"Unexpected Python version: {version_output}"

        # Parse major.minor version
        version_parts = version_output.split()[1].split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])

        assert major == 3, f"Python major version must be 3, got {major}"
        assert minor >= 9, f"Python minor version must be >= 9, got {minor}"

    def test_chrome_stable_installed(self, build_docker_image):
        """
        Test: Google Chrome Stable is installed (verify with google-chrome --version).

        Critical test: Verifies that Google Chrome Stable (NOT Chromium) is installed,
        which is required for successful Cloudflare bypass in headed mode.
        """
        result = subprocess.run(
            ["docker", "run", "--rm", build_docker_image, "google-chrome", "--version"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Chrome check failed: {result.stderr}"

        version_output = result.stdout.strip()
        assert "Google Chrome" in version_output, f"Expected Google Chrome, got: {version_output}"
        assert "Chromium" not in version_output, "Should be Google Chrome, not Chromium"

    def test_xvfb_installed_and_can_start(self, build_docker_image):
        """
        Test: Xvfb is installed and can start display :99.

        Validates that Xvfb virtual display is available for headed Chrome execution.
        Tests that Xvfb can start on display :99 as required by the entrypoint script.
        """
        # Test Xvfb binary exists
        result = subprocess.run(
            ["docker", "run", "--rm", build_docker_image, "which", "Xvfb"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Xvfb not found: {result.stderr}"
        assert "/usr/bin/Xvfb" in result.stdout, f"Xvfb path unexpected: {result.stdout}"

        # Test Xvfb can start (run in background for 2 seconds then check)
        xvfb_test_script = """
        Xvfb :99 -screen 0 1920x1080x24 &
        XVFB_PID=$!
        sleep 2
        if ps -p $XVFB_PID > /dev/null; then
            kill $XVFB_PID
            exit 0
        else
            exit 1
        fi
        """

        result = subprocess.run(
            ["docker", "run", "--rm", build_docker_image, "/bin/bash", "-c", xvfb_test_script],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Xvfb failed to start on :99: {result.stderr}"
