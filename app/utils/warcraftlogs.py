import requests
import time
import re
from typing import Optional, Dict, List, Tuple
from difflib import SequenceMatcher
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
        Fetch all participants/characters from a WarcraftLogs report using rankedCharacters.
        Converts classID to class names using WarcraftLogs class ID mappings.
        """
        query = f"""
        query {{
            reportData {{
                report(code: "{report_code}") {{
                    title
                    startTime
                    endTime
                    rankedCharacters {{
                        id
                        canonicalID
                        name
                        classID
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

        ranked_characters = report_data.get("rankedCharacters", [])

        # Convert classID to class name for better usability
        # WarcraftLogs class ID mappings (these are the actual IDs used by WarcraftLogs)
        class_names = {
            1: "Death Knight",
            2: "Druid",
            3: "Hunter",
            4: "Mage",
            5: "Monk",
            6: "Paladin",
            7: "Priest",
            8: "Rogue",
            9: "Shaman",
            10: "Warlock",
            11: "Warrior",
        }

        participants = []
        for character in ranked_characters:
            class_id = character.get("classID")
            class_name = class_names.get(class_id, "Unknown")

            participant = {
                "id": character.get("id"),
                "canonicalID": character.get("canonicalID"),
                "name": character.get("name"),
                "class": class_name,
                "classID": character.get("classID"),
                "role": "DPS",  # Default role
            }
            participants.append(participant)

        return participants

    def get_report_fights(self, report_code: str) -> Optional[List[Dict]]:
        """
        Fetch all fights from a WarcraftLogs report.
        This can be useful for understanding raid progression and attendance.
        """
        query = f"""
        query {{
            reportData {{
                report(code: "{report_code}") {{
                    fights {{
                        id
                        name
                        startTime
                        endTime
                        difficulty
                        kill
                        encounterID
                        averageItemLevel
                        bossPercentage
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

        return report_data.get("fights", [])


# Global API client instance
warcraftlogs_api = WarcraftLogsAPI()


def extract_report_code(url: str) -> Optional[str]:
    """
    Extract the report code from a WarcraftLogs report URL.
    Example: https://www.warcraftlogs.com/reports/abc123 -> 'abc123'
    """
    import re

    # Handle None or empty URLs
    if not url:
        return None

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


def normalize_username(username: str) -> str:
    """
    Normalize a WoW username for comparison by removing special characters and converting to lowercase.
    This helps with fuzzy matching of usernames that may have different special character representations.
    """
    # Remove common special characters and convert to lowercase
    normalized = re.sub(r"[^\w\s]", "", username.lower())
    # Remove extra whitespace
    normalized = re.sub(r"\s+", "", normalized)
    return normalized


def fuzzy_match_username(
    target_name: str, candidate_names: List[str], threshold: float = 0.8
) -> Optional[str]:
    """
    Find the best fuzzy match for a username among a list of candidates.

    Args:
        target_name: The username to match
        candidate_names: List of candidate usernames to match against
        threshold: Minimum similarity score (0.0 to 1.0) to consider a match

    Returns:
        The best matching username if above threshold, None otherwise
    """
    if not candidate_names:
        return None

    target_normalized = normalize_username(target_name)
    best_match = None
    best_score = 0.0

    for candidate in candidate_names:
        candidate_normalized = normalize_username(candidate)

        # Use SequenceMatcher for fuzzy string matching
        score = SequenceMatcher(
            None, target_normalized, candidate_normalized
        ).ratio()

        if score > best_score and score >= threshold:
            best_score = score
            best_match = candidate

    return best_match


def match_participants_to_toons(
    participants: List[Dict],
    team_toons: List[Dict],
    fuzzy_threshold: float = 0.8,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Match WarcraftLogs participants to existing toons in the team.

    Args:
        participants: List of participants from WarcraftLogs report
        team_toons: List of toons in the team
        fuzzy_threshold: Threshold for fuzzy name matching

    Returns:
        Tuple of (matched_participants, unmatched_team_toons, unknown_participants)
    """
    matched_participants = []
    unmatched_team_toons = team_toons.copy()
    unknown_participants = []

    # Create a mapping of normalized usernames to toon data
    toon_map = {}
    for toon in team_toons:
        normalized_name = normalize_username(toon["username"])
        toon_map[normalized_name] = toon

    # Match participants to toons
    for participant in participants:
        participant_name = participant.get("name", "")
        matched_toon = None

        # First try exact match (case-insensitive)
        for toon in unmatched_team_toons:
            if toon["username"].lower() == participant_name.lower():
                matched_toon = toon
                break

        # If no exact match, try fuzzy matching
        if not matched_toon:
            candidate_names = [
                toon["username"] for toon in unmatched_team_toons
            ]
            fuzzy_match = fuzzy_match_username(
                participant_name, candidate_names, fuzzy_threshold
            )
            if fuzzy_match:
                matched_toon = next(
                    toon
                    for toon in unmatched_team_toons
                    if toon["username"] == fuzzy_match
                )

        if matched_toon:
            # Add participant info to matched toon
            matched_participant = {
                "toon": matched_toon,
                "participant": participant,
                "is_present": True,
                "notes": f"Present in WarcraftLogs report as {participant_name}",
            }
            matched_participants.append(matched_participant)

            # Remove from unmatched list
            unmatched_team_toons = [
                t for t in unmatched_team_toons if t["id"] != matched_toon["id"]
            ]
        else:
            # This participant is not in our team
            unknown_participant = {
                "participant": participant,
                "suggested_member": None,  # Will be filled by frontend logic
                "notes": f"Unknown participant: {participant_name}",
            }
            unknown_participants.append(unknown_participant)

    # Mark remaining team toons as absent
    for toon in unmatched_team_toons:
        absent_toon = {
            "toon": toon,
            "participant": None,
            "is_present": False,
            "notes": "Not present in WarcraftLogs report",
        }
        matched_participants.append(absent_toon)

    return matched_participants, unmatched_team_toons, unknown_participants


def process_warcraftlogs_raid(
    warcraftlogs_url: str, team_toons: List[Dict], fuzzy_threshold: float = 0.8
) -> Dict:
    """
    Process a WarcraftLogs report for raid attendance.

    Args:
        warcraftlogs_url: The WarcraftLogs report URL
        team_toons: List of toons in the team
        fuzzy_threshold: Threshold for fuzzy name matching

    Returns:
        Dict containing:
        - report_metadata: Report information
        - participants: List of participants from report
        - matched_participants: Team toons matched to participants
        - unknown_participants: Participants not in team
        - attendance_records: List of attendance records to create
        - success: Boolean indicating if processing was successful
        - error: Error message if processing failed
    """
    try:
        # Extract report code
        report_code = extract_report_code(warcraftlogs_url)
        if not report_code:
            return {
                "success": False,
                "error": "Invalid WarcraftLogs URL format",
            }

        # Fetch report metadata
        report_metadata = fetch_report_metadata(report_code)
        if not report_metadata:
            return {
                "success": False,
                "error": "Failed to fetch WarcraftLogs report metadata",
            }

        # Fetch participants
        participants = fetch_report_participants(report_code)
        if not participants:
            return {
                "success": False,
                "error": "No participants found in WarcraftLogs report",
            }

        # Match participants to team toons
        matched_participants, unmatched_team_toons, unknown_participants = (
            match_participants_to_toons(
                participants, team_toons, fuzzy_threshold
            )
        )

        # Create attendance records
        attendance_records = []
        for matched in matched_participants:
            attendance_record = {
                "toon_id": matched["toon"]["id"],
                "is_present": matched["is_present"],
                "notes": matched["notes"],
            }
            attendance_records.append(attendance_record)

        return {
            "success": True,
            "report_metadata": report_metadata,
            "participants": participants,
            "matched_participants": matched_participants,
            "unknown_participants": unknown_participants,
            "attendance_records": attendance_records,
            "error": None,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing WarcraftLogs report: {str(e)}",
        }


def fetch_report_fights(report_code: str) -> Optional[List[Dict]]:
    """
    Fetch all fights from a WarcraftLogs report.
    This can be useful for understanding raid progression and attendance.
    """
    return warcraftlogs_api.get_report_fights(report_code)
