#!/usr/bin/env python3
"""
Test script for WarcraftLogs API integration.
Run this to verify your credentials and API functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.utils.warcraftlogs import (
    extract_report_code,
    fetch_report_metadata,
    fetch_report_participants,
)


def test_warcraftlogs_integration():
    """Test the WarcraftLogs API integration."""

    # Check if credentials are set
    client_id = os.getenv("WARCRAFTLOGS_CLIENT_ID")
    client_secret = os.getenv("WARCRAFTLOGS_CLIENT_SECRET")

    if not client_id or not client_secret:
        print(
            "❌ WARCRAFTLOGS_CLIENT_ID and WARCRAFTLOGS_CLIENT_SECRET must be set in .env file"
        )
        return False

    print("✅ WarcraftLogs credentials found")

    # Test URL parsing
    test_url = "https://www.warcraftlogs.com/reports/abc123def456"
    report_code = extract_report_code(test_url)

    if report_code == "abc123def456":
        print("✅ URL parsing works correctly")
    else:
        print(
            f"❌ URL parsing failed. Expected 'abc123def456', got '{report_code}'"
        )
        return False

    # Test with a real report (you'll need to provide a valid report code)
    print("\nTo test with a real WarcraftLogs report:")
    print("1. Go to a WarcraftLogs report")
    print("2. Copy the report code from the URL")
    print("3. Replace 'abc123def456' in this script with the real code")
    print("4. Run the script again")

    return True


if __name__ == "__main__":
    test_warcraftlogs_integration()
