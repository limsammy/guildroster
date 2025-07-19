#!/usr/bin/env python3
"""
Test script for WarcraftLogs API integration.
Run this to verify your credentials and API functionality.
"""

import os
import sys
import argparse
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.utils.warcraftlogs import (
    extract_report_code,
    fetch_report_metadata,
    fetch_report_participants,
    fetch_report_fights,
)


def test_warcraftlogs_integration(
    url: Optional[str] = None, test_type: str = "all"
):
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

    # Test with provided URL or show instructions
    if url:
        print(f"\n🔍 Testing with provided URL: {url}")
        report_code = extract_report_code(url)

        if not report_code:
            print("❌ Could not extract report code from the provided URL")
            return False

        print(f"✅ Extracted report code: {report_code}")

        # Test metadata fetch
        print("\n📊 Fetching report metadata...")
        metadata = fetch_report_metadata(report_code)

        if metadata:
            print("✅ Report metadata fetched successfully")
            print(f"   Title: {metadata.get('title', 'Unknown')}")
            print(f"   Zone: {metadata.get('zone', {}).get('name', 'Unknown')}")
            print(f"   Start Time: {metadata.get('startTime', 'Unknown')}")
            print(f"   End Time: {metadata.get('endTime', 'Unknown')}")
            print(
                f"   Owner: {metadata.get('owner', {}).get('name', 'Unknown')}"
            )
        else:
            print("❌ Failed to fetch report metadata")
            return False

        # Test based on user choice
        if test_type in ["all", "participants"]:
            test_participants(report_code)

        if test_type in ["all", "fights"]:
            test_fights(report_code)

        print(
            "\n🎉 All tests passed! WarcraftLogs integration is working correctly."
        )
        return True

    else:
        print("\n📝 To test with a real WarcraftLogs report:")
        print(
            "   python test_warcraftlogs.py --url 'https://www.warcraftlogs.com/reports/YOUR_REPORT_CODE'"
        )
        print("\n   Example:")
        print(
            "   python test_warcraftlogs.py --url 'https://www.warcraftlogs.com/reports/abc123def456'"
        )
        print("\n   To test specific functionality:")
        print("   python test_warcraftlogs.py --url 'URL' --type participants")
        print("   python test_warcraftlogs.py --url 'URL' --type fights")
        return True


def test_participants(report_code: str) -> bool:
    """Test participant data fetching."""
    print("\n👥 Fetching participant data...")
    participants = fetch_report_participants(report_code)

    if participants:
        print(f"✅ Found {len(participants)} participants")
        print("\n📋 Participant List:")
        for i, participant in enumerate(participants, 1):
            name = participant.get("name", "Unknown")
            class_name = participant.get("class", "Unknown")
            level = participant.get("level", 0)
            print(f"   {i:2d}. {name} ({class_name} - Level {level})")
        return True
    else:
        print("❌ Failed to fetch participant data or no participants found")
        return False


def test_fights(report_code: str) -> bool:
    """Test fight data fetching."""
    print("\n⚔️ Fetching fight data...")
    fights = fetch_report_fights(report_code)

    if fights:
        print(f"✅ Found {len(fights)} fights")
        print("\n🗡️ Fight List:")
        for i, fight in enumerate(fights, 1):
            name = fight.get("name", "Unknown")
            difficulty = fight.get("difficulty", "Unknown")
            kill = fight.get("kill", False)
            percentage = fight.get("percentage", 0)
            status = "✅ Killed" if kill else f"❌ {percentage:.1f}%"
            print(f"   {i:2d}. {name} ({difficulty}) - {status}")
        return True
    else:
        print("❌ Failed to fetch fight data or no fights found")
        return False


def interactive_mode():
    """Run the test script in interactive mode."""
    print("🔧 WarcraftLogs API Test - Interactive Mode")
    print("=" * 50)

    # Get URL from user
    url = input(
        "\n📝 Enter WarcraftLogs report URL (or press Enter to skip): "
    ).strip()

    if not url:
        print("\n📝 To test with a real WarcraftLogs report:")
        print(
            "   python test_warcraftlogs.py --url 'https://www.warcraftlogs.com/reports/YOUR_REPORT_CODE'"
        )
        return True

    # Get test type from user
    print("\n🔍 What would you like to test?")
    print("   1. All functionality")
    print("   2. Participants only")
    print("   3. Fights only")

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice == "1":
            test_type = "all"
            break
        elif choice == "2":
            test_type = "participants"
            break
        elif choice == "3":
            test_type = "fights"
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

    return test_warcraftlogs_integration(url, test_type)


def main():
    parser = argparse.ArgumentParser(
        description="Test WarcraftLogs API integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url "https://www.warcraftlogs.com/reports/abc123def456"
  %(prog)s --url "https://www.warcraftlogs.com/reports/xyz789ghi012" --type participants
  %(prog)s --url "https://www.warcraftlogs.com/reports/xyz789ghi012" --type fights
  %(prog)s --interactive
        """,
    )

    parser.add_argument(
        "--url", type=str, help="WarcraftLogs report URL to test with"
    )

    parser.add_argument(
        "--type",
        type=str,
        choices=["all", "participants", "fights"],
        default="all",
        help="Type of test to run (default: all)",
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    if args.interactive:
        success = interactive_mode()
    else:
        success = test_warcraftlogs_integration(args.url, args.type)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
