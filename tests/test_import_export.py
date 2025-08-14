import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import zipfile
import io
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.models.token import Token
from app.utils.password import hash_password

client = TestClient(app)


class TestImportExport:
    """Test import/export functionality."""

    def _create_test_superuser(self, db_session: Session) -> tuple[User, Token]:
        """Create a test superuser and return user and token."""
        # Create superuser
        hashed_password = hash_password("superpassword123")
        user = User(
            username="superuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()

        # Create token for superuser
        token = Token.create_user_token(user.id, "Superuser Token")
        db_session.add(token)
        db_session.commit()

        return user, token

    def _create_test_user(self, db_session: Session) -> tuple[User, Token]:
        """Create a test regular user and return user and token."""
        # Create regular user
        hashed_password = hash_password("userpassword123")
        user = User(
            username="testuser",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()

        # Create token for regular user
        token = Token.create_user_token(user.id, "User Token")
        db_session.add(token)
        db_session.commit()

        return user, token

    def test_export_status_endpoint(self):
        """Test that export status endpoint returns correct information."""
        response = client.get("/data-import/export-status")
        assert response.status_code == 200
        data = response.json()
        assert "import_enabled" in data
        assert "export_enabled" in data
        assert "supported_formats" in data
        assert "supported_data_types" in data

    def test_import_requires_superuser(
        self, client: TestClient, db_session: Session
    ):
        """Test that import endpoint requires superuser access."""
        # Test without authentication
        response = client.post("/data-import/import")
        assert response.status_code == 401

        # Test with regular user (non-superuser)
        user, token = self._create_test_user(db_session)
        headers = {"Authorization": f"Bearer {token.key}"}

        response = client.post("/data-import/import", headers=headers)
        assert response.status_code == 403

    def test_import_invalid_file_format(
        self, client: TestClient, db_session: Session
    ):
        """Test that import rejects invalid file formats."""
        # Create superuser and token
        user, token = self._create_test_superuser(db_session)
        headers = {"Authorization": f"Bearer {token.key}"}

        # Create a file with wrong extension
        files = {"file": ("test.txt", b"test content", "text/plain")}

        response = client.post(
            "/data-import/import", headers=headers, files=files
        )
        if response.status_code != 400:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 400
        assert "ZIP or JSON file" in response.json()["detail"]

    def test_import_valid_json_file(
        self, client: TestClient, db_session: Session
    ):
        """Test importing a valid JSON file."""
        # Create superuser and token
        user, token = self._create_test_superuser(db_session)
        headers = {"Authorization": f"Bearer {token.key}"}

        # Create test data
        test_data = {
            "guilds": [
                {
                    "name": "Test Guild",
                    "realm": "Test Realm",
                    "faction": "Alliance",
                }
            ],
            "teams": [
                {
                    "name": "Test Team",
                    "guild_name": "Test Guild",
                    "is_active": True,
                }
            ],
        }

        # Create a JSON file
        json_content = json.dumps(test_data).encode("utf-8")
        files = {"file": ("test.json", json_content, "application/json")}

        with patch(
            "app.routers.data_import.process_import_data"
        ) as mock_process:
            mock_process.return_value = {
                "guilds": {"imported": 1, "errors": []},
                "teams": {"imported": 1, "errors": []},
            }

            response = client.post(
                "/data-import/import", headers=headers, files=files
            )
            if response.status_code != 200:
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            assert response.status_code == 200
            data = response.json()
            assert "Import completed successfully" in data["message"]

    def test_import_valid_zip_file(
        self, client: TestClient, db_session: Session
    ):
        """Test importing a valid ZIP file."""
        # Create superuser and token
        user, token = self._create_test_superuser(db_session)
        headers = {"Authorization": f"Bearer {token.key}"}

        # Create test data
        test_data = {
            "guilds": [
                {
                    "name": "Test Guild",
                    "realm": "Test Realm",
                    "faction": "Alliance",
                }
            ]
        }

        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("guilds.json", json.dumps(test_data))

        zip_content = zip_buffer.getvalue()
        files = {"file": ("test.zip", zip_content, "application/zip")}

        with patch(
            "app.routers.data_import.process_import_data"
        ) as mock_process:
            mock_process.return_value = {
                "guilds": {"imported": 1, "errors": []}
            }

            response = client.post(
                "/data-import/import", headers=headers, files=files
            )
            if response.status_code != 200:
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            assert response.status_code == 200
            data = response.json()
            assert "Import completed successfully" in data["message"]
