import requests
from typing import Optional, Dict

# TODO: Store your WarcraftLogs API client ID/secret securely
WARCRAFTLOGS_CLIENT_ID = "your_client_id"
WARCRAFTLOGS_CLIENT_SECRET = "your_client_secret"
WARCRAFTLOGS_API_URL = "https://www.warcraftlogs.com/api/v2/client"


def fetch_report_metadata(
    report_code: str, access_token: str
) -> Optional[Dict]:
    """
    Fetch metadata for a WarcraftLogs report using the v2 API.
    Args:
        report_code: The WarcraftLogs report code (from the URL).
        access_token: OAuth2 access token for WarcraftLogs API.
    Returns:
        Dict with report metadata, or None if failed.
    """
    # Example GraphQL query: get report title, start/end, etc.
    query = {
        "query": f"""
        query {{
            reportData {{
                report(code: \"{report_code}\") {{
                    title
                    startTime
                    endTime
                    owner {{ name }}
                }}
            }}
        }}
        """
    }
    resp = requests.post(
        WARCRAFTLOGS_API_URL,
        json=query,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if resp.status_code == 200:
        return resp.json()
    return None


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
