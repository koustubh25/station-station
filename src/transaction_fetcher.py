"""Transaction fetching with pagination for Myki Attendance Tracker.

Handles fetching transactions from Myki API with special pagination error handling.
"""

from typing import List, Dict, Any

import requests

from myki_api_client import MykiAPIClient


def is_special_pagination_error(http_error: requests.HTTPError) -> bool:
    """Check if HTTPError is the special pagination end-of-data signal.

    The Myki API returns 409 with message "txnTimestamp: Expected a non-empty
    value. Got: null" when there are no more pages available. This is NOT an
    error - it's the API's way of signaling end-of-data.

    Args:
        http_error: requests.HTTPError exception

    Returns:
        True if this is the special pagination end-of-data error, False otherwise
    """
    # Check status code is 409
    # NOTE: Use 'is None' instead of 'not' because Response objects evaluate
    # to False for error status codes (4xx, 5xx)
    if http_error.response is None:
        return False

    if http_error.response.status_code != 409:
        return False

    # Try to parse error message from response
    try:
        error_data = http_error.response.json()
        error_message = error_data.get('message', '')

        # Check for specific message indicating end of data
        return ('txnTimestamp' in error_message and
                'Expected a non-empty value' in error_message and
                'null' in error_message)
    except:
        # If we can't parse the response, it's not the special error
        return False


def fetch_all_transactions(client: MykiAPIClient, card_number: str) -> List[Dict[str, Any]]:
    """Fetch all transactions for a myki card with pagination handling.

    Handles special pagination end-of-data signal: 409 error with message
    "txnTimestamp: Expected a non-empty value. Got: null" which indicates
    no more pages available (this is NORMAL, not an error).

    Args:
        client: MykiAPIClient instance
        card_number: Myki card number (e.g., "308425279093478")

    Returns:
        List of all transaction dictionaries across all pages

    Raises:
        requests.HTTPError: If API returns non-409 error or different 409 error
    """
    page = 0
    all_transactions = []
    MAX_PAGES = 5

    print(f"\nFetching transactions for card {card_number}...")

    while page < MAX_PAGES:
        try:
            print(f"  Fetching page {page}...")
            response = client.get_transactions(card_number, page)

            # Extract transactions from response
            # API may return different structures, handle both cases
            if isinstance(response, dict):
                if 'transactions' in response:
                    page_transactions = response['transactions']
                else:
                    # Response might be list directly or other structure
                    page_transactions = response.get('data', [])
            elif isinstance(response, list):
                page_transactions = response
            else:
                page_transactions = []

            # Add to all transactions
            all_transactions.extend(page_transactions)
            print(f"    Retrieved {len(page_transactions)} transactions")

            # Move to next page
            page += 1

        except requests.HTTPError as e:
            # Check if this is the special pagination end-of-data error
            if is_special_pagination_error(e):
                print(f"    Reached end of transaction data (page {page})")
                break  # Normal end of data - exit gracefully
            else:
                # Different error - this is an actual failure
                # NOTE: Use 'is not None' instead of truthy check because Response
                # objects evaluate to False for error status codes
                status_code = e.response.status_code if e.response is not None else 'unknown'
                print(f"✗ API error on page {page}: {status_code}")

                if e.response is not None:
                    try:
                        error_json = e.response.json()
                        print(f"  Error details: {error_json}")
                    except:
                        print(f"  Raw response: {e.response.text}")

                raise  # Re-raise actual errors

    if page >= MAX_PAGES:
        print(f"  Reached maximum page limit ({MAX_PAGES})")

    print(f"  Total transactions fetched: {len(all_transactions)}")
    return all_transactions
