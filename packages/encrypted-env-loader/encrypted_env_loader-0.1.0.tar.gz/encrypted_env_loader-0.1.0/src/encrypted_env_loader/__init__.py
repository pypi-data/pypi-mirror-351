"""
Encrypted Environment Loader

A secure way to load and manage encrypted environment variables.
"""

__version__ = "0.1.0"
__author__ = "Isaac Harrison Gutekunst"

from .core import (
    load_encrypted_env,
    generate_key,
    encrypt_env_file,
    decrypt_env_file,
    validate_encrypted_file,
    encrypted_env_context,
    with_encrypted_env,
)

__all__ = [
    "load_encrypted_env",
    "generate_key", 
    "encrypt_env_file",
    "decrypt_env_file",
    "validate_encrypted_file",
    "encrypted_env_context",
    "with_encrypted_env",
] 