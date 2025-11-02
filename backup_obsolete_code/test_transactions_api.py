"""Test the transactions API endpoint with saved authentication data."""

import requests
import json
from pathlib import Path
from auth_loader import load_session_data


def test_transactions_api():
    """Test the transactions API with saved authentication data."""

    print("=" * 60)
    print("TESTING TRANSACTIONS API")
    print("=" * 60)

    # Load saved session data
    print("\n1. Loading saved authentication data...")
    cookies, headers, auth_request = load_session_data()

    if not cookies or not headers:
        print("✗ No authentication data found. Run authentication first.")
        return

    # Prepare the request based on the curl example
    url = "https://mykiapi.ptv.vic.gov.au/v2/myki/transactions"
    params = {'page': 0}

    # Build headers from our saved data + curl example
    request_headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'User-Agent': headers.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'),
        'Origin': headers.get('Origin', 'https://transport.vic.gov.au'),
        'Referer': headers.get('Referer', 'https://transport.vic.gov.au/'),
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    # Add authentication-specific headers from our captured auth_request
    if auth_request and auth_request.get('headers'):
        auth_headers = auth_request['headers']

        # Add x-verifytoken
        if 'x-verifytoken' in auth_headers:
            request_headers['x-verifytoken'] = auth_headers['x-verifytoken']
            print(f"\n  ✓ Added x-verifytoken: {auth_headers['x-verifytoken'][:50]}...")

        # Add x-ptvwebauth
        if 'x-ptvwebauth' in auth_headers:
            request_headers['x-ptvwebauth'] = auth_headers['x-ptvwebauth']
            print(f"  ✓ Added x-ptvwebauth: {auth_headers['x-ptvwebauth']}")

    # Add x-passthruauth header from PassthruAuth cookie
    if 'PassthruAuth' in cookies:
        request_headers['x-passthruauth'] = cookies['PassthruAuth']
        print(f"  ✓ Added x-passthruauth from cookie: {cookies['PassthruAuth'][:50]}...")

    # Note: We don't have the 'authorization: Bearer' token yet
    # Let's try without it first to see what error we get
    print("\n  ⚠ Note: Missing 'authorization: Bearer' header")
    print("    (Will try request without it to see error message)")

    # Request body - we need a card number
    # Let's try without a card number first to see if the endpoint works
    request_body = {}

    print("\n2. Making API request...")
    print(f"   URL: {url}")
    print(f"   Params: {params}")
    print(f"   Headers: {len(request_headers)} headers")
    print(f"   Cookies: {len(cookies)} cookies")

    try:
        response = requests.post(
            url,
            params=params,
            headers=request_headers,
            cookies=cookies,
            json=request_body
        )

        print(f"\n3. Response received:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")

        # Try to parse response
        try:
            response_json = response.json()
            print(f"\n   Response body (JSON):")
            print(json.dumps(response_json, indent=4))
        except:
            print(f"\n   Response body (text):")
            print(response.text)

        # Raise for HTTP errors
        response.raise_for_status()

    except requests.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
        print(f"   This error tells us what's missing or wrong")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_with_card_number(card_number: str):
    """Test transactions API with a specific card number.

    Args:
        card_number: The myki card number
    """
    print("=" * 60)
    print(f"TESTING TRANSACTIONS API WITH CARD NUMBER")
    print("=" * 60)

    # Load saved session data
    print("\n1. Loading saved authentication data...")
    cookies, headers, auth_request = load_session_data()

    if not cookies or not headers:
        print("✗ No authentication data found. Run authentication first.")
        return

    # Prepare the request
    url = "https://mykiapi.ptv.vic.gov.au/v2/myki/transactions"
    params = {'page': 0}

    # Build headers
    request_headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        'User-Agent': headers.get('User-Agent'),
        'Origin': headers.get('Origin'),
        'Referer': headers.get('Referer'),
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    # Add auth headers
    if auth_request and auth_request.get('headers'):
        auth_headers = auth_request['headers']
        if 'x-verifytoken' in auth_headers:
            request_headers['x-verifytoken'] = auth_headers['x-verifytoken']
        if 'x-ptvwebauth' in auth_headers:
            request_headers['x-ptvwebauth'] = auth_headers['x-ptvwebauth']

    # Add x-passthruauth from cookie
    if 'PassthruAuth' in cookies:
        request_headers['x-passthruauth'] = cookies['PassthruAuth']

    # Request body with card number
    request_body = {'mykiCardNumber': card_number}

    print(f"\n2. Making API request with card number: {card_number}")

    try:
        response = requests.post(
            url,
            params=params,
            headers=request_headers,
            cookies=cookies,
            json=request_body
        )

        print(f"\n3. Response:")
        print(f"   Status: {response.status_code}")

        try:
            response_json = response.json()
            print(f"\n   Response (JSON):")
            print(json.dumps(response_json, indent=4))
        except:
            print(f"\n   Response (text):")
            print(response.text)

        response.raise_for_status()

    except requests.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    # Test without card number first
    test_transactions_api()

    # If you have a card number, uncomment and test:
    # test_with_card_number("YOUR_CARD_NUMBER_HERE")
