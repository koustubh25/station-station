"""Chrome profile management for Cloudflare bypass with trust signals.

This module handles copying and managing Chrome profile files to provide
browser trust signals that help bypass Cloudflare Turnstile detection.

For Docker deployment, supports using a pre-mounted Chrome profile directory
via the CHROME_PROFILE_DIR environment variable.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
import tempfile


class ProfileManager:
    """Manages Chrome profile copying for Cloudflare bypass."""

    # Files that contain trust signals recognized by Cloudflare
    PROFILE_FILES = [
        "Cookies",
        "Preferences",
        "History",
        "Web Data",
        "Login Data",
        "Network/Cookies",  # Additional cookie storage
    ]

    def __init__(self):
        """Initialize profile manager."""
        self.temp_profile_dir: Optional[Path] = None

    def get_chrome_profile_path(self) -> Path:
        """Get the path to the user's Chrome profile directory.

        Checks in order:
        1. CHROME_PROFILE_DIR environment variable (for Docker deployment)
        2. System-specific Chrome profile locations (macOS, Linux, Windows)

        Returns:
            Path to Chrome Default profile

        Raises:
            FileNotFoundError: If Chrome profile not found
        """
        # Check for environment variable override (Docker deployment)
        env_profile_dir = os.getenv('CHROME_PROFILE_DIR')
        if env_profile_dir:
            profile_path = Path(env_profile_dir)
            if profile_path.exists():
                print(f"Using Chrome profile from CHROME_PROFILE_DIR: {profile_path}")
                return profile_path
            else:
                print(f"Warning: CHROME_PROFILE_DIR set but path does not exist: {profile_path}")
                print("Falling back to system Chrome profile detection...")

        home = Path.home()

        # macOS path
        chrome_profile = home / "Library" / "Application Support" / "Google" / "Chrome" / "Default"

        if chrome_profile.exists():
            return chrome_profile

        # Linux path
        chrome_profile = home / ".config" / "google-chrome" / "Default"
        if chrome_profile.exists():
            return chrome_profile

        # Windows path (if running under WSL or similar)
        chrome_profile = home / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
        if chrome_profile.exists():
            return chrome_profile

        raise FileNotFoundError(
            f"Chrome Default profile not found. Checked:\n"
            f"  - CHROME_PROFILE_DIR environment variable: {env_profile_dir or 'not set'}\n"
            f"  - {home}/Library/Application Support/Google/Chrome/Default (macOS)\n"
            f"  - {home}/.config/google-chrome/Default (Linux)\n"
            f"  - {home}/AppData/Local/Google/Chrome/User Data/Default (Windows)"
        )

    def copy_profile(self, source_profile: Optional[Path] = None, use_mounted_profile: bool = True) -> Path:
        """Copy Chrome profile files to a temporary directory.

        For Docker deployment with mounted Chrome profile:
        - If CHROME_PROFILE_DIR is set and use_mounted_profile is True, uses the mounted
          profile directly without copying (avoiding disk I/O and permission issues)
        - Otherwise, copies profile files to a temporary directory

        Args:
            source_profile: Path to source Chrome profile (defaults to user's profile)
            use_mounted_profile: If True, use mounted profile directly without copying (Docker mode)

        Returns:
            Path to profile directory (mounted or temporary)

        Raises:
            FileNotFoundError: If source profile not found
        """
        # Check if using a pre-mounted Chrome profile (Docker deployment)
        env_profile_dir = os.getenv('CHROME_PROFILE_DIR')
        if env_profile_dir and use_mounted_profile:
            profile_path = Path(env_profile_dir)
            if profile_path.exists():
                print(f"Using mounted Chrome profile (no copy): {profile_path}")
                print("Note: Profile will be used directly, Chrome can write updates")
                # Return the parent directory of Default (or the directory itself if it's the user data dir)
                # Playwright expects user_data_dir, which should contain a Default subdirectory
                if profile_path.name == "Default":
                    return profile_path.parent
                else:
                    return profile_path
            else:
                print(f"Warning: CHROME_PROFILE_DIR set but path does not exist: {profile_path}")
                print("Falling back to profile copy mode...")

        # Standard mode: Copy profile to temporary directory
        if source_profile is None:
            source_profile = self.get_chrome_profile_path()

        if not source_profile.exists():
            raise FileNotFoundError(f"Source profile not found: {source_profile}")

        # Create temporary profile directory
        self.temp_profile_dir = Path(tempfile.mkdtemp(prefix="chrome_profile_"))
        temp_default = self.temp_profile_dir / "Default"
        temp_default.mkdir(parents=True)

        print(f"Copying profile from: {source_profile}")
        print(f"To temporary location: {temp_default}")

        # Copy profile files
        copied_count = 0
        for file_name in self.PROFILE_FILES:
            source_file = source_profile / file_name

            if source_file.exists():
                dest_file = temp_default / file_name
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                try:
                    if source_file.is_file():
                        shutil.copy2(source_file, dest_file)
                        copied_count += 1
                        print(f"  ✓ Copied: {file_name}")
                    elif source_file.is_dir():
                        shutil.copytree(source_file, dest_file)
                        copied_count += 1
                        print(f"  ✓ Copied directory: {file_name}")
                except (OSError, PermissionError) as e:
                    print(f"  ⚠ Skipped {file_name}: {e}")

        print(f"\nCopied {copied_count} profile files/directories")

        if copied_count == 0:
            raise RuntimeError("No profile files could be copied")

        return self.temp_profile_dir

    def cleanup(self):
        """Clean up temporary profile directory.

        Note: Does not clean up mounted profiles (CHROME_PROFILE_DIR).
        Only cleans up temporary directories created by copy_profile().
        """
        if self.temp_profile_dir and self.temp_profile_dir.exists():
            try:
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
                print(f"Cleaned up temporary profile: {self.temp_profile_dir}")
            except Exception as e:
                print(f"Warning: Could not clean up profile directory: {e}")
            finally:
                self.temp_profile_dir = None

    def __enter__(self):
        """Context manager entry - copy profile."""
        return self.copy_profile()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup profile."""
        self.cleanup()
        return False
