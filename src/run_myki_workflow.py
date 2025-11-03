"""Myki Workflow Orchestrator

Automatically runs Phase 1 (authentication) followed by Phase 2 (attendance tracking)
if authentication succeeds. Supports custom config file path.

Usage:
    python run_myki_workflow.py                              # Use default config
    python run_myki_workflow.py config/custom_config.json   # Use custom config
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

from myki_auth import main as auth_main
from myki_attendance_tracker import main as tracker_main
from config_manager import load_unified_config, validate_user_config, load_user_credentials
from dotenv import load_dotenv


def print_header(title, char="=", width=80):
    """Print a formatted header."""
    print("\n" + char * width)
    print(title)
    print(char * width)


def validate_unified_config_requirements(config_path):
    """Validate unified configuration requirements (both Phase 1 and Phase 2).

    Args:
        config_path: Path to unified config file

    Returns:
        Tuple of (success: bool, error_message: str or None)
    """
    # Load .env file
    load_dotenv()

    # Determine config file path
    if not config_path:
        config_path = "config/myki_config.json"

    # Check if config file exists
    if not Path(config_path).exists():
        return False, (
            f"Config file not found: {config_path}\n"
            f"  Create config file first (see config/myki_config.example.json)"
        )

    print(f"✓ Config file found: {config_path}")

    # Try to load and validate unified config
    try:
        user_config = load_unified_config(config_path)
        validate_user_config(user_config)
    except FileNotFoundError as e:
        return False, f"Config file error: {str(e)}"
    except ValueError as e:
        return False, f"Config validation error: {str(e)}"
    except Exception as e:
        return False, f"Config error: {str(e)}"

    # Validate user credentials exist in environment
    try:
        user_credentials = load_user_credentials(user_config)
        print(f"✓ Credentials loaded for {len(user_credentials)} user(s)")
    except ValueError as e:
        return False, str(e)

    print(f"✓ Configuration validated for {len(user_config)} user(s)")

    return True, None


def run_preflight_checks(config_path):
    """Run all pre-flight validation checks before Phase 1.

    Args:
        config_path: Path to config file

    Returns:
        bool: True if all checks pass, False otherwise
    """
    print_header("PRE-FLIGHT VALIDATION")
    print("Checking unified configuration...")
    print()

    # Validate unified config (covers both Phase 1 auth and Phase 2 tracking)
    success, error = validate_unified_config_requirements(config_path)
    if not success:
        print(f"❌ Configuration validation failed:\n{error}")
        return False

    print()
    print("✅ All pre-flight checks passed")
    print("Ready to proceed with authentication and tracking")

    return True


def main():
    """Run the complete Myki workflow: auth then tracking.

    Returns:
        Exit code: 0 if both phases succeed, 1 if any phase fails
    """
    start_time = datetime.now()

    print_header("MYKI WORKFLOW ORCHESTRATOR")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get config path from CLI args if provided
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        print(f"Using config file: {config_path}")
    else:
        config_path = "config/myki_config.json"
        print(f"Using default config file: {config_path}")

    # PRE-FLIGHT VALIDATION: Check all requirements before starting
    if not run_preflight_checks(config_path):
        print_header("❌ WORKFLOW ABORTED - Pre-flight checks failed", char="=")
        print("\nPlease fix the above issues and try again.")

        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\nEnd time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration: {duration}")

        return 1

    # Load unified config (validation already done in pre-flight)
    load_dotenv()
    user_config = load_unified_config(config_path)
    user_credentials = load_user_credentials(user_config)

    # Phase 1: Authentication (Multi-User)
    print_header("PHASE 1: MULTI-USER AUTHENTICATION")

    # Save original sys.argv to restore later
    original_argv = sys.argv.copy()

    # Track authentication results
    auth_successes = []
    auth_failures = []

    # Get usernames (filter out comment keys)
    usernames = [k for k in user_config.keys() if not k.startswith("_")]

    # Authenticate each user sequentially
    for config_key in usernames:
        # Get credentials for this user
        creds = user_credentials[config_key]
        myki_username = creds["username"]
        myki_password = creds["password"]
        display_name = creds["display_username"]

        print(f"\n{'─' * 80}")
        print(f"Authenticating: {display_name}")
        print(f"{'─' * 80}")

        # Set environment variables for this user
        # Use actual Myki username from credentials (may differ from config key)
        os.environ['MYKI_USERNAME'] = myki_username
        os.environ['MYKI_PASSWORD'] = myki_password
        os.environ['MYKI_AUTH_USERNAME_KEY'] = config_key  # For session file naming

        # Clear args for auth_main (it doesn't take CLI args)
        sys.argv = [sys.argv[0]]

        try:
            auth_exit_code = auth_main()
            if auth_exit_code == 0:
                auth_successes.append(display_name)
                print(f"  ✓ {display_name} authenticated successfully")
            else:
                auth_failures.append(display_name)
                print(f"  ✗ {display_name} authentication failed (exit code {auth_exit_code})")
        except Exception as e:
            auth_failures.append(display_name)
            print(f"  ✗ {display_name} authentication error: {e}")
            import traceback
            traceback.print_exc()

    # Restore original sys.argv
    sys.argv = original_argv

    # Print authentication summary
    print(f"\n{'=' * 80}")
    print(f"Authentication Summary")
    print(f"{'=' * 80}")
    print(f"Total users: {len(usernames)}")
    print(f"  ✓ Successful: {len(auth_successes)}")
    print(f"  ✗ Failed: {len(auth_failures)}")

    if auth_failures:
        print(f"\nFailed authentications:")
        for username in auth_failures:
            print(f"  - {username}")

    # If ANY user failed, abort
    if auth_failures:
        print_header("❌ WORKFLOW FAILED - Some authentications did not succeed", char="=")
        print("\nPhase 2 (Attendance Tracking) will NOT run.")
        print("Please fix authentication issues and try again.")

        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\nEnd time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration: {duration}")

        return 1

    print_header("✅ PHASE 1 COMPLETE - All users authenticated successfully")
    print("\nProceeding to Phase 2...")

    # Phase 2: Attendance Tracking
    print_header("PHASE 2: ATTENDANCE TRACKING")

    # Create temporary config file with users section for Phase 2
    # (Phase 2 doesn't need auth credentials - uses saved session from Phase 1)
    import tempfile
    import json

    temp_config_file = None
    try:
        # Write users config to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(user_config, f, indent=2)
            temp_config_file = f.name

        print(f"Created temporary config for Phase 2: {temp_config_file}")

        # Set up sys.argv for tracker_main with temp config
        sys.argv = [sys.argv[0], temp_config_file]

        tracker_exit_code = tracker_main()
    except Exception as e:
        print(f"\n❌ ATTENDANCE TRACKING ERROR: {e}")
        import traceback
        traceback.print_exc()
        tracker_exit_code = 1
    finally:
        # Clean up temporary config file
        if temp_config_file and Path(temp_config_file).exists():
            os.unlink(temp_config_file)

        # Restore original sys.argv
        sys.argv = original_argv

    # Print final summary
    end_time = datetime.now()
    duration = end_time - start_time

    if tracker_exit_code != 0:
        print_header("⚠️  WORKFLOW COMPLETED WITH ERRORS")
        print("\nPhase 1 (Authentication): ✅ Success")
        print("Phase 2 (Attendance Tracking): ❌ Failed")
        print(f"\nEnd time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration: {duration}")
        return 1

    # Success!
    print_header("✅ WORKFLOW COMPLETE - All phases successful")
    print("\nPhase 1 (Authentication): ✅ Success")
    print("Phase 2 (Attendance Tracking): ✅ Success")
    print(f"\nEnd time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {duration}")

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
