# type: ignore[comparison-overlap,assignment,arg-type]
"""
Unit tests for invite code utilities.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.utils.invite import (
    generate_invite_code,
    ensure_unique_code,
    validate_invite_code,
    use_invite_code,
    is_invite_expired,
    calculate_expiration_date,
)
from app.models.invite import Invite
from app.models.user import User


class TestInviteCodeGeneration:
    def test_generate_invite_code_format(self):
        """Test that generated invite codes have correct format."""
        code = generate_invite_code()

        # Should be 8 characters long
        assert len(code) == 8

        # Should be uppercase alphanumeric only
        assert code.isalnum()
        assert code.isupper()

        # Should only contain A-Z and 0-9
        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        assert all(char in allowed_chars for char in code)

    def test_generate_invite_code_uniqueness(self):
        """Test that generated codes are unique."""
        codes = set()
        for _ in range(100):
            code = generate_invite_code()
            assert code not in codes
            codes.add(code)

    def test_generate_invite_code_randomness(self):
        """Test that generated codes appear random."""
        codes = [generate_invite_code() for _ in range(50)]

        # Should have different characters in different positions
        char_counts = {}
        for code in codes:
            for i, char in enumerate(code):
                key = f"pos_{i}_{char}"
                char_counts[key] = char_counts.get(key, 0) + 1

        # No single character should dominate any position
        for count in char_counts.values():
            assert (
                count < 20
            )  # No more than 20 occurrences of any char at any position


class TestEnsureUniqueCode:
    def test_ensure_unique_code_success(self, db_session):
        """Test successful unique code generation."""
        with patch("app.utils.invite.generate_invite_code") as mock_generate:
            mock_generate.side_effect = ["ABC12345", "DEF67890"]

            # Mock database query to return None (no existing code)
            with patch.object(db_session, "query") as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = (
                    None
                )

                code = ensure_unique_code(db_session)
                assert code == "ABC12345"
                assert mock_generate.call_count == 1

    def test_ensure_unique_code_retry_on_collision(self, db_session):
        """Test that code generation retries on collision."""
        with patch("app.utils.invite.generate_invite_code") as mock_generate:
            mock_generate.side_effect = ["ABC12345", "DEF67890"]

            # Mock database query to return existing code first, then None
            with patch.object(db_session, "query") as mock_query:
                mock_filter = Mock()
                mock_query.return_value.filter.return_value = mock_filter
                mock_filter.first.side_effect = [
                    Mock(),
                    None,
                ]  # First call returns existing, second returns None

                code = ensure_unique_code(db_session)
                assert code == "DEF67890"
                assert mock_generate.call_count == 2

    def test_ensure_unique_code_max_attempts_exceeded(self, db_session):
        """Test that error is raised when max attempts exceeded."""
        with patch("app.utils.invite.generate_invite_code") as mock_generate:
            mock_generate.return_value = "ABC12345"

            # Mock database query to always return existing code
            with patch.object(db_session, "query") as mock_query:
                mock_query.return_value.filter.return_value.first.return_value = (
                    Mock()
                )

                with pytest.raises(HTTPException) as exc_info:
                    ensure_unique_code(db_session, max_attempts=3)

                assert exc_info.value.status_code == 500
                assert "Unable to generate unique invite code" in str(
                    exc_info.value.detail
                )


class TestCalculateExpirationDate:
    def test_calculate_expiration_date_with_days(self):
        """Test expiration date calculation with days."""
        expires_in_days = 7
        expiration_date = calculate_expiration_date(expires_in_days)

        # Should be approximately 7 days from now
        now = datetime.now()
        expected_date = now + timedelta(days=7)

        # Allow for small time differences (within 1 second)
        time_diff = abs((expiration_date - expected_date).total_seconds())
        assert time_diff < 1

    def test_calculate_expiration_date_none(self):
        """Test expiration date calculation with None."""
        expiration_date = calculate_expiration_date(None)
        assert expiration_date is None

    def test_calculate_expiration_date_zero_days(self):
        """Test expiration date calculation with 0 days."""
        expiration_date = calculate_expiration_date(0)

        now = datetime.now()
        expected_date = now + timedelta(days=0)

        time_diff = abs((expiration_date - expected_date).total_seconds())
        assert time_diff < 1


class TestIsInviteExpired:
    def test_is_invite_expired_no_expiration(self):
        """Test expired check for invite with no expiration."""
        invite = Mock()
        invite.expires_at = None

        assert is_invite_expired(invite) is False

    def test_is_invite_expired_future_date(self):
        """Test expired check for invite with future expiration."""
        invite = Mock()
        invite.expires_at = datetime.now() + timedelta(days=1)

        assert is_invite_expired(invite) is False

    def test_is_invite_expired_past_date(self):
        """Test expired check for invite with past expiration."""
        invite = Mock()
        invite.expires_at = datetime.now() - timedelta(days=1)

        assert is_invite_expired(invite) is True

    def test_is_invite_expired_current_date(self):
        """Test expired check for invite expiring now."""
        invite = Mock()
        invite.expires_at = datetime.now()

        assert is_invite_expired(invite) is True


class TestValidateInviteCode:
    def test_validate_invite_code_success(self, db_session):
        """Test successful invite code validation."""
        # Create a valid invite
        invite = Invite(
            code="ABC12345",
            created_by=1,
            is_active=True,
            expires_at=datetime.now() + timedelta(days=1),
        )

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = (
                invite
            )

            result = validate_invite_code("abc12345", db_session)
            assert result == invite

    def test_validate_invite_code_case_insensitive(self, db_session):
        """Test that invite code validation is case insensitive."""
        invite = Invite(
            code="ABC12345",
            created_by=1,
            is_active=True,
            expires_at=datetime.now() + timedelta(days=1),
        )

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = (
                invite
            )

            # Should work with lowercase input
            result = validate_invite_code("abc12345", db_session)
            assert result == invite

    def test_validate_invite_code_not_found(self, db_session):
        """Test validation failure when code not found."""
        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = (
                None
            )

            with pytest.raises(HTTPException) as exc_info:
                validate_invite_code("INVALID", db_session)

            assert exc_info.value.status_code == 404
            assert "Invalid invite code" in str(exc_info.value.detail)

    def test_validate_invite_code_inactive(self, db_session):
        """Test validation failure when code is inactive."""
        invite = Invite(
            code="ABC12345",
            created_by=1,
            is_active=False,
            expires_at=datetime.now() + timedelta(days=1),
        )

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = (
                invite
            )

            with pytest.raises(HTTPException) as exc_info:
                validate_invite_code("ABC12345", db_session)

            assert exc_info.value.status_code == 400
            assert "has been invalidated" in str(exc_info.value.detail)

    def test_validate_invite_code_already_used(self, db_session):
        """Test validation failure when code is already used."""
        invite = Invite(
            code="ABC12345",
            created_by=1,
            used_by=2,
            is_active=True,
            expires_at=datetime.now() + timedelta(days=1),
        )

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = (
                invite
            )

            with pytest.raises(HTTPException) as exc_info:
                validate_invite_code("ABC12345", db_session)

            assert exc_info.value.status_code == 400
            assert "already been used" in str(exc_info.value.detail)

    def test_validate_invite_code_expired(self, db_session):
        """Test validation failure when code is expired."""
        invite = Invite(
            code="ABC12345",
            created_by=1,
            is_active=True,
            expires_at=datetime.now() - timedelta(days=1),
        )

        with patch.object(db_session, "query") as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = (
                invite
            )

            with pytest.raises(HTTPException) as exc_info:
                validate_invite_code("ABC12345", db_session)

            assert exc_info.value.status_code == 400
            assert "has expired" in str(exc_info.value.detail)


class TestUseInviteCode:
    def test_use_invite_code_success(self, db_session):
        """Test successful invite code usage."""
        invite = Invite(
            code="ABC12345",
            created_by=1,
            is_active=True,
            expires_at=datetime.now() + timedelta(days=1),
        )

        with patch(
            "app.utils.invite.validate_invite_code", return_value=invite
        ):
            with patch.object(db_session, "commit") as mock_commit:
                use_invite_code("ABC12345", 123, db_session)

                assert invite.used_by == 123
                assert invite.used_at is not None
                mock_commit.assert_called_once()

    def test_use_invite_code_validation_failure(self, db_session):
        """Test invite code usage with validation failure."""
        with patch("app.utils.invite.validate_invite_code") as mock_validate:
            mock_validate.side_effect = HTTPException(
                status_code=404, detail="Not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                use_invite_code("INVALID", 123, db_session)

            assert exc_info.value.status_code == 404
