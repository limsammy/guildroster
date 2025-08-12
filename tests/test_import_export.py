import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import zipfile
import io

from app.main import app

client = TestClient(app)


class TestImportExport:
    """Test import/export functionality."""

    def test_export_status_endpoint(self):
        """Test that export status endpoint returns correct information."""
        response = client.get("/import-export/export-status")
        assert response.status_code == 200
        data = response.json()
        assert "import_enabled" in data
        assert "export_enabled" in data
        assert "supported_formats" in data
        assert "supported_data_types" in data

    def test_import_requires_superuser(self, auth_headers):
        """Test that import endpoint requires superuser access."""
        # Test without authentication
        response = client.post("/import-export/import")
        assert response.status_code == 401

        # Test with regular user (non-superuser)
        with patch('app.utils.auth.require_superuser') as mock_require:
            mock_require.side_effect = Exception("Superuser required")
            response = client.post("/import-export/import", headers=auth_headers)
            assert response.status_code == 500

    def test_import_invalid_file_format(self, auth_headers_superuser):
        """Test that import rejects invalid file formats."""
        # Create a mock file with wrong extension
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.read.return_value = b"test content"

        with patch('fastapi.UploadFile', return_value=mock_file):
            response = client.post("/import-export/import", headers=auth_headers_superuser)
            assert response.status_code == 400
            assert "ZIP file" in response.json()["detail"]

    def test_import_valid_json_file(self, auth_headers_superuser):
        """Test importing a valid JSON file."""
        # Create test data
        test_data = {
            "guilds": [
                {
                    "name": "Test Guild",
                    "realm": "Test Realm",
                    "faction": "Alliance"
                }
            ],
            "teams": [
                {
                    "name": "Test Team",
                    "guild_name": "Test Guild",
                    "is_active": True
                }
            ]
        }

        # Create a mock file
        mock_file = MagicMock()
        mock_file.filename = "test.json"
        mock_file.read.return_value = json.dumps(test_data).encode('utf-8')

        with patch('fastapi.UploadFile', return_value=mock_file):
            with patch('app.routers.import_export.process_import_data') as mock_process:
                mock_process.return_value = {
                    "guilds": {"imported": 1, "errors": []},
                    "teams": {"imported": 1, "errors": []}
                }
                
                response = client.post("/import-export/import", headers=auth_headers_superuser)
                assert response.status_code == 200
                data = response.json()
                assert "Import completed successfully" in data["message"]

    def test_import_valid_zip_file(self, auth_headers_superuser):
        """Test importing a valid ZIP file."""
        # Create test data
        test_data = {
            "guilds": [
                {
                    "name": "Test Guild",
                    "realm": "Test Realm",
                    "faction": "Alliance"
                }
            ]
        }

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('guilds.json', json.dumps(test_data))

        # Create a mock file
        mock_file = MagicMock()
        mock_file.filename = "test.zip"
        mock_file.read.return_value = zip_buffer.getvalue()

        with patch('fastapi.UploadFile', return_value=mock_file):
            with patch('app.routers.import_export.process_import_data') as mock_process:
                mock_process.return_value = {
                    "guilds": {"imported": 1, "errors": []}
                }
                
                response = client.post("/import-export/import", headers=auth_headers_superuser)
                assert response.status_code == 200
                data = response.json()
                assert "Import completed successfully" in data["message"]


@pytest.fixture
def auth_headers_superuser():
    """Create auth headers for a superuser."""
    # This would need to be implemented based on your auth system
    # For now, we'll mock the auth requirement
    return {"Authorization": "Bearer test-superuser-token"}

