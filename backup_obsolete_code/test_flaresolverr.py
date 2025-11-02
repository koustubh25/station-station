"""Test FlareSolverr for Cloudflare bypass."""

import requests
import json
import time

def test_flaresolverr():
    """Test FlareSolverr to bypass Cloudflare on Myki site."""
    print("=" * 60)
    print("TESTING FLARESOLVERR")
    print("=" * 60)

    # FlareSolverr API endpoint (default port 8191)
    flaresolverr_url = "http://localhost:8191/v1"

    # Request payload
    payload = {
        "cmd": "request.get",
        "url": "https://transport.vic.gov.au/manage-myki",
        "maxTimeout": 60000  # 60 seconds
    }

    try:
        print("\n1. Sending request to FlareSolverr...")
        print(f"   URL: {payload['url']}")

        response = requests.post(flaresolverr_url, json=payload, timeout=90)

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n2. FlareSolverr response:")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")

            if data.get('status') == 'ok':
                solution = data.get('solution', {})

                print(f"\n3. Solution details:")
                print(f"   Response status: {solution.get('status')}")
                print(f"   URL: {solution.get('url')}")

                # Get cookies
                cookies = solution.get('cookies', [])
                print(f"\n4. Cookies ({len(cookies)} total):")
                for cookie in cookies[:5]:  # Show first 5
                    print(f"   - {cookie.get('name')}: {cookie.get('value')[:40]}...")

                # Check response
                html_response = solution.get('response', '')
                print(f"\n5. HTML response length: {len(html_response)} bytes")

                # Check for indicators
                html_lower = html_response.lower()
                print(f"\n6. Content analysis:")
                print(f"   - Contains 'cloudflare': {('cloudflare' in html_lower)}")
                print(f"   - Contains 'verifying': {('verifying' in html_lower)}")
                print(f"   - Contains 'turnstile': {('turnstile' in html_lower)}")
                print(f"   - Contains 'username': {('username' in html_lower)}")
                print(f"   - Contains 'password': {('password' in html_lower)}")

                # Save HTML for inspection
                with open('screenshots/flaresolverr_response.html', 'w') as f:
                    f.write(html_response)
                print(f"\n   HTML saved to: screenshots/flaresolverr_response.html")

                # Check success
                if 'verifying' not in html_lower and 'username' in html_lower:
                    print("\n" + "=" * 60)
                    print("SUCCESS! FLARESOLVERR BYPASSED CLOUDFLARE!")
                    print("=" * 60)
                    print("\nCookies and HTML retrieved successfully!")
                    print("Login form should be accessible!")
                    return True, cookies, html_response
                else:
                    print("\n" + "=" * 60)
                    print("PARTIAL - Got response but may have challenges")
                    print("=" * 60)
                    return False, cookies, html_response

            else:
                print(f"\n   Error: {data.get('message')}")
                return False, [], ""

        else:
            print(f"   Failed with status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False, [], ""

    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, [], ""


if __name__ == '__main__':
    import sys
    success, cookies, html = test_flaresolverr()
    sys.exit(0 if success else 1)
