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
    get_key_from_keyring,
    set_key_in_keyring,
    delete_key_from_keyring,
    list_keyring_profiles,
    get_git_repo_name,
    KEYRING_AVAILABLE,
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
@click.argument("command", nargs=-1, required=True)
def run(
    file_path: Optional[str],
    profile: Optional[str], 
    key_env: str,
    no_keyring: bool,
    command: tuple
) -> None:
    """Run command with encrypted environment variables loaded."""
    try:
        # Load encrypted environment
        env_vars = load_encrypted_env(
            file_path=file_path,
            profile=profile,
            change_os_env=False,
            key_env=key_env,
            use_keyring=not no_keyring
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def load(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    shell: str,
    quiet: bool,
    no_keyring: bool
) -> None:
    """Generate shell commands to load encrypted environment variables."""
    try:
        env_vars = load_encrypted_env(
            file_path=file_path,
            profile=profile,
            change_os_env=False,
            key_env=key_env,
            use_keyring=not no_keyring
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def clear(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    shell: str,
    quiet: bool,
    no_keyring: bool
) -> None:
    """Generate shell commands to clear encrypted environment variables."""
    try:
        env_vars = load_encrypted_env(
            file_path=file_path,
            profile=profile,
            change_os_env=False,
            key_env=key_env,
            use_keyring=not no_keyring
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def encrypt(
    source_file: str,
    output: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool,
    no_keyring: bool
) -> None:
    """Encrypt an existing .env file."""
    try:
        if output is None:
            output = str(_resolve_file_path(None, profile))
        
        encrypt_env_file(source_file, output, key_env=key_env, profile=profile, use_keyring=not no_keyring)
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def decrypt(
    file_path: Optional[str],
    output: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool,
    no_keyring: bool
) -> None:
    """Decrypt encrypted env file to filesystem."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        if output is None:
            # Default to .env in current directory
            output = ".env"
        
        decrypt_env_file(resolved_path, output, key_env=key_env, profile=profile, use_keyring=not no_keyring)
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
    "--shell",
    default="auto",
    help="Shell type (fish, bash, auto)"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def edit(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool,
    no_keyring: bool
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
            env_vars = decrypt_env_file(resolved_path, tmp.name, key_env=key_env, profile=profile, use_keyring=not no_keyring)
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
            encrypt_env_file(tmp_path, resolved_path, key_env=key_env, profile=profile, use_keyring=not no_keyring)
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def rekey(
    file_path: Optional[str],
    profile: Optional[str],
    old_key_env: str,
    new_key_env: Optional[str],
    quiet: bool,
    no_keyring: bool
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
        env_vars = decrypt_env_file(resolved_path, key_env=old_key_env, profile=profile, use_keyring=not no_keyring)
        
        # Create temporary file with decrypted content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            for key, value in env_vars.items():
                tmp.write(f"{key}={value}\n")
            tmp.flush()
            
            try:
                # Re-encrypt with new key
                encrypt_env_file(tmp.name, resolved_path, new_key, profile=profile, use_keyring=False)
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def status(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    no_keyring: bool
) -> None:
    """Show status and information about encrypted environment file."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        click.echo(f"File: {resolved_path}")
        click.echo(f"Exists: {resolved_path.exists()}")
        
        if resolved_path.exists():
            click.echo(f"Size: {resolved_path.stat().st_size} bytes")
            
            # Check if we can decrypt
            key = os.getenv(key_env) if no_keyring else None
            keyring_key = get_key_from_keyring(profile) if not no_keyring else None
            
            if keyring_key and not no_keyring:
                click.echo(f"Key source: keyring (profile: {profile or 'default'})")
                if validate_encrypted_file(resolved_path, profile=profile, use_keyring=True):
                    env_vars = decrypt_env_file(resolved_path, profile=profile, use_keyring=True)
                    click.echo(f"Status: Valid (contains {len(env_vars)} variables)")
                    
                    # Show variable names (not values)
                    if env_vars:
                        click.echo("Variables:")
                        for var_name in sorted(env_vars.keys()):
                            click.echo(f"  - {var_name}")
                else:
                    click.echo("Status: Invalid (cannot decrypt)")
            elif key:
                click.echo(f"Key source: ${key_env}")
                if validate_encrypted_file(resolved_path, key=key, use_keyring=False):
                    env_vars = decrypt_env_file(resolved_path, key=key, use_keyring=False)
                    click.echo(f"Status: Valid (contains {len(env_vars)} variables)")
                    
                    # Show variable names (not values)
                    if env_vars:
                        click.echo("Variables:")
                        for var_name in sorted(env_vars.keys()):
                            click.echo(f"  - {var_name}")
                else:
                    click.echo("Status: Invalid (cannot decrypt)")
            else:
                sources = []
                if not no_keyring:
                    sources.append("keyring")
                sources.append(f"${key_env}")
                click.echo(f"Key source: {' or '.join(sources)} (not found)")
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def validate(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    quiet: bool,
    no_keyring: bool
) -> None:
    """Validate that encrypted file can be decrypted."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        
        if validate_encrypted_file(resolved_path, key_env=key_env, profile=profile, use_keyring=not no_keyring):
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
@click.option(
    "--no-keyring",
    is_flag=True,
    help="Skip keyring lookup, use only environment variables"
)
def show(
    file_path: Optional[str],
    profile: Optional[str],
    key_env: str,
    show_values: bool,
    names_only: bool,
    no_keyring: bool
) -> None:
    """Show variables in encrypted file without loading them."""
    try:
        resolved_path = _resolve_file_path(file_path, profile)
        env_vars = decrypt_env_file(resolved_path, key_env=key_env, profile=profile, use_keyring=not no_keyring)
        
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


@main.group()
def keyring() -> None:
    """Manage encryption keys in system keyring."""
    if not KEYRING_AVAILABLE:
        click.echo("Error: keyring package not available", err=True)
        sys.exit(1)


@keyring.command("set-key")
@click.option(
    "--profile",
    help="Profile name (default: 'default')"
)
@click.option(
    "--key",
    help="Encryption key (if not provided, will be generated)"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Only output the key, no additional messages (CI-friendly)"
)
def keyring_set_key(
    profile: Optional[str],
    key: Optional[str],
    quiet: bool
) -> None:
    """Store encryption key in system keyring."""
    try:
        if key is None:
            key = generate_key()
            if not quiet:
                click.echo(f"Generated new key: {key}")
        
        if set_key_in_keyring(key, profile):
            profile_name = profile or "default"
            if not quiet:
                click.echo(f"Key stored in keyring for profile: {profile_name}")
                click.echo(f"Service: {get_git_repo_name()}")
            if quiet:
                click.echo(key)
        else:
            click.echo("Error: Failed to store key in keyring", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@keyring.command("get-key")
@click.option(
    "--profile",
    help="Profile name (default: 'default')"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Only output the key, no additional messages (CI-friendly)"
)
def keyring_get_key(
    profile: Optional[str],
    quiet: bool
) -> None:
    """Retrieve encryption key from system keyring."""
    try:
        key = get_key_from_keyring(profile)
        if key:
            if quiet:
                click.echo(key)
            else:
                profile_name = profile or "default"
                click.echo(f"Key for profile '{profile_name}': {key}")
        else:
            profile_name = profile or "default"
            if not quiet:
                click.echo(f"No key found for profile: {profile_name}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@keyring.command("delete-key")
@click.option(
    "--profile",
    help="Profile name (default: 'default')"
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress informational output (CI-friendly)"
)
def keyring_delete_key(
    profile: Optional[str],
    quiet: bool
) -> None:
    """Delete encryption key from system keyring."""
    try:
        profile_name = profile or "default"
        if not quiet:
            if not click.confirm(f"Delete key for profile '{profile_name}'?"):
                click.echo("Aborted.")
                return
        
        if delete_key_from_keyring(profile):
            if not quiet:
                click.echo(f"Key deleted for profile: {profile_name}")
        else:
            if not quiet:
                click.echo(f"No key found for profile: {profile_name}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@keyring.command("list-keys")
@click.option(
    "--quiet",
    is_flag=True,
    help="Only show profile names, no additional messages (CI-friendly)"
)
def keyring_list_keys(quiet: bool) -> None:
    """List all profiles with keys stored in keyring."""
    try:
        profiles = list_keyring_profiles()
        if profiles:
            if not quiet:
                click.echo(f"Found keys for {len(profiles)} profiles:")
            for profile in profiles:
                if quiet:
                    click.echo(profile)
                else:
                    click.echo(f"  - {profile}")
        else:
            if not quiet:
                click.echo("No keys found in keyring.")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 