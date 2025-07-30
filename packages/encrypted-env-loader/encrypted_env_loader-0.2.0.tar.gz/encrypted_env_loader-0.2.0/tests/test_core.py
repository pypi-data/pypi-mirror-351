"""
Tests for core functionality.
"""

import os
import tempfile
from pathlib import Path

import pytest

from encrypted_env_loader.core import (
    generate_key,
    encrypt_env_file,
    decrypt_env_file, 
    load_encrypted_env,
    validate_encrypted_file,
    encrypted_env_context,
    with_encrypted_env,
    EncryptedEnvError,
    DecryptionError,
    KeyError,
)


@pytest.fixture
def sample_env_content():
    """Sample .env file content."""
    return "DATABASE_URL=postgresql://localhost/test\nSECRET_KEY=mysecret123\nDEBUG=true\n"


@pytest.fixture
def temp_env_file(sample_env_content):
    """Create a temporary .env file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(sample_env_content)
        f.flush()
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def encryption_key():
    """Generate encryption key for testing."""
    return generate_key()


def test_generate_key():
    """Test key generation."""
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) > 0
    
    # Each key should be unique
    key2 = generate_key()
    assert key != key2


def test_encrypt_decrypt_file(temp_env_file, encryption_key, sample_env_content):
    """Test file encryption and decryption."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt the file
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        assert Path(encrypted_path).exists()
        
        # Decrypt the file
        env_vars = decrypt_env_file(encrypted_path, key=encryption_key)
        
        expected_vars = {
            "DATABASE_URL": "postgresql://localhost/test",
            "SECRET_KEY": "mysecret123", 
            "DEBUG": "true"
        }
        assert env_vars == expected_vars
        
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_encrypt_file_missing_source():
    """Test encryption with missing source file."""
    with pytest.raises(EncryptedEnvError, match="Source file not found"):
        encrypt_env_file("nonexistent.env", "output.encrypted", generate_key())


def test_decrypt_file_missing():
    """Test decryption with missing encrypted file."""
    with pytest.raises(EncryptedEnvError, match="Encrypted file not found"):
        decrypt_env_file("nonexistent.encrypted", key=generate_key())


def test_decrypt_file_wrong_key(temp_env_file, encryption_key):
    """Test decryption with wrong key."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt with one key
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        
        # Try to decrypt with different key
        wrong_key = generate_key()
        with pytest.raises(DecryptionError, match="Failed to decrypt file"):
            decrypt_env_file(encrypted_path, key=wrong_key)
            
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_validate_encrypted_file(temp_env_file, encryption_key):
    """Test encrypted file validation."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt file
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        
        # Validate with correct key
        assert validate_encrypted_file(encrypted_path, key=encryption_key) is True
        
        # Validate with wrong key
        wrong_key = generate_key()
        assert validate_encrypted_file(encrypted_path, key=wrong_key) is False
        
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_load_encrypted_env(temp_env_file, encryption_key):
    """Test loading encrypted environment variables."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt file
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        
        # Load without changing os.environ
        env_vars = load_encrypted_env(
            key=encryption_key,
            file_path=encrypted_path,
            change_os_env=False
        )
        
        expected_vars = {
            "DATABASE_URL": "postgresql://localhost/test",
            "SECRET_KEY": "mysecret123",
            "DEBUG": "true"
        }
        assert env_vars == expected_vars
        
        # Verify os.environ was not changed
        assert "DATABASE_URL" not in os.environ
        
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_load_encrypted_env_change_os_env(temp_env_file, encryption_key):
    """Test loading env vars and changing os.environ."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt file  
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        
        # Store original env state
        original_database_url = os.environ.get("DATABASE_URL")
        
        # Load with changing os.environ
        env_vars = load_encrypted_env(
            key=encryption_key,
            file_path=encrypted_path,
            change_os_env=True
        )
        
        # Verify os.environ was changed
        assert os.environ.get("DATABASE_URL") == "postgresql://localhost/test"
        assert os.environ.get("SECRET_KEY") == "mysecret123"
        assert os.environ.get("DEBUG") == "true"
        
        # Clean up
        for key in env_vars:
            if key in os.environ:
                del os.environ[key]
        
        # Restore original state
        if original_database_url is not None:
            os.environ["DATABASE_URL"] = original_database_url
            
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_encrypted_env_context(temp_env_file, encryption_key):
    """Test encrypted environment context manager."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt file
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        
        # Store original env state
        original_database_url = os.environ.get("DATABASE_URL")
        
        # Use context manager
        with encrypted_env_context(key=encryption_key, file_path=encrypted_path) as env_vars:
            # Inside context - variables should be loaded
            assert os.environ.get("DATABASE_URL") == "postgresql://localhost/test"
            assert os.environ.get("SECRET_KEY") == "mysecret123"
            assert env_vars["DATABASE_URL"] == "postgresql://localhost/test"
        
        # Outside context - variables should be restored
        current_database_url = os.environ.get("DATABASE_URL")
        assert current_database_url == original_database_url
        
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_with_encrypted_env_decorator(temp_env_file, encryption_key):
    """Test encrypted environment decorator."""
    encrypted_path = temp_env_file + ".encrypted"
    
    try:
        # Encrypt file
        encrypt_env_file(temp_env_file, encrypted_path, encryption_key)
        
        # Store original env state
        original_database_url = os.environ.get("DATABASE_URL")
        
        @with_encrypted_env(key=encryption_key, file_path=encrypted_path)
        def test_function():
            # Inside decorated function - variables should be loaded
            assert os.environ.get("DATABASE_URL") == "postgresql://localhost/test"
            assert os.environ.get("SECRET_KEY") == "mysecret123"
            return "success"
        
        result = test_function()
        assert result == "success"
        
        # After function - variables should be restored
        current_database_url = os.environ.get("DATABASE_URL")
        assert current_database_url == original_database_url
        
    finally:
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_key_from_environment(temp_env_file):
    """Test reading encryption key from environment variable."""
    encrypted_path = temp_env_file + ".encrypted"
    key = generate_key()
    
    try:
        # Set key in environment
        os.environ["TEST_KEY"] = key
        
        # Encrypt file using env key
        encrypt_env_file(temp_env_file, encrypted_path, key_env="TEST_KEY")
        assert Path(encrypted_path).exists()
        
        # Decrypt using env key
        env_vars = decrypt_env_file(encrypted_path, key_env="TEST_KEY")
        assert "DATABASE_URL" in env_vars
        
    finally:
        if "TEST_KEY" in os.environ:
            del os.environ["TEST_KEY"]
        if Path(encrypted_path).exists():
            os.unlink(encrypted_path)


def test_missing_key_environment(temp_env_file):
    """Test error when key environment variable is missing."""
    with pytest.raises(KeyError, match="Encryption key not found"):
        encrypt_env_file(temp_env_file, "dummy.encrypted", key_env="MISSING_KEY")


def test_invalid_key():
    """Test error with invalid encryption key."""
    with pytest.raises(KeyError, match="Invalid encryption key"):
        from encrypted_env_loader.core import _get_fernet
        _get_fernet("invalid-key") 