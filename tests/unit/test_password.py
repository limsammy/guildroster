"""
Unit tests for password hashing utilities.
"""

import pytest
from app.utils.password import hash_password, verify_password


class TestPasswordHashing:
    def test_hash_password(self):
        """Test that password hashing works correctly."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Hash should be different from original password
        assert hashed != password

        # Hash should be a string
        assert isinstance(hashed, str)

        # Hash should be longer than original password
        assert len(hashed) > len(password)

        # Hash should start with sha256 identifier
        assert hashed.startswith("sha256$")

    def test_verify_password_correct(self):
        """Test that password verification works with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Should verify correctly
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that password verification fails with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        # Should not verify with wrong password
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test that empty passwords are handled correctly."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Empty password should not verify
        assert verify_password("", hashed) is False
        assert verify_password(None, hashed) is False  # type: ignore[arg-type]

    def test_hash_password_empty(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_password("")

        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_password(None)  # type: ignore[arg-type]

    def test_same_password_different_hashes(self):
        """Test that the same password produces different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2

        # Both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_strong_password_hashing(self):
        """Test hashing of strong passwords."""
        strong_password = "MyStr0ng!P@ssw0rd"
        hashed = hash_password(strong_password)

        assert verify_password(strong_password, hashed) is True
        assert (
            verify_password("MyStr0ng!P@ssw0rd", hashed) is True
        )  # Same password
        assert (
            verify_password("mystr0ng!p@ssw0rd", hashed) is False
        )  # Different case

    def test_special_characters(self):
        """Test hashing of passwords with special characters."""
        special_password = "p@ssw0rd!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = hash_password(special_password)

        assert verify_password(special_password, hashed) is True
        assert (
            verify_password("p@ssw0rd!@#$%^&*()_+-=[]{}|;:,.<>?", hashed)
            is True
        )
        assert verify_password("password", hashed) is False
