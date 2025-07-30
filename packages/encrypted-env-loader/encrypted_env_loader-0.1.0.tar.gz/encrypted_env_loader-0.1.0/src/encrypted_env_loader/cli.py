"""
Command-line interface for encrypted environment loader.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, List

import click

from .core import (
    generate_key,
    encrypt_env_file, 
    decrypt_env_file,
    load_encrypted_env,
    validate_encrypted_file,
    _resolve_file_path,
    EncryptedEnvError,
    DecryptionError,
    KeyError,
)


def _get_shell_export_commands(env_vars: Dict[str, str], shell: str = "auto") -> List[str]:
    """Generate shell commands to export environment variables.
    
    Args:
        env_vars: Dictionary of environment variables
        shell: Shell type ('fish', 'bash', 'auto')
        
    Returns:
        List of shell commands
    """
    if shell == "auto":
        shell = os.path.basename(os.getenv("SHELL", "bash"))
    
    commands = []
    for key, value in env_vars.items():
        # Escape single quotes in values
        escaped_value = value.replace("'", "'\"'\"'")
        
        if shell == "fish":
            commands.append(f"set -gx {key} '{escaped_value}'")
        else:  # bash, zsh, etc.
            commands.append(f"export {key}='{escaped_value}'")
    
    return commands


def _get_shell_clear_commands(env_vars: Dict[str, str], shell: str = "auto") -> List[str]:
    """Generate shell commands to clear environment variables.
    
    Args:
        env_vars: Dictionary of environment variables to clear
        shell: Shell type ('fish', 'bash', 'auto')
        
    Returns:
        List of shell commands
    """
    if shell == "auto":
        shell = os.path.basename(os.getenv("SHELL", "bash"))
    
    commands = []
    for key in env_vars.keys():
        if shell == "fish":
            commands.append(f"set -e {key}")
        else:  # bash, zsh, etc.
            commands.append(f"unset {key}")
    
    return commands


@click.group()
@click.version_option(version="0.1.0")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Securely load and manage encrypted environment variables."""
    ctx.ensure_object(dict)


@main.command()
@click.option(
    "--file", 
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.argument("command", nargs=-1, required=True)
def run(
    file_path: Optional[str],
    profile: Optional[str], 
    key_env: str,
    command: tuple
) -> None:
    """Run command with encrypted environment variables loaded."""
    try:
        # Load encrypted environment
        env_vars = load_encrypted_env(
            file_path=file_path,
            profile=profile,
            change_os_env=False,
            key_env=key_env
        )
        
        # Merge with current environment
        new_env = os.environ.copy()
        new_env.update(env_vars)
        
        # Run command with merged environment
        result = subprocess.run(list(command), env=new_env)
        sys.exit(result.returncode)
        
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path", 
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--shell",
    default="auto",
    help="Shell type (fish, bash, auto)"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
def load(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    shell: str,
    quiet: bool
) -> None:
    """Generate shell commands to load encrypted environment variables."""
    try:
        env_vars = load_encrypted_env(
            file_path=file_path,
            profile=profile,
            change_os_env=False,
            key_env=key_env
        )
        
        commands = _get_shell_export_commands(env_vars, shell)
        for command in commands:
            click.echo(command)
            
        if not quiet:
            click.echo(f"# Loaded {len(env_vars)} environment variables", err=True)
            
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        if not quiet:
            click.echo(f"echo 'Error: {e}'; exit 1", err=True)
        else:
            click.echo(f"echo 'Error loading environment'; exit 1", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile", 
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--shell",
    default="auto",
    help="Shell type (fish, bash, auto)"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
def clear(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    shell: str,
    quiet: bool
) -> None:
    """Generate shell commands to clear encrypted environment variables."""
    try:
        env_vars = load_encrypted_env(
            file_path=file_path,
            profile=profile,
            change_os_env=False,
            key_env=key_env
        )
        
        commands = _get_shell_clear_commands(env_vars, shell)
        for command in commands:
            click.echo(command)
            
        if not quiet:
            click.echo(f"# Cleared {len(env_vars)} environment variables", err=True)
            
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        if not quiet:
            click.echo(f"echo 'Error: {e}'; exit 1", err=True)
        else:
            click.echo(f"echo 'Error clearing environment'; exit 1", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path for encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-file",
    help="Path to write generated key file"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY", 
    help="Environment variable to store encryption key"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Only output the key, no additional messages (CI-friendly)"
)
def init(
    file_path: Optional[str],
    profile: Optional[str],
    key_file: Optional[str],
    key_env: str,
    quiet: bool
) -> None:
    """Initialize new encrypted environment file with random key."""
    try:
        # Generate new key
        key = generate_key()
        
        # Resolve file path
        resolved_path = _resolve_file_path(file_path, profile)
        
        # Check if file already exists
        if resolved_path.exists() and not quiet:
            if not click.confirm(f"File {resolved_path} already exists. Overwrite?"):
                click.echo("Aborted.")
                return
        
        # Create empty encrypted file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("# Add your environment variables here\n")
            tmp.flush()
            
            try:
                encrypt_env_file(tmp.name, resolved_path, key)
            finally:
                os.unlink(tmp.name)
        
        # Write key to file if requested
        if key_file:
            Path(key_file).write_text(key)
            if not quiet:
                click.echo(f"Encryption key written to: {key_file}")
        
        if quiet:
            # Only output the key for CI/scripting
            click.echo(key)
        else:
            click.echo(f"Encryption key: {key}")
            click.echo(f"Encrypted environment file created: {resolved_path}")
            click.echo(f"Set your encryption key: export {key_env}='{key}'")
        
    except EncryptedEnvError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("source_file")
@click.option(
    "--output",
    help="Output path for encrypted file"
)
@click.option(
    "--profile",
    help="Profile name (affects default output path)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
def encrypt(
    source_file: str,
    output: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool
) -> None:
    """Encrypt an existing .env file."""
    try:
        if output is None:
            output = str(_resolve_file_path(None, profile))
        
        encrypt_env_file(source_file, output, key_env=key_env)
        if not quiet:
            click.echo(f"Encrypted {source_file} -> {output}")
        
    except (EncryptedEnvError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--output",
    help="Output path for decrypted file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
def decrypt(
    file_path: Optional[str],
    output: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool
) -> None:
    """Decrypt encrypted env file to filesystem."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        if output is None:
            # Default to .env in current directory
            output = ".env"
        
        decrypt_env_file(resolved_path, output, key_env=key_env)
        if not quiet:
            click.echo(f"Decrypted {resolved_path} -> {output}")
        
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
def edit(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool
) -> None:
    """Edit encrypted environment file."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        if not resolved_path.exists():
            click.echo(f"Error: File not found: {resolved_path}", err=True)
            sys.exit(1)
        
        # Get editor
        editor = os.getenv("EDITOR", "vi")
        
        # Create backup
        backup_path = resolved_path.with_suffix(resolved_path.suffix + ".backup")
        import shutil
        shutil.copy2(resolved_path, backup_path)
        if not quiet:
            click.echo(f"Backup created: {backup_path}")
        
        # Decrypt to temporary file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.env', delete=False) as tmp:
            env_vars = decrypt_env_file(resolved_path, tmp.name, key_env=key_env)
            tmp_path = tmp.name
        
        try:
            # Open in editor
            result = subprocess.run([editor, tmp_path])
            
            if result.returncode != 0:
                click.echo("Editor exited with error, not saving changes.", err=True)
                return
            
            # Validate the edited file
            try:
                from dotenv import dotenv_values
                dotenv_values(tmp_path)
            except Exception as e:
                click.echo(f"Error: Invalid .env format: {e}", err=True)
                if not quiet and not click.confirm("Save anyway?"):
                    return
            
            # Re-encrypt
            encrypt_env_file(tmp_path, resolved_path, key_env=key_env)
            if not quiet:
                click.echo(f"Encrypted file updated: {resolved_path}")
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command(name="generate-key")
@click.option(
    "--quiet",
    is_flag=True,
    help="Only output the key, no additional messages (CI-friendly)"
)
def generate_key_cmd(quiet: bool) -> None:
    """Generate a new encryption key."""
    key = generate_key()
    if quiet:
        click.echo(key)
    else:
        click.echo(f"Generated key: {key}")


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--old-key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing old encryption key"
)
@click.option(
    "--new-key-env", 
    help="Environment variable containing new encryption key"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Only output the new key if generated, no additional messages (CI-friendly)"
)
def rekey(
    file_path: Optional[str],
    profile: Optional[str],
    old_key_env: str,
    new_key_env: Optional[str],
    quiet: bool
) -> None:
    """Change encryption key for existing file."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        if not resolved_path.exists():
            click.echo(f"Error: File not found: {resolved_path}", err=True)
            sys.exit(1)
        
        # Get new key
        if new_key_env:
            new_key = os.getenv(new_key_env)
            if not new_key:
                click.echo(f"Error: New key not found in {new_key_env}", err=True)
                sys.exit(1)
        else:
            new_key = generate_key()
            if quiet:
                click.echo(new_key)
            else:
                click.echo(f"Generated new key: {new_key}")
        
        # Decrypt with old key
        env_vars = decrypt_env_file(resolved_path, key_env=old_key_env)
        
        # Create temporary file with decrypted content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            for key, value in env_vars.items():
                tmp.write(f"{key}={value}\n")
            tmp.flush()
            
            try:
                # Re-encrypt with new key
                encrypt_env_file(tmp.name, resolved_path, new_key)
                if not quiet:
                    click.echo(f"File re-encrypted with new key: {resolved_path}")
            finally:
                os.unlink(tmp.name)
        
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
def status(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str
) -> None:
    """Show status and information about encrypted environment file."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        click.echo(f"File: {resolved_path}")
        click.echo(f"Exists: {resolved_path.exists()}")
        
        if resolved_path.exists():
            click.echo(f"Size: {resolved_path.stat().st_size} bytes")
            
            # Check if we can decrypt
            key = os.getenv(key_env)
            if key:
                click.echo(f"Key source: ${key_env}")
                if validate_encrypted_file(resolved_path, key):
                    env_vars = decrypt_env_file(resolved_path, key_env=key_env)
                    click.echo(f"Status: Valid (contains {len(env_vars)} variables)")
                    
                    # Show variable names (not values)
                    if env_vars:
                        click.echo("Variables:")
                        for var_name in sorted(env_vars.keys()):
                            click.echo(f"  - {var_name}")
                else:
                    click.echo("Status: Invalid (cannot decrypt)")
            else:
                click.echo(f"Key source: ${key_env} (not set)")
                click.echo("Status: Cannot validate (no key)")
        
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Only show validation result (CI-friendly)"
)
def validate(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool
) -> None:
    """Validate that encrypted file can be decrypted."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        if validate_encrypted_file(resolved_path, key_env=key_env):
            if not quiet:
                click.echo(f"✓ Valid: {resolved_path}")
        else:
            if not quiet:
                click.echo(f"✗ Invalid: {resolved_path}")
            sys.exit(1)
            
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        if not quiet:
            click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--file",
    "file_path",
    help="Path to encrypted env file"
)
@click.option(
    "--profile",
    help="Profile name (affects default file selection)"
)
@click.option(
    "--key-env",
    default="ENCRYPTED_ENV_KEY",
    help="Environment variable containing encryption key"
)
@click.option(
    "--show-values",
    is_flag=True,
    help="Show variable values (WARNING: exposes secrets)"
)
@click.option(
    "--names-only",
    is_flag=True,
    help="Show only variable names, not values (CI-friendly)"
)
def show(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    show_values: bool,
    names_only: bool
) -> None:
    """Show variables in encrypted file without loading them."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        env_vars = decrypt_env_file(resolved_path, key_env=key_env)
        
        if not env_vars:
            click.echo("No variables found.")
            return
        
        if names_only:
            # Only show variable names (CI-safe)
            for key in sorted(env_vars.keys()):
                click.echo(key)
        elif show_values:
            # Show full key=value (requires explicit flag)
            for key, value in sorted(env_vars.items()):
                click.echo(f"{key}={value}")
        else:
            # Default: show names with masked values
            for key in sorted(env_vars.keys()):
                click.echo(f"{key}=***")
            
    except (EncryptedEnvError, DecryptionError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 