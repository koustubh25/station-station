"""Myki API Client for making authenticated requests using saved session data.

This module uses the authentication data (cookies and headers) saved by myki_auth.py
to make authenticated API calls to the Myki API.
"""

import requests
import json
from typing import Dict, Optional, List, Any
from pathlib import Path
from auth_loader import load_session_data


class MykiAPIClient:
    """Client for making authenticated requests to the Myki API."""

    BASE_URL = "https://mykiapi.ptv.vic.gov.au/v2"

    def __init__(self, cookies: Optional[Dict] = None, headers: Optional[Dict] = None,
                 auth_request: Optional[Dict] = None, bearer_token: Optional[str] = None):
        """Initialize the API client.

        Args:
            cookies: Session cookies. If None, loads from saved data.
            headers: Request headers. If None, loads from saved data.
            auth_request: Authentication request data containing special headers.
            bearer_token: Bearer token for authorization header.
        """
        if cookies is None or headers is None:
            print("Loading saved authentication data...")
            cookies, headers, auth_request, bearer_token = load_session_data()

            if not cookies or not headers:
                raise ValueError(
                    "No authentication data found. Run authentication first."
                )

        self.cookies = cookies
        self.auth_request = auth_request or {}
        self.bearer_token = bearer_token

        # Build headers properly
        self.headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'User-Agent': headers.get('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'),
            'Origin': headers.get('Origin', 'https://transport.vic.gov.au'),
            'Referer': headers.get('Referer', 'https://transport.vic.gov.au/'),
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        # Add critical auth-specific headers from auth request
        if auth_request and auth_request.get('headers'):
            auth_headers = auth_request['headers']
            # x-verifytoken: JWT verification token from Cloudflare
            if 'x-verifytoken' in auth_headers:
                self.headers['x-verifytoken'] = auth_headers['x-verifytoken']
            # x-ptvwebauth: PTV web authentication token
            if 'x-ptvwebauth' in auth_headers:
                self.headers['x-ptvwebauth'] = auth_headers['x-ptvwebauth']

        # Add x-passthruauth header from PassthruAuth cookie (required for API calls)
        if 'PassthruAuth' in cookies:
            self.headers['x-passthruauth'] = cookies['PassthruAuth']

        # Add Authorization Bearer token (CRITICAL for API calls)
        if self.bearer_token:
            self.headers['authorization'] = f'Bearer {self.bearer_token}'
            print(f"\n✓ MykiAPIClient initialized")
            print(f"  Cookies: {len(self.cookies)} items")
            print(f"  Headers: {len(self.headers)} items")
            print(f"  Auth headers: x-verifytoken, x-ptvwebauth, x-passthruauth, authorization")
        else:
            print(f"\n⚠ MykiAPIClient initialized WITHOUT Bearer token")
            print(f"  Cookies: {len(self.cookies)} items")
            print(f"  Headers: {len(self.headers)} items")
            print(f"  Auth headers: x-verifytoken, x-ptvwebauth, x-passthruauth")
            print(f"  WARNING: API calls may fail without Bearer token!")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> requests.Response:
        """Make an authenticated request to the Myki API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/account/cards')
            data: Request body data (for POST, PUT)
            params: URL query parameters

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        print(f"\n→ {method} {url}")

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            cookies=self.cookies,
            json=data,
            params=params
        )

        print(f"← Status: {response.status_code}")

        return response

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint (e.g., '/account/cards')
            params: URL query parameters

        Returns:
            Response data as dictionary

        Raises:
            requests.HTTPError: If request fails
        """
        response = self._make_request('GET', endpoint, params=params)
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            return {'raw_content': response.text}

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint
            data: Request body data

        Returns:
            Response data as dictionary

        Raises:
            requests.HTTPError: If request fails
        """
        response = self._make_request('POST', endpoint, data=data)
        response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            return {'raw_content': response.text}

    # Common API endpoint methods

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information.

        Returns:
            Account data
        """
        print("\nFetching account information...")
        return self.get('/account')

    def get_cards(self) -> List[Dict[str, Any]]:
        """Get list of myki cards associated with the account.

        Returns:
            List of card objects
        """
        print("\nFetching myki cards...")
        result = self.get('/account/cards')
        return result if isinstance(result, list) else result

    def get_card_details(self, card_id: str) -> Dict[str, Any]:
        """Get details for a specific card.

        Args:
            card_id: Card identifier

        Returns:
            Card details
        """
        print(f"\nFetching details for card {card_id}...")
        return self.get(f'/card/{card_id}')

    def get_transactions(
        self,
        card_number: str,
        page: int = 0
    ) -> Dict[str, Any]:
        """Get transaction history for a specific myki card.

        Args:
            card_number: The myki card number (e.g., "308425279093478")
            page: Page number for pagination (default: 0)

        Returns:
            Transactions data including list of transactions

        Example:
            >>> client = MykiAPIClient()
            >>> transactions = client.get_transactions("308425279093478", page=0)
        """
        print(f"\nFetching transaction history for card {card_number}...")
        endpoint = '/myki/transactions'
        params = {'page': page}
        data = {'mykiCardNumber': card_number}

        # Use POST request as per the actual API
        response = self._make_request('POST', endpoint, data=data, params=params)

        # Special handling for 409 errors (pagination end-of-data signal)
        # Don't call raise_for_status() here - let the caller handle 409 errors
        # because 409 with "txnTimestamp: null" is a normal pagination end signal
        if response.status_code != 200 and response.status_code != 409:
            response.raise_for_status()
        elif response.status_code == 409:
            # For 409, still raise but as HTTPError so it can be caught and checked
            response.raise_for_status()

        try:
            return response.json()
        except json.JSONDecodeError:
            return {'raw_content': response.text}

    def get_balance(self, card_id: str) -> Dict[str, Any]:
        """Get balance for a specific card.

        Args:
            card_id: Card identifier

        Returns:
            Balance information
        """
        print(f"\nFetching balance for card {card_id}...")
        return self.get(f'/card/{card_id}/balance')

    def authenticate_account(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate with username and password.

        Note: This is typically not needed as we already have authenticated session.
        This is here for reference of the authentication endpoint.

        Args:
            username: Account username
            password: Account password

        Returns:
            Authentication response
        """
        print("\nAuthenticating account...")
        data = {
            'username': username,
            'password': password,
            'privacyConsentAgree': True
        }
        return self.post('/account/authenticate', data=data)


def main():
    """Test the API client with saved authentication data."""
    try:
        # Initialize client with saved data
        client = MykiAPIClient()

        print("\n" + "=" * 60)
        print("TESTING MYKI API CLIENT")
        print("=" * 60)

        # Test: Get transactions for a specific card
        # Note: You need to replace this with your actual card number
        card_number = "308425279093478"  # Example from curl request

        print(f"\n1. Testing transactions endpoint for card {card_number}...")
        print("   (Update card_number in the code with your actual card number)")

        try:
            transactions = client.get_transactions(card_number, page=0)
            print("✓ Transactions retrieved successfully!")
            print(json.dumps(transactions, indent=2))
        except requests.HTTPError as e:
            print(f"✗ Transactions endpoint failed: {e}")
            if e.response:
                try:
                    error_json = e.response.json()
                    print(f"   Error details: {json.dumps(error_json, indent=2)}")
                except:
                    print(f"   Response: {e.response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

        # Test with different pages
        print(f"\n2. Testing pagination (page 1)...")
        try:
            transactions_p1 = client.get_transactions(card_number, page=1)
            print("✓ Page 1 transactions retrieved:")
            print(json.dumps(transactions_p1, indent=2))
        except requests.HTTPError as e:
            print(f"✗ Page 1 failed: {e.response.status_code} - {e.response.text}")

        print("\n" + "=" * 60)
        print("API CLIENT TESTING COMPLETE")
        print("=" * 60)
        print("\nNOTE: Update the card_number variable with your actual myki card number")
        print("      to retrieve your own transaction data.")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
