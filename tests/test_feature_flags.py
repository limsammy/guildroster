import pytest
from unittest.mock import patch
from app.config import settings
from app.routers.attendance import get_export_status


class TestFeatureFlags:
    """Test feature flag functionality."""

    def test_export_status_endpoint_enabled(self, client):
        """Test that export status endpoint returns correct status when enabled."""
        with patch.object(settings, "ENABLE_ATTENDANCE_EXPORT", True):
            response = client.get("/attendance/export/status")
            assert response.status_code == 200
            assert response.json() == {"export_enabled": True}

    def test_export_status_endpoint_disabled(self, client):
        """Test that export status endpoint returns correct status when disabled."""
        with patch.object(settings, "ENABLE_ATTENDANCE_EXPORT", False):
            response = client.get("/attendance/export/status")
            assert response.status_code == 200
            assert response.json() == {"export_enabled": False}

    def test_export_team_image_disabled(self, client, auth_headers):
        """Test that export team image endpoint returns 403 when disabled."""
        with patch.object(settings, "ENABLE_ATTENDANCE_EXPORT", False):
            response = client.get(
                "/attendance/export/team/1/image", headers=auth_headers
            )
            assert response.status_code == 403
            assert "disabled" in response.json()["detail"].lower()

    def test_export_all_teams_disabled(self, client, auth_headers):
        """Test that export all teams endpoint returns 403 when disabled."""
        with patch.object(settings, "ENABLE_ATTENDANCE_EXPORT", False):
            response = client.get(
                "/attendance/export/all-teams/image", headers=auth_headers
            )
            assert response.status_code == 403
            assert "disabled" in response.json()["detail"].lower()

    def test_boolean_parsing_from_env(self):
        """Test that boolean values are correctly parsed from environment variables."""
        # Test various truthy values
        for truthy_value in ["true", "1", "yes", "on", "TRUE", "True"]:
            with patch.dict(
                "os.environ", {"ENABLE_ATTENDANCE_EXPORT": truthy_value}
            ):
                # Recreate settings to pick up new env var
                from app.config import Settings

                test_settings = Settings()
                assert test_settings.ENABLE_ATTENDANCE_EXPORT is True

        # Test various falsy values
        for falsy_value in ["false", "0", "no", "off", "FALSE", "False", ""]:
            with patch.dict(
                "os.environ", {"ENABLE_ATTENDANCE_EXPORT": falsy_value}
            ):
                # Recreate settings to pick up new env var
                from app.config import Settings

                test_settings = Settings()
                assert test_settings.ENABLE_ATTENDANCE_EXPORT is False

    def test_default_value(self):
        """Test that the default value is True when no environment variable is set."""
        with patch.dict("os.environ", {}, clear=True):
            from app.config import Settings

            test_settings = Settings()
            assert test_settings.ENABLE_ATTENDANCE_EXPORT is True
