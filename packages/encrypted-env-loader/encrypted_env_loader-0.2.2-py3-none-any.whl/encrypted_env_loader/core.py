"""
Core functionality for encrypted environment loading.
"""

import base64
import os
import tempfile
import subprocess
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Dict, Optional, Union, Any, Callable, List

from cryptography.fernet import Fernet, InvalidToken
from dotenv import dotenv_values

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class EncryptedEnvError(Exception):
    """Base exception for encrypted env operations."""
    pass


class DecryptionError(EncryptedEnvError):
    """Raised when decryption fails."""
    pass


class KeyError(EncryptedEnvError):
    """Raised when encryption key is invalid or missing."""
    pass


def generate_key() -> str:
    """Generate a new base64-encoded encryption key.
    
    Returns:
        Base64-encoded encryption key
    """
    return base64.urlsafe_b64encode(Fernet.generate_key()).decode()


def _get_fernet(key: str) -> Fernet:
    """Create Fernet instance from base64 key.
    
    Args:
        key: Base64-encoded encryption key
        
    Returns:
        Fernet encryption instance
        
    Raises:
        KeyError: If key is invalid
    """
    try:
        # Decode base64 key back to bytes for Fernet
        key_bytes = base64.urlsafe_b64decode(key.encode())
        return Fernet(key_bytes)
    except Exception as e:
        raise KeyError(f"Invalid encryption key: {e}")


def _resolve_file_path(file_path: Optional[str], profile: Optional[str]) -> Path:
    """Resolve the encrypted file path based on profile.
    
    Args:
        file_path: Explicit file path, or None to use default
        profile: Profile name, or None for default
        
    Returns:
        Resolved file path
    """
    if file_path:
        return Path(file_path)
    
    if profile and profile != "default":
        return Path(f".env.{profile}.encrypted")
    else:
        return Path(".env.encrypted")


def encrypt_env_file(
    source_path: Union[str, Path], 
    output_path: Optional[Union[str, Path]] = None,
    key: Optional[str] = None,
    key_env: str = "ENCRYPTED_ENV_KEY",
    profile: Optional[str] = None,
    use_keyring: bool = True
) -> None:
    """Encrypt a .env file.
    
    Args:
        source_path: Path to source .env file
        output_path: Path for encrypted output (defaults to source + .encrypted)
        key: Encryption key (if None, uses keyring then environment)
        key_env: Environment variable name for key
        profile: Profile name for keyring lookup
        use_keyring: Whether to try keyring lookup
        
    Raises:
        EncryptedEnvError: If encryption fails
        KeyError: If key is missing or invalid
    """
    source_path = Path(source_path)
    if not source_path.exists():
        raise EncryptedEnvError(f"Source file not found: {source_path}")
    
    if output_path is None:
        output_path = source_path.with_suffix(source_path.suffix + ".encrypted")
    else:
        output_path = Path(output_path)
    
    # Resolve key using new priority system
    resolved_key = _resolve_key(key, profile, key_env, use_keyring)
    
    try:
        fernet = _get_fernet(resolved_key)
        
        # Read and encrypt the file content
        content = source_path.read_bytes()
        encrypted_content = fernet.encrypt(content)
        
        # Write encrypted content
        output_path.write_bytes(encrypted_content)
        
    except Exception as e:
        raise EncryptedEnvError(f"Failed to encrypt file: {e}")


def decrypt_env_file(
    encrypted_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    key: Optional[str] = None,
    key_env: str = "ENCRYPTED_ENV_KEY",
    profile: Optional[str] = None,
    use_keyring: bool = True
) -> Dict[str, str]:
    """Decrypt an encrypted .env file.
    
    Args:
        encrypted_path: Path to encrypted file
        output_path: Path to write decrypted content (optional)
        key: Decryption key (if None, uses keyring then environment)
        key_env: Environment variable name for key
        profile: Profile name for keyring lookup
        use_keyring: Whether to try keyring lookup
        
    Returns:
        Dictionary of environment variables
        
    Raises:
        EncryptedEnvError: If file not found or decryption fails
        DecryptionError: If decryption fails
        KeyError: If key is missing or invalid
    """
    encrypted_path = Path(encrypted_path)
    if not encrypted_path.exists():
        raise EncryptedEnvError(f"Encrypted file not found: {encrypted_path}")
    
    # Resolve key using new priority system
    resolved_key = _resolve_key(key, profile, key_env, use_keyring)
    
    try:
        fernet = _get_fernet(resolved_key)
        
        # Read and decrypt content
        encrypted_content = encrypted_path.read_bytes()
        decrypted_content = fernet.decrypt(encrypted_content)
        
        # If output path specified, write decrypted content
        if output_path:
            Path(output_path).write_bytes(decrypted_content)
        
        # Parse as .env content and return as dict
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp:
            tmp.write(decrypted_content)
            tmp.flush()
            
            try:
                env_vars = dotenv_values(tmp.name)
                return {k: v for k, v in env_vars.items() if v is not None}
            finally:
                os.unlink(tmp.name)
                
    except InvalidToken:
        raise DecryptionError("Failed to decrypt file - invalid key or corrupted data")
    except Exception as e:
        raise EncryptedEnvError(f"Failed to decrypt file: {e}")


def validate_encrypted_file(
    file_path: Union[str, Path],
    key: Optional[str] = None,
    key_env: str = "ENCRYPTED_ENV_KEY",
    profile: Optional[str] = None,
    use_keyring: bool = True
) -> bool:
    """Validate that an encrypted file can be decrypted.
    
    Args:
        file_path: Path to encrypted file
        key: Decryption key (if None, uses keyring then environment)
        key_env: Environment variable name for key
        profile: Profile name for keyring lookup
        use_keyring: Whether to try keyring lookup
        
    Returns:
        True if file can be decrypted successfully
    """
    try:
        decrypt_env_file(file_path, key=key, key_env=key_env, profile=profile, use_keyring=use_keyring)
        return True
    except (EncryptedEnvError, DecryptionError, KeyError):
        return False


def load_encrypted_env(
    key: Optional[str] = None,
    file_path: Optional[str] = None,
    profile: Optional[str] = None,
    change_os_env: bool = True,
    key_env: str = "ENCRYPTED_ENV_KEY",
    use_keyring: bool = True
) -> Dict[str, str]:
    """Load encrypted environment variables.
    
    Args:
        key: Decryption key (if None, uses keyring then environment)
        file_path: Path to encrypted file (if None, uses profile-based default)
        profile: Profile name for file selection
        change_os_env: Whether to update os.environ
        key_env: Environment variable name for key
        use_keyring: Whether to try keyring lookup
        
    Returns:
        Dictionary of loaded environment variables
        
    Raises:
        EncryptedEnvError: If loading fails
        DecryptionError: If decryption fails
        KeyError: If key is missing or invalid
    """
    resolved_path = _resolve_file_path(file_path, profile)
    env_vars = decrypt_env_file(resolved_path, key=key, key_env=key_env, profile=profile, use_keyring=use_keyring)
    
    if change_os_env:
        os.environ.update(env_vars)
    
    return env_vars


@contextmanager
def encrypted_env_context(
    key: Optional[str] = None,
    file_path: Optional[str] = None,
    profile: Optional[str] = None,
    key_env: str = "ENCRYPTED_ENV_KEY",
    use_keyring: bool = True
):
    """Context manager for temporary environment variable loading.
    
    Args:
        key: Decryption key (if None, uses keyring then environment)
        file_path: Path to encrypted file
        profile: Profile name for file selection
        key_env: Environment variable name for key
        use_keyring: Whether to try keyring lookup
        
    Yields:
        Dictionary of loaded environment variables
    """
    # Load variables without changing os.environ
    env_vars = load_encrypted_env(
        key=key, 
        file_path=file_path, 
        profile=profile,
        change_os_env=False,
        key_env=key_env,
        use_keyring=use_keyring
    )
    
    # Backup current environment state
    original_env = os.environ.copy()
    
    try:
        # Apply environment variables
        os.environ.update(env_vars)
        yield env_vars
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def with_encrypted_env(
    key: Optional[str] = None,
    file_path: Optional[str] = None,
    profile: Optional[str] = None,
    key_env: str = "ENCRYPTED_ENV_KEY",
    use_keyring: bool = True
) -> Callable:
    """Decorator for functions that need encrypted environment variables.
    
    Args:
        key: Decryption key (if None, uses keyring then environment)
        file_path: Path to encrypted file
        profile: Profile name for file selection
        key_env: Environment variable name for key
        use_keyring: Whether to try keyring lookup
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with encrypted_env_context(key, file_path, profile, key_env, use_keyring):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def get_git_repo_name() -> str:
    """Get the name of the current git repository.
    
    Returns:
        Repository name (folder name)
        
    Raises:
        EncryptedEnvError: If not in a git repository
    """
    try:
        # Try to get repo name from git remote
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        # Extract repo name from URL (handle both SSH and HTTPS)
        url = result.stdout.strip()
        repo_name = url.split("/")[-1].replace(".git", "")
        return repo_name
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to directory name
        return Path.cwd().name


def _get_keyring_service_name() -> str:
    """Get the keyring service name based on git repo."""
    return get_git_repo_name()


def _get_keyring_username(profile: Optional[str]) -> str:
    """Get the keyring username for a profile.
    
    Args:
        profile: Profile name or None for default
        
    Returns:
        Username for keyring storage
    """
    profile_name = profile or "default"
    return f"{profile_name}-key"


def get_key_from_keyring(profile: Optional[str] = None) -> Optional[str]:
    """Get encryption key from system keyring.
    
    Args:
        profile: Profile name (default: "default")
        
    Returns:
        Encryption key if found, None otherwise
    """
    if not KEYRING_AVAILABLE:
        return None
    
    try:
        service = _get_keyring_service_name()
        username = _get_keyring_username(profile)
        return keyring.get_password(service, username)
    except Exception:
        # Keyring operations can fail for various reasons
        return None


def set_key_in_keyring(key: str, profile: Optional[str] = None) -> bool:
    """Store encryption key in system keyring.
    
    Args:
        key: Encryption key to store
        profile: Profile name (default: "default")
        
    Returns:
        True if successful, False otherwise
    """
    if not KEYRING_AVAILABLE:
        return False
    
    try:
        service = _get_keyring_service_name()
        username = _get_keyring_username(profile)
        keyring.set_password(service, username, key)
        return True
    except Exception:
        return False


def delete_key_from_keyring(profile: Optional[str] = None) -> bool:
    """Delete encryption key from system keyring.
    
    Args:
        profile: Profile name (default: "default")
        
    Returns:
        True if successful, False otherwise
    """
    if not KEYRING_AVAILABLE:
        return False
    
    try:
        service = _get_keyring_service_name()
        username = _get_keyring_username(profile)
        keyring.delete_password(service, username)
        return True
    except Exception:
        return False


def list_keyring_profiles() -> List[str]:
    """List all profiles with keys stored in keyring.
    
    Returns:
        List of profile names
    """
    if not KEYRING_AVAILABLE:
        return []
    
    # This is tricky as keyring doesn't provide a list function
    # We'll try common profile names
    common_profiles = ["default", "dev", "development", "staging", "prod", "production", "test"]
    found_profiles = []
    
    service = _get_keyring_service_name()
    for profile in common_profiles:
        username = _get_keyring_username(profile)
        try:
            if keyring.get_password(service, username):
                found_profiles.append(profile)
        except Exception:
            continue
    
    return found_profiles


def _resolve_key(
    key: Optional[str] = None,
    profile: Optional[str] = None,
    key_env: str = "ENCRYPTED_ENV_KEY",
    use_keyring: bool = True
) -> str:
    """Resolve encryption key with priority: explicit > keyring > env var.
    
    Args:
        key: Explicit key (highest priority)
        profile: Profile name for keyring lookup
        key_env: Environment variable name
        use_keyring: Whether to try keyring lookup
        
    Returns:
        Resolved encryption key
        
    Raises:
        KeyError: If no key found
    """
    # 1. Explicit key parameter
    if key:
        return key
    
    # 2. Keyring (if enabled and available)
    if use_keyring:
        keyring_key = get_key_from_keyring(profile)
        if keyring_key:
            return keyring_key
    
    # 3. Environment variable
    env_key = os.getenv(key_env)
    if env_key:
        return env_key
    
    # 4. Error if none found
    sources = ["explicit parameter"]
    if use_keyring and KEYRING_AVAILABLE:
        sources.append("keyring")
    sources.append(f"environment variable {key_env}")
    
    raise KeyError(f"Encryption key not found in: {', '.join(sources)}") 