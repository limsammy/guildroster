import requests
import time
from typing import Optional, Dict, List
from app.config import settings


class WarcraftLogsAPI:
    """
    WarcraftLogs API client using OAuth2 Client Credentials flow.
    Handles token management and API requests.
    """

    def __init__(self):
        self.client_id = settings.WARCRAFTLOGS_CLIENT_ID
        self.client_secret = settings.WARCRAFTLOGS_CLIENT_SECRET
        self.token_url = settings.WARCRAFTLOGS_TOKEN_URL
        self.api_url = settings.WARCRAFTLOGS_API_URL
        self._access_token = None
        self._token_expires_at = 0

    def _get_access_token(self) -> Optional[str]:
        """
        Get a valid access token using client credentials flow.
        Caches the token until it expires.
        """
        # Return cached token if still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        # Request new token
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = requests.post(self.token_url, data=token_data)
            response.raise_for_status()

            token_info = response.json()
            self._access_token = token_info["access_token"]
            # Set expiration time (subtract 60 seconds for safety)
            self._token_expires_at = time.time() + token_info["expires_in"] - 60

            return self._access_token

        except requests.exceptions.RequestException as e:
            print(f"Failed to get WarcraftLogs access token: {e}")
            return None

    def _make_api_request(self, query: str) -> Optional[Dict]:
        """
        Make a GraphQL request to the WarcraftLogs API.
        """
        access_token = self._get_access_token()
        if not access_token:
            return None

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.api_url, json={"query": query}, headers=headers
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"WarcraftLogs API request failed: {e}")
            return None

    def get_report_metadata(self, report_code: str) -> Optional[Dict]:
        """
        Fetch basic metadata for a WarcraftLogs report.
        """
        query = f"""
        query {{
            reportData {{
                report(code: "{report_code}") {{
                    title
                    startTime
                    endTime
                    owner {{ name }}
                    zone {{ name }}
                }}
            }}
        }}
        """

        result = self._make_api_request(query)
        if result and "data" in result:
            return result["data"]["reportData"]["report"]
        return None

    def get_report_participants(self, report_code: str) -> Optional[List[Dict]]:
        """
        Fetch all participants/characters from a WarcraftLogs report.
        """
        query = f"""
        query {{
            reportData {{
                report(code: "{report_code}") {{
                    playerDetails {{
                        dps {{
                            name
                            class
                            spec
                            role
                        }}
                        healers {{
                            name
                            class
                            spec
                            role
                        }}
                        tanks {{
                            name
                            class
                            spec
                            role
                        }}
                    }}
                }}
            }}
        }}
        """

        result = self._make_api_request(query)
        if not result or "data" not in result:
            return None

        report_data = result["data"]["reportData"]["report"]
        if not report_data:
            return None

        player_details = report_data["playerDetails"]
        participants = []

        # Combine all player types into a single list
        for player_type in ["dps", "healers", "tanks"]:
            if player_details.get(player_type):
                participants.extend(player_details[player_type])

        return participants


# Global API client instance
warcraftlogs_api = WarcraftLogsAPI()


def extract_report_code(url: str) -> Optional[str]:
    """
    Extract the report code from a WarcraftLogs report URL.
    Example: https://www.warcraftlogs.com/reports/abc123 -> 'abc123'
    """
    import re

    match = re.search(r"/reports/([a-zA-Z0-9]+)", url)
    if match:
        return match.group(1)
    return None


def fetch_report_metadata(
    report_code: str, access_token: Optional[str] = None
) -> Optional[Dict]:
    """
    Fetch metadata for a WarcraftLogs report using the v2 API.
    Args:
        report_code: The WarcraftLogs report code (from the URL).
        access_token: Deprecated - now handled internally by the API client.
    Returns:
        Dict with report metadata, or None if failed.
    """
    return warcraftlogs_api.get_report_metadata(report_code)


def fetch_report_participants(report_code: str) -> Optional[List[Dict]]:
    """
    Fetch all participants/characters from a WarcraftLogs report.
    Args:
        report_code: The WarcraftLogs report code (from the URL).
    Returns:
        List of participant dictionaries with name, class, spec, and role, or None if failed.
    """
    return warcraftlogs_api.get_report_participants(report_code)
