"""Helper module to load saved authentication data for Phase 2 testing.

Supports multi-user sessions by using MYKI_AUTH_USERNAME_KEY environment variable.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple


def get_session_suffix() -> str:
    """Get session file suffix for multi-user support.

    Returns:
        Empty string for single-user, or "_username" for multi-user
    """
    username_key = os.getenv('MYKI_AUTH_USERNAME_KEY', '')
    if username_key:
        return f"_{username_key}"
    return ""


def load_session_data() -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[str]]:
    """Load saved authentication data from files.

    Supports multi-user sessions via MYKI_AUTH_USERNAME_KEY environment variable.

    Returns:
        Tuple of (cookies, headers, auth_request_data, bearer_token)
        Returns (None, None, None, None) if files don't exist
    """
    suffix = get_session_suffix()
    auth_data_dir = Path(os.getenv('AUTH_DATA_DIR', 'auth_data'))
    session_file = auth_data_dir / f'session{suffix}.json'

    if not session_file.exists():
        print(f"Session file not found: {session_file}")
        print("Run authentication first to generate session data.")
        return (None, None, None, None)

    with open(session_file, 'r') as f:
        session_data = json.load(f)

    cookies = session_data.get('cookies', {})
    headers = session_data.get('headers', {})
    auth_request = session_data.get('auth_request', {})
    bearer_token = session_data.get('bearer_token')
    timestamp = session_data.get('timestamp', 'unknown')

    print(f"Loaded session data from: {session_file}")
    print(f"Session timestamp: {timestamp}")
    print(f"Cookies: {len(cookies)} items")
    print(f"Headers: {len(headers)} items")
    print(f"Auth request data: {'available' if auth_request else 'not available'}")
    print(f"Bearer token: {'available' if bearer_token else 'NOT FOUND'}")

    return (cookies, headers, auth_request, bearer_token)


def load_cookies() -> Optional[Dict]:
    """Load only cookies from saved data.

    Supports multi-user sessions via MYKI_AUTH_USERNAME_KEY environment variable.

    Returns:
        Cookie dictionary or None if file doesn't exist
    """
    suffix = get_session_suffix()
    auth_data_dir = Path(os.getenv('AUTH_DATA_DIR', 'auth_data'))
    cookies_file = auth_data_dir / f'cookies{suffix}.json'

    if not cookies_file.exists():
        print(f"Cookies file not found: {cookies_file}")
        return None

    with open(cookies_file, 'r') as f:
        cookies = json.load(f)

    print(f"Loaded {len(cookies)} cookies from: {cookies_file}")
    return cookies


def load_headers() -> Optional[Dict]:
    """Load only headers from saved data.

    Supports multi-user sessions via MYKI_AUTH_USERNAME_KEY environment variable.

    Returns:
        Headers dictionary or None if file doesn't exist
    """
    suffix = get_session_suffix()
    auth_data_dir = Path(os.getenv('AUTH_DATA_DIR', 'auth_data'))
    headers_file = auth_data_dir / f'headers{suffix}.json'

    if not headers_file.exists():
        print(f"Headers file not found: {headers_file}")
        return None

    with open(headers_file, 'r') as f:
        headers = json.load(f)

    print(f"Loaded {len(headers)} headers from: {headers_file}")
    return headers


def load_auth_request_data() -> Optional[Dict]:
    """Load authentication request data from saved data.

    Supports multi-user sessions via MYKI_AUTH_USERNAME_KEY environment variable.

    Returns:
        Auth request dictionary or None if file doesn't exist
    """
    suffix = get_session_suffix()
    auth_data_dir = Path(os.getenv('AUTH_DATA_DIR', 'auth_data'))
    auth_request_file = auth_data_dir / f'auth_request{suffix}.json'

    if not auth_request_file.exists():
        print(f"Auth request file not found: {auth_request_file}")
        return None

    with open(auth_request_file, 'r') as f:
        auth_request = json.load(f)

    print(f"Loaded auth request data from: {auth_request_file}")
    return auth_request


def display_session_info():
    """Display information about saved session data."""
    cookies, headers, auth_request = load_session_data()

    if not cookies:
        print("\nNo session data found. Run authentication first.")
        return

    print("\n" + "=" * 60)
    print("SAVED SESSION DATA")
    print("=" * 60)

    print("\nCookies:")
    for name, value in cookies.items():
        # Show truncated value for security
        display_value = value[:20] + "..." if len(value) > 20 else value
        print(f"  {name}: {display_value}")

    print("\nHeaders:")
    for name, value in headers.items():
        print(f"  {name}: {value}")

    if auth_request and auth_request.get('headers'):
        print("\nAuthentication POST Request Headers:")
        for name, value in auth_request['headers'].items():
            # Redact sensitive headers
            if name.lower() in ['cookie', 'authorization']:
                print(f"  {name}: [REDACTED]")
            else:
                print(f"  {name}: {value}")


if __name__ == '__main__':
    # Display session info when run directly
    display_session_info()
