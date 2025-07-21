import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from app.utils.warcraftlogs import (
    extract_report_code,
    fetch_report_metadata,
    fetch_report_participants,
    fetch_report_fights,
    WarcraftLogsAPI,
)


class TestExtractReportCode:
    """Test URL parsing functionality."""

    def test_valid_warcraftlogs_url(self):
        """Test extracting report code from valid WarcraftLogs URL."""
        url = "https://www.warcraftlogs.com/reports/abc123def456"
        result = extract_report_code(url)
        assert result == "abc123def456"

    def test_valid_url_with_extra_path(self):
        """Test extracting report code from URL with additional path segments."""
        url = "https://www.warcraftlogs.com/reports/abc123def456/fights"
        result = extract_report_code(url)
        assert result == "abc123def456"

    def test_invalid_url_format(self):
        """Test handling of invalid URL formats."""
        invalid_urls = [
            "https://www.warcraftlogs.com/reports/",
            "https://www.warcraftlogs.com/reports",
            "https://www.warcraftlogs.com/",
            "https://www.warcraftlogs.com",
            "not_a_url",
            "",
            None,
        ]

        for url in invalid_urls:
            result = extract_report_code(url)
            assert result is None

    def test_url_with_different_case(self):
        """Test URL parsing with different case combinations."""
        urls = [
            "https://www.warcraftlogs.com/reports/ABC123DEF456",
            "https://www.warcraftlogs.com/reports/abc123DEF456",
            "https://www.warcraftlogs.com/reports/ABC123def456",
        ]

        for url in urls:
            result = extract_report_code(url)
            assert result is not None
            assert len(result) == 12


class TestWarcraftLogsAPI:
    """Test WarcraftLogs API client functionality."""

    @pytest.fixture
    def api_client(self):
        """Create a WarcraftLogs API client for testing."""
        with patch("app.utils.warcraftlogs.settings") as mock_settings:
            mock_settings.WARCRAFTLOGS_CLIENT_ID = "test_client_id"
            mock_settings.WARCRAFTLOGS_CLIENT_SECRET = "test_client_secret"
            mock_settings.WARCRAFTLOGS_TOKEN_URL = (
                "https://test.com/oauth/token"
            )
            mock_settings.WARCRAFTLOGS_API_URL = (
                "https://test.com/api/v2/client"
            )
            return WarcraftLogsAPI()

    @patch("app.utils.warcraftlogs.requests.post")
    def test_token_acquisition_success(self, mock_post, api_client):
        """Test successful token acquisition."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        # Test token acquisition
        token = api_client._get_access_token()

        assert token == "test_access_token"
        assert api_client._access_token == "test_access_token"
        assert api_client._token_expires_at > 0

    @patch("app.utils.warcraftlogs.requests.post")
    def test_token_acquisition_failure(self, mock_post, api_client):
        """Test token acquisition failure."""
        # Mock failed token response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("Unauthorized")
        )
        mock_post.return_value = mock_response

        # Test token acquisition failure
        token = api_client._get_access_token()

        assert token is None
        assert api_client._access_token is None

    @patch("app.utils.warcraftlogs.requests.post")
    def test_token_caching(self, mock_post, api_client):
        """Test that tokens are cached and reused."""
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        # Get token twice
        token1 = api_client._get_access_token()
        token2 = api_client._get_access_token()

        # Should only make one API call
        assert mock_post.call_count == 1
        assert token1 == token2 == "test_access_token"

    @patch("app.utils.warcraftlogs.requests.post")
    def test_api_request_success(self, mock_post, api_client):
        """Test successful API request."""
        # Mock token acquisition
        api_client._access_token = "test_token"
        api_client._token_expires_at = 9999999999  # Far future

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "reportData": {
                    "report": {
                        "title": "Test Report",
                        "startTime": 1234567890,
                        "endTime": 1234567890,
                        "owner": {"name": "Test Owner"},
                        "zone": {"name": "Test Zone"},
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Test API request
        query = 'query { reportData { report(code: "test") { title } } }'
        result = api_client._make_api_request(query)

        assert result is not None
        assert result["data"]["reportData"]["report"]["title"] == "Test Report"

    @patch("app.utils.warcraftlogs.requests.post")
    def test_api_request_failure(self, mock_post, api_client):
        """Test API request failure."""
        # Mock token acquisition
        api_client._access_token = "test_token"
        api_client._token_expires_at = 9999999999  # Far future

        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("Server Error")
        )
        mock_post.return_value = mock_response

        # Test API request failure
        query = 'query { reportData { report(code: "test") { title } } }'
        result = api_client._make_api_request(query)

        assert result is None

    @patch("app.utils.warcraftlogs.requests.post")
    def test_get_report_metadata_success(self, mock_post, api_client):
        """Test successful report metadata retrieval."""
        # Mock token acquisition
        api_client._access_token = "test_token"
        api_client._token_expires_at = 9999999999  # Far future

        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "reportData": {
                    "report": {
                        "title": "Test Report",
                        "startTime": 1234567890,
                        "endTime": 1234567890,
                        "owner": {"name": "Test Owner"},
                        "zone": {"name": "Test Zone"},
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Test metadata retrieval
        result = api_client.get_report_metadata("test123")

        assert result is not None
        assert result["title"] == "Test Report"
        assert result["owner"]["name"] == "Test Owner"
        assert result["zone"]["name"] == "Test Zone"

    @patch("app.utils.warcraftlogs.requests.post")
    def test_get_report_participants_success(self, mock_post, api_client):
        """Test successful participant data retrieval."""
        # Mock token acquisition
        api_client._access_token = "test_token"
        api_client._token_expires_at = 9999999999  # Far future

        # Mock successful API response with participant data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "reportData": {
                    "report": {
                        "title": "Test Report",
                        "startTime": 1234567890,
                        "endTime": 1234567890,
                        "rankedCharacters": [
                            {
                                "id": 123,
                                "canonicalID": 123,
                                "name": "TestPlayer1",
                                "classID": 11,
                            },
                            {
                                "id": 456,
                                "canonicalID": 456,
                                "name": "TestPlayer2",
                                "classID": 8,
                            },
                        ],
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Test participant retrieval
        result = api_client.get_report_participants("test123")

        assert result is not None
        assert len(result) == 2
        assert result[0]["name"] == "TestPlayer1"
        assert result[0]["class"] == "Druid"
        assert result[0]["classID"] == 11
        assert result[1]["name"] == "TestPlayer2"
        assert result[1]["class"] == "Mage"
        assert result[1]["classID"] == 8

    @patch("app.utils.warcraftlogs.requests.post")
    def test_get_report_fights_success(self, mock_post, api_client):
        """Test successful fight data retrieval."""
        # Mock token acquisition
        api_client._access_token = "test_token"
        api_client._token_expires_at = 9999999999  # Far future

        # Mock successful API response with fight data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "reportData": {
                    "report": {
                        "title": "Test Report",
                        "fights": [
                            {
                                "id": 1,
                                "name": "Test Boss 1",
                                "startTime": 1234567890,
                                "endTime": 1234567890,
                                "difficulty": "Mythic",
                                "kill": True,
                                "encounterID": 1001,
                                "averageItemLevel": 447,
                                "bossPercentage": 100.0,
                            },
                            {
                                "id": 2,
                                "name": "Test Boss 2",
                                "startTime": 1234567890,
                                "endTime": 1234567890,
                                "difficulty": "Mythic",
                                "kill": False,
                                "encounterID": 1002,
                                "averageItemLevel": 447,
                                "bossPercentage": 45.2,
                            },
                        ],
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        # Test fight retrieval
        result = api_client.get_report_fights("test123")

        assert result is not None
        assert len(result) == 2
        assert result[0]["name"] == "Test Boss 1"
        assert result[0]["kill"] is True
        assert result[0]["difficulty"] == "Mythic"
        assert result[1]["name"] == "Test Boss 2"
        assert result[1]["kill"] is False
        assert result[1]["bossPercentage"] == 45.2

    def test_class_name_conversion(self, api_client):
        """Test class ID to class name conversion."""
        # Test all class mappings by creating a mock participant and processing it
        class_mappings = {
            1: "Warrior",
            2: "Paladin",
            3: "Hunter",
            4: "Rogue",
            5: "Priest",
            6: "Death Knight",
            7: "Shaman",
            8: "Mage",
            9: "Warlock",
            10: "Monk",
            11: "Druid",
            12: "Demon Hunter",
            13: "Evoker",
        }

        # Test the conversion logic by creating a mock response and processing it
        for class_id, expected_name in class_mappings.items():
            # Create a mock response with the class ID
            mock_response_data = {
                "data": {
                    "reportData": {
                        "report": {
                            "title": "Test Report",
                            "rankedCharacters": [
                                {
                                    "id": 1,
                                    "canonicalID": 1,
                                    "name": "TestPlayer",
                                    "classID": class_id,
                                }
                            ],
                        }
                    }
                }
            }

            # Test the conversion by mocking the API call and checking the result
            with patch.object(
                api_client, "_make_api_request", return_value=mock_response_data
            ):
                result = api_client.get_report_participants("test123")

                assert result is not None
                assert len(result) == 1
                assert result[0]["class"] == expected_name
                assert result[0]["classID"] == class_id

    def test_unknown_class_id(self, api_client):
        """Test handling of unknown class ID."""
        # Create a mock response with an unknown class ID
        mock_response_data = {
            "data": {
                "reportData": {
                    "report": {
                        "title": "Test Report",
                        "rankedCharacters": [
                            {
                                "id": 1,
                                "canonicalID": 1,
                                "name": "TestPlayer",
                                "classID": 999,  # Unknown class ID
                            }
                        ],
                    }
                }
            }
        }

        # Test the conversion by mocking the API call and checking the result
        with patch.object(
            api_client, "_make_api_request", return_value=mock_response_data
        ):
            result = api_client.get_report_participants("test123")

            assert result is not None
            assert len(result) == 1
            assert result[0]["class"] == "Unknown"
            assert result[0]["classID"] == 999


class TestWrapperFunctions:
    """Test the wrapper functions that provide easy access to the API."""

    @patch("app.utils.warcraftlogs.warcraftlogs_api")
    def test_fetch_report_metadata(self, mock_api):
        """Test the fetch_report_metadata wrapper function."""
        mock_api.get_report_metadata.return_value = {"title": "Test Report"}

        result = fetch_report_metadata("test123")

        assert result == {"title": "Test Report"}
        mock_api.get_report_metadata.assert_called_once_with("test123")

    @patch("app.utils.warcraftlogs.warcraftlogs_api")
    def test_fetch_report_participants(self, mock_api):
        """Test the fetch_report_participants wrapper function."""
        mock_api.get_report_participants.return_value = [
            {"name": "TestPlayer", "class": "Druid"}
        ]

        result = fetch_report_participants("test123")

        assert result == [{"name": "TestPlayer", "class": "Druid"}]
        mock_api.get_report_participants.assert_called_once_with("test123")

    @patch("app.utils.warcraftlogs.warcraftlogs_api")
    def test_fetch_report_fights(self, mock_api):
        """Test the fetch_report_fights wrapper function."""
        mock_api.get_report_fights.return_value = [
            {"name": "Test Boss", "kill": True}
        ]

        result = fetch_report_fights("test123")

        assert result == [{"name": "Test Boss", "kill": True}]
        mock_api.get_report_fights.assert_called_once_with("test123")


class TestIntegrationScenarios:
    """Test integration scenarios and error handling."""

    @patch("app.utils.warcraftlogs.warcraftlogs_api")
    def test_fetch_report_metadata_with_none_response(self, mock_api):
        """Test handling of None response from API."""
        mock_api.get_report_metadata.return_value = None

        result = fetch_report_metadata("test123")

        assert result is None

    @patch("app.utils.warcraftlogs.warcraftlogs_api")
    def test_fetch_report_participants_with_empty_list(self, mock_api):
        """Test handling of empty participant list."""
        mock_api.get_report_participants.return_value = []

        result = fetch_report_participants("test123")

        assert result == []

    @patch("app.utils.warcraftlogs.warcraftlogs_api")
    def test_fetch_report_fights_with_none_response(self, mock_api):
        """Test handling of None response for fights."""
        mock_api.get_report_fights.return_value = None

        result = fetch_report_fights("test123")

        assert result is None
