"""Test FlareSolverr with longer timeout and post-command delay."""

import requests
import json
import time

def test_flaresolverr_with_patience():
    """Test FlareSolverr with extended timeout."""
    print("=" * 60)
    print("TESTING FLARESOLVERR WITH EXTENDED TIMEOUT")
    print("=" * 60)

    flaresolverr_url = "http://localhost:8191/v1"

    # Request with POST command that includes post-request delay
    payload = {
        "cmd": "request.get",
        "url": "https://transport.vic.gov.au/manage-myki",
        "maxTimeout": 90000,  # 90 seconds for Cloudflare to complete
        "postRequestDelay": 10000  # Wait 10 seconds after page loads
    }

    try:
        print("\n1. Sending request to FlareSolverr...")
        print(f"   URL: {payload['url']}")
        print(f"   Max timeout: 90 seconds")
        print(f"   Post-request delay: 10 seconds")
        print("\n   Watch the browser window - it should stay open longer...")

        response = requests.post(flaresolverr_url, json=payload, timeout=120)

        print(f"\n2. Response received!")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n3. FlareSolverr response:")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")

            if data.get('status') == 'ok':
                solution = data.get('solution', {})

                print(f"\n4. Solution details:")
                print(f"   Response status: {solution.get('status')}")
                print(f"   URL: {solution.get('url')}")

                cookies = solution.get('cookies', [])
                print(f"\n5. Cookies ({len(cookies)} total):")
                for cookie in cookies:
                    print(f"   - {cookie.get('name')}")

                html_response = solution.get('response', '')
                print(f"\n6. HTML response length: {len(html_response)} bytes")

                html_lower = html_response.lower()
                print(f"\n7. Content analysis:")
                print(f"   - Contains 'cloudflare': {('cloudflare' in html_lower)}")
                print(f"   - Contains 'verifying': {('verifying' in html_lower)}")
                print(f"   - Contains 'turnstile': {('turnstile' in html_lower)}")
                print(f"   - Contains 'username': {('username' in html_lower)}")
                print(f"   - Contains 'password': {('password' in html_lower)}")

                with open('screenshots/flaresolverr_slow_response.html', 'w') as f:
                    f.write(html_response)
                print(f"\n   HTML saved to: screenshots/flaresolverr_slow_response.html")

                # Show first 1000 chars to verify content
                print(f"\n8. HTML preview (first 1000 chars):")
                print("-" * 60)
                print(html_response[:1000])
                print("-" * 60)

                if 'verifying' not in html_lower and 'username' in html_lower:
                    print("\n" + "=" * 60)
                    print("SUCCESS!")
                    print("=" * 60)
                    return True
                else:
                    print("\n" + "=" * 60)
                    print("FAILED - Cloudflare challenge still present")
                    print("=" * 60)
                    return False

        else:
            print(f"Failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = test_flaresolverr_with_patience()
    sys.exit(0 if success else 1)
