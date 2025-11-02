"""Test FlareSolverr with sessions to keep browser open longer."""

import requests
import time

def test_with_session():
    """Use FlareSolverr sessions to wait for Cloudflare."""
    print("=" * 60)
    print("TESTING FLARESOLVERR WITH SESSIONS")
    print("=" * 60)

    api_url = "http://localhost:8191/v1"

    try:
        # Step 1: Create a session
        print("\n1. Creating FlareSolverr session...")
        create_session = requests.post(api_url, json={
            "cmd": "sessions.create",
            "session": "myki_session"
        }, timeout=30)

        if create_session.status_code == 200:
            print("   ✓ Session created: myki_session")
        else:
            print(f"   ✗ Failed to create session: {create_session.text}")
            return False

        # Step 2: Navigate with much longer timeout
        print("\n2. Navigating to Myki page (90s timeout)...")
        print("   Watching browser for Cloudflare challenge...")

        navigate = requests.post(api_url, json={
            "cmd": "request.get",
            "url": "https://transport.vic.gov.au/manage-myki",
            "session": "myki_session",
            "maxTimeout": 90000,  # 90 seconds
        }, timeout=120)

        print(f"\n3. Response received!")

        if navigate.status_code == 200:
            data = navigate.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")

            solution = data.get('solution', {})
            html = solution.get('response', '')

            # Check what we got
            html_lower = html.lower()
            print(f"\n4. Content check:")
            print(f"   - Has 'verifying': {('verifying' in html_lower)}")
            print(f"   - Has 'username': {('username' in html_lower)}")
            print(f"   - Has 'password': {('password' in html_lower)}")
            print(f"   - Has 'turnstile': {('turnstile' in html_lower)}")

            # If still has Cloudflare, wait and try again
            if 'verifying' in html_lower or 'turnstile' in html_lower:
                print("\n5. Cloudflare still present, waiting 30 more seconds...")
                time.sleep(30)

                # Try to get the page again from same session
                print("\n6. Fetching page again from same session...")
                retry = requests.post(api_url, json={
                    "cmd": "request.get",
                    "url": "https://transport.vic.gov.au/manage-myki",
                    "session": "myki_session",
                    "maxTimeout": 60000,
                }, timeout=90)

                if retry.status_code == 200:
                    retry_data = retry.json()
                    retry_html = retry_data.get('solution', {}).get('response', '')
                    retry_lower = retry_html.lower()

                    print(f"\n7. Second attempt check:")
                    print(f"   - Has 'verifying': {('verifying' in retry_lower)}")
                    print(f"   - Has 'username': {('username' in retry_lower)}")

                    if 'verifying' not in retry_lower and 'username' in retry_lower:
                        print("\n   ✓ SUCCESS! Cloudflare cleared on retry!")
                        with open('screenshots/flaresolverr_session_success.html', 'w') as f:
                            f.write(retry_html)
                        return True

            elif 'username' in html_lower:
                print("\n5. ✓ No Cloudflare detected, form present!")
                with open('screenshots/flaresolverr_session_success.html', 'w') as f:
                    f.write(html)
                return True

        print("\n" + "=" * 60)
        print("FAILED - Cloudflare not bypassed")
        print("=" * 60)
        return False

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up session
        print("\n8. Destroying session...")
        try:
            requests.post(api_url, json={
                "cmd": "sessions.destroy",
                "session": "myki_session"
            }, timeout=10)
            print("   ✓ Session destroyed")
        except:
            pass


if __name__ == '__main__':
    import sys
    success = test_with_session()
    sys.exit(0 if success else 1)
