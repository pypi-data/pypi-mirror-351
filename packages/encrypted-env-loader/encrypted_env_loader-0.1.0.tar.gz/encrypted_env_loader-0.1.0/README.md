# Encrypted Environment Loader

A secure Python package for managing encrypted environment variables. Load sensitive configuration from encrypted `.env` files using Fernet encryption.

## Features

- **Secure encryption** using Fernet (AES 128 in CBC mode with HMAC-SHA256)
- **Profile support** for multiple environments (dev, prod, test, etc.)
- **CLI tools** for file management and subprocess execution
- **Python API** with context managers and decorators
- **Shell integration** for fish, bash, and zsh
- **Safe editing** with backup and validation
- **CI/CD friendly** with quiet modes and secret masking
- **Modern Python** with type hints and proper packaging

## Installation

```bash
pip install encrypted-env-loader
```

## Quick Start

### 1. Initialize a new encrypted environment file

```bash
# Generate new encrypted file with random key
encrypted-env init
# Output: Encryption key: gAAAAABh...
# Output: Set your encryption key: export ENCRYPTED_ENV_KEY='gAAAAABh...'

# Set the key in your shell
export ENCRYPTED_ENV_KEY='gAAAAABh...'
```

### 2. Edit your environment variables

```bash
# Opens decrypted content in $EDITOR, re-encrypts on save
encrypted-env edit
```

### 3. Run commands with encrypted environment

```bash
# Run any command with encrypted env loaded
encrypted-env run -- python app.py
encrypted-env run -- ./deploy.sh
```

## Security Features

### CI/CD Safe Operations
All commands support `--quiet` mode for CI environments and have secure defaults:

```bash
# Generate keys silently (CI-safe)
KEY=$(encrypted-env generate-key --quiet)

# Show variable names only (never exposes values)
encrypted-env show --names-only

# Validate files without output (exit codes only)
encrypted-env validate --quiet
```

### Secret Masking
By default, commands mask sensitive values:

```bash
# Safe - shows masked values
encrypted-env show
# Output: DATABASE_URL=***
#         API_KEY=***

# Requires explicit flag to show values
encrypted-env show --show-values  # WARNING: exposes secrets
```

## Examples and Testing

Run the comprehensive demo to see all features:

```bash
# Interactive demo with full output
./examples/demo.sh

# CI-friendly mode (no secrets exposed)
./examples/demo.sh --ci

# View usage examples
./examples/basic_usage.sh
```

## CLI Reference

### Core Operations

#### `run` - Execute commands with encrypted environment
```bash
encrypted-env run [--file FILE] [--profile PROFILE] -- <command>

# Examples
encrypted-env run -- python app.py
encrypted-env run --profile prod -- ./deploy.sh
encrypted-env run --file .env.custom.encrypted -- npm start
```

#### `load` - Generate shell commands to load environment
```bash
encrypted-env load [--file FILE] [--profile PROFILE] [--shell SHELL] [--quiet]

# Usage in fish shell
eval (encrypted-env load)
eval (encrypted-env load --profile dev)

# Usage in bash/zsh
eval $(encrypted-env load)
eval $(encrypted-env load --profile prod)
```

#### `clear` - Generate shell commands to clear environment
```bash
encrypted-env clear [--file FILE] [--profile PROFILE] [--shell SHELL] [--quiet]

# Usage
eval (encrypted-env clear)  # fish
eval $(encrypted-env clear)  # bash/zsh
```

### File Management

#### `init` - Create new encrypted environment file
```bash
encrypted-env init [--file FILE] [--profile PROFILE] [--key-file KEYFILE] [--quiet]

# Examples
encrypted-env init                           # creates .env.encrypted
encrypted-env init --profile dev             # creates .env.dev.encrypted  
encrypted-env init --key-file .env.key      # saves key to file
encrypted-env init --quiet                   # CI-friendly (key only)
```

#### `encrypt` - Encrypt existing .env file
```bash
encrypted-env encrypt <source> [--output OUTPUT] [--profile PROFILE] [--quiet]

# Examples
encrypted-env encrypt .env                   # creates .env.encrypted
encrypted-env encrypt .env.dev --profile dev  # creates .env.dev.encrypted
encrypted-env encrypt .env --output custom.encrypted
```

#### `decrypt` - Decrypt to filesystem
```bash
encrypted-env decrypt [--file FILE] [--output OUTPUT] [--profile PROFILE] [--quiet]

# Examples
encrypted-env decrypt                        # decrypts to .env
encrypted-env decrypt --profile dev         # decrypts .env.dev.encrypted to .env
encrypted-env decrypt --output .env.backup  # custom output file
```

#### `edit` - Safely edit encrypted files
```bash
encrypted-env edit [--file FILE] [--profile PROFILE] [--quiet]

# Opens in $EDITOR (vi by default)
# Creates backup before editing
# Validates .env format before re-encrypting
encrypted-env edit --profile prod
```

### Key Management

#### `generate-key` - Generate new encryption key
```bash
encrypted-env generate-key [--quiet]

# Interactive mode
encrypted-env generate-key
# Output: Generated key: gAAAAABh...

# CI mode
encrypted-env generate-key --quiet
# Output: gAAAAABh...
```

#### `rekey` - Change encryption key
```bash
encrypted-env rekey [--file FILE] [--profile PROFILE] [--old-key-env VAR] [--new-key-env VAR] [--quiet]

# Examples
ENCRYPTED_ENV_KEY="old_key" NEW_KEY="new_key" encrypted-env rekey --new-key-env NEW_KEY
encrypted-env rekey --quiet  # generates new random key silently
```

### Utilities

#### `status` - Show file information and variables
```bash
encrypted-env status [--file FILE] [--profile PROFILE]

# Example output:
# File: .env.encrypted
# Exists: True
# Size: 1024 bytes
# Key source: $ENCRYPTED_ENV_KEY  
# Status: Valid (contains 5 variables)
# Variables:
#   - DATABASE_URL
#   - SECRET_KEY
```

#### `validate` - Check if file can be decrypted
```bash
encrypted-env validate [--file FILE] [--profile PROFILE] [--quiet]
# Exit code 0 if valid, 1 if invalid
```

#### `show` - Display variables (with security options)
```bash
encrypted-env show [--file FILE] [--profile PROFILE] [--names-only] [--show-values]

# Safe default (masks values)
encrypted-env show
# Output: DATABASE_URL=***

# CI-safe (names only)
encrypted-env show --names-only
# Output: DATABASE_URL
#         API_KEY

# Explicit flag required to show values
encrypted-env show --show-values  # WARNING: exposes secrets
```

## Python API

### Basic Usage

```python
from encrypted_env_loader import load_encrypted_env

# Load with default settings (.env.encrypted, ENCRYPTED_ENV_KEY)
env_vars = load_encrypted_env()

# Load with specific parameters
env_vars = load_encrypted_env(
    key="base64-encoded-key",
    file_path=".env.prod.encrypted",
    profile="prod",
    change_os_env=True  # Updates os.environ
)
```

### Context Manager

```python
from encrypted_env_loader import encrypted_env_context
import os

with encrypted_env_context(profile="dev"):
    # Environment variables loaded here
    database_url = os.getenv("DATABASE_URL")
    secret_key = os.getenv("SECRET_KEY")
# Environment automatically restored when exiting context
```

### Decorator

```python
from encrypted_env_loader import with_encrypted_env
import os

@with_encrypted_env(profile="prod")
def deploy_application():
    # Function runs with encrypted env loaded
    api_key = os.getenv("API_KEY")
    database_url = os.getenv("DATABASE_URL")
    # Environment restored after function returns

deploy_application()
```

### Utility Functions

```python
from encrypted_env_loader import (
    generate_key,
    encrypt_env_file,
    decrypt_env_file,
    validate_encrypted_file
)

# Generate encryption key
key = generate_key()

# Encrypt a file
encrypt_env_file(".env", ".env.encrypted", key)

# Decrypt and get variables
env_vars = decrypt_env_file(".env.encrypted", key=key)

# Validate file
is_valid = validate_encrypted_file(".env.encrypted", key=key)
```

## Profiles

Profiles allow managing multiple environment configurations:

```bash
# Profile-based file naming
.env.encrypted          # default profile
.env.dev.encrypted      # dev profile  
.env.prod.encrypted     # prod profile
.env.test.encrypted     # test profile

# Usage
encrypted-env init --profile dev
encrypted-env run --profile prod -- python app.py
encrypted-env edit --profile test
```

## Shell Integration

### Fish Shell
```fish
# Load environment
eval (encrypted-env load --profile dev)

# Clear environment  
eval (encrypted-env clear --profile dev)

# One-liner with auto-clear
encrypted-env run --profile dev -- python app.py
```

### Bash/Zsh
```bash
# Load environment
eval $(encrypted-env load --profile dev)

# Clear environment
eval $(encrypted-env clear --profile dev)

# Use in loops (eval once, use many times)
eval $(encrypted-env load)
for i in {1..100}; do
    curl -H "Authorization: $SECRET_TOKEN" api.example.com/data/$i
done
eval $(encrypted-env clear)
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Setup encrypted environment
  run: |
    # Generate or retrieve key securely
    echo "${{ secrets.ENCRYPTED_ENV_KEY }}" > .env.key
    export ENCRYPTED_ENV_KEY=$(cat .env.key)
    
    # Validate encrypted file
    encrypted-env validate --quiet
    
    # Run tests with encrypted environment
    encrypted-env run -- pytest
```

### Security Best Practices
```bash
# Never expose secrets in CI logs
encrypted-env show --names-only          # ✅ Safe
encrypted-env validate --quiet           # ✅ Safe  
encrypted-env generate-key --quiet       # ✅ Safe

# Avoid these in CI
encrypted-env show --show-values         # ❌ Exposes secrets
encrypted-env status                     # ❌ May expose info
```

## Security Considerations

- **Key Storage**: Never commit encryption keys to version control
- **Key Rotation**: Regularly rotate encryption keys using `rekey` command
- **File Permissions**: Ensure encrypted files have appropriate permissions
- **Backup Strategy**: Keep secure backups of both encrypted files and keys
- **Environment Isolation**: Use profiles to separate dev/staging/prod secrets
- **CI/CD Safety**: Use `--quiet` and `--names-only` flags in automated environments

## Error Handling

The package provides specific exception types:

```python
from encrypted_env_loader import EncryptedEnvError, DecryptionError, KeyError

try:
    load_encrypted_env()
except KeyError:
    print("Encryption key missing or invalid")
except DecryptionError:
    print("File cannot be decrypted - wrong key or corrupted data")
except EncryptedEnvError:
    print("General error with encrypted environment operations")
```

## Development

### Setup
```bash
git clone https://github.com/igutekunst/encrypted-env-loader
cd encrypted-env-loader
pip install -e ".[dev]"
```

### Testing
```bash
# Run unit tests
pytest

# Run full demo/integration tests
./examples/demo.sh

# Run CI-safe tests
./examples/demo.sh --ci

# Test coverage
pytest --cov=encrypted_env_loader
```

### Code Quality
```bash
black src tests
isort src tests  
flake8 src tests
mypy src
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Changelog

### 0.1.0
- Initial release
- Basic encryption/decryption functionality
- CLI with all core commands
- Python API with context managers and decorators
- Profile support
- Shell integration
- CI/CD safety features with quiet modes and secret masking 