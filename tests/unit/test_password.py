"""
Unit tests for password hashing utilities.
"""

import pytest
from app.utils.password import (
    hash_password,
    verify_password,
    generate_salt,
    needs_rehash,
    get_password_hash_info,
    SALT_LENGTH,
    HASH_ALGORITHM,
    ITERATIONS,
)


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

        # Hash should have correct format: algorithm$iterations$salt$hash
        parts = hashed.split("$")
        assert len(parts) == 4
        assert parts[0] == "sha256"
        assert parts[1] == str(ITERATIONS)

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

    def test_verify_password_empty_hash(self):
        """Test that empty hashed passwords are handled correctly."""
        password = "testpassword123"

        # Empty hash should not verify
        assert verify_password(password, "") is False
        assert verify_password(password, None) is False  # type: ignore[arg-type]

    def test_verify_password_invalid_format(self):
        """Test that invalid hash formats are handled correctly."""
        password = "testpassword123"

        # Invalid format should not verify
        assert verify_password(password, "invalid_hash") is False
        assert (
            verify_password(password, "sha256$100000") is False
        )  # Missing parts
        assert (
            verify_password(password, "sha256$100000$salt") is False
        )  # Missing hash
        assert (
            verify_password(password, "sha256$100000$salt$hash$extra") is False
        )  # Too many parts

    def test_verify_password_wrong_algorithm(self):
        """Test that wrong algorithm in hash is handled correctly."""
        password = "testpassword123"
        wrong_algo_hash = "md5$100000$salt$hash"

        assert verify_password(password, wrong_algo_hash) is False

    def test_verify_password_invalid_iterations(self):
        """Test that invalid iterations in hash is handled correctly."""
        password = "testpassword123"
        invalid_iterations_hash = "sha256$invalid$salt$hash"

        assert verify_password(password, invalid_iterations_hash) is False

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

    def test_unicode_password(self):
        """Test hashing of passwords with unicode characters."""
        unicode_password = "p@ssw0rd🚀🌟🎉"
        hashed = hash_password(unicode_password)

        assert verify_password(unicode_password, hashed) is True
        assert verify_password("p@ssw0rd", hashed) is False


class TestSaltGeneration:
    def test_generate_salt(self):
        """Test that salt generation works correctly."""
        salt1 = generate_salt()
        salt2 = generate_salt()

        # Salts should be strings
        assert isinstance(salt1, str)
        assert isinstance(salt2, str)

        # Salts should be different (random)
        assert salt1 != salt2

        # Salts should have correct length (URL-safe base64 encoding)
        # SALT_LENGTH=32 bytes = 43 characters in URL-safe base64
        assert len(salt1) == 43
        assert len(salt2) == 43

        # Salts should be URL-safe (no + or / characters)
        assert "+" not in salt1
        assert "/" not in salt1
        assert "+" not in salt2
        assert "/" not in salt2


class TestNeedsRehash:
    def test_needs_rehash_valid_hash(self):
        """Test that valid hash doesn't need rehash."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert needs_rehash(hashed) is False

    def test_needs_rehash_invalid_format(self):
        """Test that invalid format needs rehash."""
        assert needs_rehash("invalid_hash") is True
        assert needs_rehash("sha256$100000") is True  # Missing parts
        assert needs_rehash("sha256$100000$salt") is True  # Missing hash
        assert (
            needs_rehash("sha256$100000$salt$hash$extra") is True
        )  # Too many parts

    def test_needs_rehash_wrong_algorithm(self):
        """Test that wrong algorithm needs rehash."""
        wrong_algo_hash = "md5$100000$salt$hash"
        assert needs_rehash(wrong_algo_hash) is True

    def test_needs_rehash_wrong_iterations(self):
        """Test that wrong iterations needs rehash."""
        wrong_iterations_hash = "sha256$50000$salt$hash"
        assert needs_rehash(wrong_iterations_hash) is True

    def test_needs_rehash_invalid_iterations(self):
        """Test that invalid iterations needs rehash."""
        invalid_iterations_hash = "sha256$invalid$salt$hash"
        assert needs_rehash(invalid_iterations_hash) is True

    def test_needs_rehash_exception_handling(self):
        """Test that exceptions in needs_rehash return True."""
        # This should trigger an exception and return True
        assert needs_rehash("") is True


class TestGetPasswordHashInfo:
    def test_get_password_hash_info_valid(self):
        """Test getting info from valid hash."""
        password = "testpassword123"
        hashed = hash_password(password)
        info = get_password_hash_info(hashed)

        assert info["algorithm"] == HASH_ALGORITHM
        assert info["iterations"] == ITERATIONS
        assert info["salt_length"] == 43  # URL-safe base64 length
        assert info["hash_length"] > 0
        assert info["is_valid"] is True
        assert "error" not in info

    def test_get_password_hash_info_invalid_format(self):
        """Test getting info from invalid format."""
        info = get_password_hash_info("invalid_hash")

        assert info["algorithm"] == "unknown"
        assert info["iterations"] == 0
        assert info["salt_length"] == 0
        assert info["hash_length"] == 12  # Length of "invalid_hash"
        assert info["is_valid"] is False
        assert info["error"] == "Invalid format"

    def test_get_password_hash_info_missing_parts(self):
        """Test getting info from hash with missing parts."""
        info = get_password_hash_info("sha256$100000")

        assert info["algorithm"] == "unknown"
        assert info["iterations"] == 0
        assert info["salt_length"] == 0
        assert info["hash_length"] == 13  # Length of "sha256$100000"
        assert info["is_valid"] is False
        assert info["error"] == "Invalid format"

    def test_get_password_hash_info_invalid_iterations(self):
        """Test getting info from hash with invalid iterations."""
        info = get_password_hash_info("sha256$invalid$salt$hash")

        assert info["algorithm"] == "sha256"
        assert info["iterations"] == 0
        assert info["salt_length"] == 4  # Length of "salt"
        assert info["hash_length"] == 4  # Length of "hash"
        assert info["is_valid"] is False

    def test_get_password_hash_info_wrong_algorithm(self):
        """Test getting info from hash with wrong algorithm."""
        info = get_password_hash_info("md5$100000$salt$hash")

        assert info["algorithm"] == "md5"
        assert info["iterations"] == 100000
        assert info["salt_length"] == 4  # Length of "salt"
        assert info["hash_length"] == 4  # Length of "hash"
        assert info["is_valid"] is False

    def test_get_password_hash_info_exception_handling(self):
        """Test that exceptions in get_password_hash_info are handled."""
        # This should trigger an exception and return error info
        info = get_password_hash_info("")

        assert info["algorithm"] == "unknown"
        assert info["iterations"] == 0
        assert info["salt_length"] == 0
        assert info["hash_length"] == 0
        assert info["is_valid"] is False
        assert "error" in info


class TestPasswordConstants:
    def test_password_constants(self):
        """Test that password constants are correctly defined."""
        assert SALT_LENGTH == 32
        assert HASH_ALGORITHM == "sha256"
        assert ITERATIONS == 100000
