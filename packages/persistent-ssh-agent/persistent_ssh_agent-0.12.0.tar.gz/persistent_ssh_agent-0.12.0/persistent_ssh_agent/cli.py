"""Command-line interface for persistent-ssh-agent."""

# Import built-in modules
import base64
import getpass
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

# Import third-party modules
import click
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from loguru import logger
from persistent_ssh_agent import PersistentSSHAgent
from persistent_ssh_agent.config import SSHConfig
from persistent_ssh_agent.constants import CLIConstants
from persistent_ssh_agent.constants import LoggingConstants
from persistent_ssh_agent.constants import SystemConstants
from persistent_ssh_agent.utils import run_command


# Logger will be configured dynamically in main() based on --debug flag


class Args:
    """Simple class to mimic argparse namespace for compatibility with existing functions."""

    def __init__(self, **kwargs):
        """Initialize with keyword arguments.

        Args:
            **kwargs: Attributes to set on the instance
        """
        for key, value in kwargs.items():
            setattr(self, key, value)


class ConfigManager:
    """Manages persistent configuration for SSH agent."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / CLIConstants.CONFIG_DIR_NAME
        self.config_file = self.config_dir / CLIConstants.CONFIG_FILE_NAME
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # Set proper permissions for config directory
        if os.name != SystemConstants.WINDOWS_PLATFORM:  # Skip on Windows
            os.chmod(self.config_dir, CLIConstants.CONFIG_DIR_PERMISSIONS)

    def load_config(self) -> Dict:
        """Load configuration from file.

        Returns:
            Dict: Configuration dictionary
        """
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file, "r", encoding=SystemConstants.DEFAULT_ENCODING) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}

    def save_config(self, config: Dict) -> bool:
        """Save configuration to file.

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if successful
        """
        try:
            with open(self.config_file, "w", encoding=SystemConstants.DEFAULT_ENCODING) as f:
                json.dump(config, f, indent=2)

            # Set proper permissions for config file
            if os.name != SystemConstants.WINDOWS_PLATFORM:  # Skip on Windows
                os.chmod(self.config_file, CLIConstants.CONFIG_FILE_PERMISSIONS)

            return True
        except IOError as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def _get_config_value(self, key: str) -> Optional[Any]:
        """Get a value from the configuration.

        Args:
            key: Configuration key

        Returns:
            Optional[Any]: Configuration value or None
        """
        config = self.load_config()
        return config.get(key)

    def _set_config_value(self, key: str, value: Any) -> bool:
        """Set a value in the configuration.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            bool: True if successful
        """
        config = self.load_config()
        config[key] = value
        return self.save_config(config)

    def get_passphrase(self) -> Optional[str]:
        """Get stored passphrase.

        Returns:
            Optional[str]: Stored passphrase or None
        """
        return self._get_config_value("passphrase")

    def set_passphrase(self, passphrase: str) -> bool:
        """Set and store passphrase.

        Args:
            passphrase: SSH key passphrase

        Returns:
            bool: True if successful
        """
        # Use AES-256 encryption
        encrypted = self._encrypt_passphrase(passphrase)
        return self._set_config_value("passphrase", encrypted)

    def get_identity_file(self) -> Optional[str]:
        """Get stored identity file path.

        Returns:
            Optional[str]: Stored identity file path or None
        """
        return self._get_config_value("identity_file")

    def set_identity_file(self, identity_file: str) -> bool:
        """Set and store identity file path.

        Args:
            identity_file: Path to SSH identity file

        Returns:
            bool: True if successful
        """
        expanded_path = os.path.expanduser(identity_file)
        return self._set_config_value("identity_file", expanded_path)

    def get_expiration_time(self) -> Optional[int]:
        """Get stored expiration time.

        Returns:
            Optional[int]: Expiration time in seconds or None
        """
        return self._get_config_value("expiration_time")

    def set_expiration_time(self, hours: int) -> bool:
        """Set and store expiration time.

        Args:
            hours: Expiration time in hours

        Returns:
            bool: True if successful
        """
        seconds = hours * CLIConstants.SECONDS_PER_HOUR  # Convert to seconds
        return self._set_config_value(CLIConstants.CONFIG_KEY_EXPIRATION_TIME, seconds)

    def get_reuse_agent(self) -> Optional[bool]:
        """Get stored reuse agent setting.

        Returns:
            Optional[bool]: Reuse agent setting or None
        """
        return self._get_config_value("reuse_agent")

    def set_reuse_agent(self, reuse: bool) -> bool:
        """Set and store reuse agent setting.

        Args:
            reuse: Whether to reuse existing SSH agent

        Returns:
            bool: True if successful
        """
        return self._set_config_value("reuse_agent", reuse)

    def list_keys(self) -> Dict:
        """List all configured SSH keys.

        Returns:
            Dict: Dictionary of configured keys
        """
        config = self.load_config()
        result = {}

        # Add default key if exists
        identity_file = config.get("identity_file")
        if identity_file:
            result["default"] = identity_file

        # Add named keys if exist
        keys = config.get("keys", {})
        if isinstance(keys, dict):
            result.update(keys)

        return result

    def add_key(self, name: str, identity_file: str) -> bool:
        """Add a named SSH key.

        Args:
            name: Name of the key
            identity_file: Path to SSH identity file

        Returns:
            bool: True if successful
        """
        config = self.load_config()

        # Handle default key
        if name == "default":
            return self.set_identity_file(identity_file)

        # Handle named keys
        if "keys" not in config:
            config["keys"] = {}

        config["keys"][name] = os.path.expanduser(identity_file)
        return self.save_config(config)

    def remove_key(self, name: str) -> bool:
        """Remove a named SSH key.

        Args:
            name: Name of the key

        Returns:
            bool: True if successful
        """
        config = self.load_config()
        updated = False

        # Handle default key
        if name == "default" and "identity_file" in config:
            config.pop("identity_file")
            updated = True

        # Handle named keys
        elif "keys" in config and name in config["keys"]:
            config["keys"].pop(name)
            updated = True

            # Clean up empty keys dictionary
            if not config["keys"]:
                config.pop("keys")

        return self.save_config(config) if updated else False

    def clear_config(self) -> bool:
        """Clear all configuration.

        Returns:
            bool: True if successful
        """
        return self.save_config({})

    def export_config(self, include_sensitive: bool = False) -> Dict:
        """Export configuration.

        Args:
            include_sensitive: Whether to include sensitive information

        Returns:
            Dict: Exported configuration
        """
        config = self.load_config()
        export = {}

        # Define non-sensitive keys
        non_sensitive_keys = ["identity_file", "keys", "expiration_time", "reuse_agent"]

        # Copy non-sensitive keys
        for key in non_sensitive_keys:
            if key in config:
                export[key] = config[key]

        # Include sensitive information if requested
        if include_sensitive and "passphrase" in config:
            export["passphrase"] = config["passphrase"]

        return export

    def import_config(self, config_data: Dict) -> bool:
        """Import configuration.

        Args:
            config_data: Configuration data to import

        Returns:
            bool: True if successful
        """
        # Validate input data
        if not isinstance(config_data, dict):
            logger.error("Invalid configuration data: not a dictionary")
            return False

        # Get current configuration
        current_config = self.load_config()

        # Update current configuration with imported data
        current_config.update(config_data)

        return self.save_config(current_config)

    def _derive_key_from_system(self) -> Tuple[bytes, bytes]:
        """Derive encryption key from system-specific information.

        Returns:
            Tuple[bytes, bytes]: (key, salt)
        """
        # Get system-specific information
        try:
            # Get username with fallbacks for CI environments
            username = self._get_username()

            # Get system information
            system_info = {
                "hostname": socket.gethostname(),
                "machine_id": self._get_machine_id(),
                "username": username,
                "home": str(Path.home()),
            }
        except Exception as e:
            # If all else fails, use a default set of values
            logger.warning(f"Failed to get system info: {e}, using fallback values")
            system_info = {
                "hostname": SystemConstants.UNKNOWN_HOST,
                "machine_id": SystemConstants.UNKNOWN_MACHINE,
                "username": SystemConstants.UNKNOWN_USER,
                "home": SystemConstants.UNKNOWN_HOME,
            }

        # Create a deterministic salt from system info
        salt_base = f"{system_info['hostname']}:{system_info['machine_id']}:{system_info['username']}"
        salt = hashlib.sha256(salt_base.encode()).digest()[:CLIConstants.SALT_SIZE]

        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=CLIConstants.KEY_SIZE,
            salt=salt,
            iterations=CLIConstants.KEY_DERIVATION_ITERATIONS,
            backend=default_backend()
        )

        # Use a combination of system info as the password
        password = f"{system_info['hostname']}:{system_info['machine_id']}:{system_info['home']}"
        key = kdf.derive(password.encode())

        return key, salt

    def _get_username(self) -> str:
        """Get current username with fallbacks for CI environments.

        Returns:
            str: Username
        """
        try:
            return os.getlogin()
        except (AttributeError, OSError):
            try:
                return getpass.getuser()
            except Exception:
                # Last resort fallback for CI environments
                user = os.environ.get(SystemConstants.ENV_USER, "")
                return user or os.environ.get(SystemConstants.ENV_USERNAME, SystemConstants.UNKNOWN_USER)

    def _get_machine_id(self) -> str:
        """Get a unique machine identifier.

        Returns:
            str: Machine ID
        """
        # Try to get machine ID from common locations
        machine_id = ""

        # Linux
        if os.path.exists(SystemConstants.LINUX_MACHINE_ID_PATH):
            try:
                with open(SystemConstants.LINUX_MACHINE_ID_PATH, "r", encoding=SystemConstants.DEFAULT_ENCODING) as f:
                    machine_id = f.read().strip()
            except (IOError, OSError):
                pass

        # Windows
        elif os.name == SystemConstants.WINDOWS_PLATFORM:
            try:
                # Import built-in modules
                import winreg

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, SystemConstants.WINDOWS_MACHINE_GUID_REGISTRY_PATH) as key:
                    machine_id = winreg.QueryValueEx(key, SystemConstants.WINDOWS_MACHINE_GUID_KEY)[0]
            except (ImportError, OSError):
                pass

        # Fallback to a hash of the hostname if we couldn't get a machine ID
        if not machine_id:
            machine_id = hashlib.sha256(socket.gethostname().encode()).hexdigest()

        return machine_id

    def _encrypt_passphrase(self, passphrase: str) -> str:
        """Encrypt passphrase using AES-256.

        Args:
            passphrase: Plain text passphrase

        Returns:
            str: Encrypted passphrase
        """
        try:
            # Get key and salt
            key, salt = self._derive_key_from_system()

            # Generate a random IV
            iv = os.urandom(CLIConstants.IV_SIZE)

            # Create an encryptor
            cipher = Cipher(AES(key), CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Pad the plaintext to a multiple of 16 bytes (AES block size)
            plaintext = self._pad_data(passphrase.encode())

            # Encrypt the padded plaintext
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()

            # Combine salt, IV, and ciphertext
            encrypted_data = salt + iv + ciphertext

            # Encode as base64 for storage
            return base64.b64encode(encrypted_data).decode()

        except Exception as e:
            logger.error(f"Failed to encrypt passphrase: {e}")
            raise

    def _pad_data(self, data: bytes) -> bytes:
        """Pad data to a multiple of 16 bytes (AES block size) using PKCS7 padding.

        Args:
            data: Data to pad

        Returns:
            bytes: Padded data
        """
        padding_length = CLIConstants.AES_BLOCK_SIZE - (len(data) % CLIConstants.AES_BLOCK_SIZE)
        return data + bytes([padding_length]) * padding_length

    def _unpad_data(self, padded_data: bytes) -> bytes:
        """Remove PKCS7 padding from data.

        Args:
            padded_data: Padded data

        Returns:
            bytes: Unpadded data
        """
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]

    def deobfuscate_passphrase(self, encrypted_data: str) -> str:
        """Decrypt passphrase.

        Args:
            encrypted_data: Encrypted passphrase

        Returns:
            str: Plain text passphrase
        """
        try:
            # Decode base64 data
            data = base64.b64decode(encrypted_data)

            # Extract IV and ciphertext (salt is not used as we get it from _derive_key_from_system)
            iv = data[CLIConstants.SALT_SIZE : CLIConstants.SALT_SIZE + CLIConstants.IV_SIZE]
            ciphertext = data[CLIConstants.SALT_SIZE + CLIConstants.IV_SIZE :]

            # Get key using the same method as encryption
            key, _ = self._derive_key_from_system()

            # Create a decryptor
            cipher = Cipher(AES(key), CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt the ciphertext
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding
            plaintext = self._unpad_data(padded_plaintext)

            return plaintext.decode()

        except Exception as e:
            logger.error(f"Failed to decrypt passphrase: {e}")
            raise

    @staticmethod
    def secure_delete_from_memory(data: Union[str, bytes, bytearray]) -> None:
        """Securely delete sensitive data from memory.

        Args:
            data: Data to delete
        """
        if isinstance(data, str):
            # For strings, we can't modify the bytes directly
            # This is a best-effort approach
            data = "0" * len(data)
            return

        if isinstance(data, bytearray):
            # For bytearrays, we can modify in place
            for i, _ in enumerate(data):
                data[i] = 0
            return

        # For bytes, we can't modify (immutable), but we can try to
        # encourage garbage collection by removing references
        if isinstance(data, bytes):
            del data


def setup_config(args):
    """Set up configuration.

    Args:
        args: Command line arguments
    """
    config_manager = ConfigManager()

    # Process configuration options
    try:
        # Handle identity file
        if args.identity_file:
            _set_identity_file(config_manager, args.identity_file)

        # Handle passphrase
        _set_passphrase(config_manager, args)

        # Handle expiration time
        if hasattr(args, "expiration") and args.expiration is not None:
            _set_expiration_time(config_manager, args.expiration)

        # Handle reuse agent
        if hasattr(args, "reuse_agent") and args.reuse_agent is not None:
            _set_reuse_agent(config_manager, args.reuse_agent)

    except SystemExit:
        # Re-raise any SystemExit exceptions
        raise
    except Exception as e:
        logger.error(f"Failed to set up configuration: {e}")
        sys.exit(1)


def _set_identity_file(config_manager, identity_file_path):
    """Set identity file in configuration.

    Args:
        config_manager: ConfigManager instance
        identity_file_path: Path to identity file
    """
    identity_file = os.path.expanduser(identity_file_path)
    if not os.path.exists(identity_file):
        logger.error(f"Identity file not found: {identity_file}")
        sys.exit(1)

    if config_manager.set_identity_file(identity_file):
        logger.info(f"Identity file set to: {identity_file}")
    else:
        logger.error("Failed to set identity file")
        sys.exit(1)


def _set_passphrase(config_manager, args):
    """Set passphrase in configuration.

    Args:
        config_manager: ConfigManager instance
        args: Command line arguments
    """
    # Get passphrase from arguments or prompt
    if args.passphrase:
        passphrase = args.passphrase
    elif args.prompt_passphrase:
        passphrase = getpass.getpass("Enter SSH key passphrase: ")
    else:
        return  # No passphrase to set

    try:
        # Set passphrase
        if config_manager.set_passphrase(passphrase):
            logger.info("Passphrase set successfully")
        else:
            logger.error("Failed to set passphrase")
            sys.exit(1)
    finally:
        # Always securely delete passphrase from memory
        if passphrase:
            config_manager.secure_delete_from_memory(passphrase)


def _set_expiration_time(config_manager, expiration_hours):
    """Set expiration time in configuration.

    Args:
        config_manager: ConfigManager instance
        expiration_hours: Expiration time in hours
    """
    if expiration_hours < 0:
        logger.error("Expiration time must be a positive number")
        sys.exit(1)

    if config_manager.set_expiration_time(expiration_hours):
        logger.info(f"Expiration time set to: {expiration_hours} hours")
    else:
        logger.error("Failed to set expiration time")
        sys.exit(1)


def _set_reuse_agent(config_manager, reuse_agent):
    """Set reuse agent setting in configuration.

    Args:
        config_manager: ConfigManager instance
        reuse_agent: Whether to reuse existing SSH agent
    """
    if config_manager.set_reuse_agent(reuse_agent):
        logger.info(f"Reuse agent set to: {reuse_agent}")
    else:
        logger.error("Failed to set reuse agent")
        sys.exit(1)


def run_ssh_connection_test(args):
    """Test SSH connection.

    Args:
        args: Command line arguments
    """
    config_manager = ConfigManager()
    passphrase = None

    try:
        # Get and validate identity file
        identity_file = _get_and_validate_identity_file(args, config_manager)

        # Get passphrase if available
        passphrase = _get_passphrase_for_test(config_manager)

        # Log configuration settings
        _log_test_configuration(args, config_manager)

        # Set up verbosity level if requested
        if hasattr(args, "verbose") and args.verbose:
            _configure_verbose_logging()

        # Create SSH configuration and agent
        ssh_config = SSHConfig(identity_file=identity_file, identity_passphrase=passphrase)
        ssh_agent = PersistentSSHAgent(config=ssh_config)

        # Test connection
        hostname = args.hostname
        if ssh_agent.setup_ssh(hostname):
            logger.info(f"✅ SSH connection to {hostname} successful")
        else:
            logger.error(f"❌ SSH connection to {hostname} failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"SSH connection test failed: {e}")
        sys.exit(1)
    finally:
        # Always clean up sensitive data
        if passphrase:
            config_manager.secure_delete_from_memory(passphrase)


def _get_and_validate_identity_file(args, config_manager):
    """Get and validate identity file from args or config.

    Args:
        args: Command line arguments
        config_manager: ConfigManager instance

    Returns:
        str: Path to identity file
    """
    # Get identity file from args or config
    identity_file = args.identity_file or config_manager.get_identity_file()
    if not identity_file:
        logger.error("No identity file specified or found in configuration")
        sys.exit(1)

    # Expand user directory in path
    identity_file = os.path.expanduser(identity_file)

    # Check if identity file exists
    if not os.path.exists(identity_file):
        logger.error(f"Identity file not found: {identity_file}")
        sys.exit(1)

    return identity_file


def _get_passphrase_for_test(config_manager):
    """Get passphrase from config if available.

    Args:
        config_manager: ConfigManager instance

    Returns:
        Optional[str]: Passphrase or None
    """
    stored_passphrase = config_manager.get_passphrase()
    if stored_passphrase:
        # Use deobfuscate_passphrase method to get plain text passphrase
        return config_manager.deobfuscate_passphrase(stored_passphrase)
    return None


def _log_test_configuration(args, config_manager):
    """Log test configuration settings.

    Args:
        args: Command line arguments
        config_manager: ConfigManager instance
    """
    # Log expiration time
    if hasattr(args, "expiration") and args.expiration is not None:
        logger.debug(f"Using expiration time from command line: {args.expiration} hours")
    else:
        stored_expiration = config_manager.get_expiration_time()
        if stored_expiration:
            logger.debug(f"Using expiration time from config: {stored_expiration / 3600} hours")

    # Log reuse agent setting
    if hasattr(args, "reuse_agent") and args.reuse_agent is not None:
        logger.debug(f"Using reuse agent setting from command line: {args.reuse_agent}")
    else:
        stored_reuse = config_manager.get_reuse_agent()
        if stored_reuse is not None:
            logger.debug(f"Using reuse agent setting from config: {stored_reuse}")


def _configure_verbose_logging():
    """Configure verbose logging with detailed format."""
    logger.remove()
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level="DEBUG",
    )


def list_keys(_):
    """List all configured SSH keys.

    Args:
        _: Command line arguments (unused)
    """
    config_manager = ConfigManager()

    try:
        keys = config_manager.list_keys()

        if not keys:
            logger.info("No SSH keys configured")
            return

        logger.info("Configured SSH keys:")
        for name, path in keys.items():
            logger.info(f"  {name}: {path}")
    except Exception as e:
        logger.error(f"Failed to list SSH keys: {e}")
        sys.exit(1)


def add_key(args):
    """Add a configured SSH key.

    Args:
        args: Command line arguments
    """
    config_manager = ConfigManager()

    # Check required arguments
    if not hasattr(args, "name") or not args.name:
        logger.error("No key name specified")
        sys.exit(1)

    if not hasattr(args, "identity_file") or not args.identity_file:
        logger.error("No identity file specified")
        sys.exit(1)

    name = args.name
    identity_file = args.identity_file

    try:
        # Add key
        if config_manager.add_key(name, identity_file):
            logger.info(f"SSH key '{name}' added")
        else:
            logger.error(f"Failed to add SSH key '{name}'")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to add SSH key '{name}': {e}")
        sys.exit(1)


def remove_key(args):
    """Remove a configured SSH key.

    Args:
        args: Command line arguments
    """
    config_manager = ConfigManager()

    if args.all:
        # Remove all keys
        if config_manager.clear_config():
            logger.info("All SSH keys removed")
        else:
            logger.error("Failed to remove SSH keys")
            sys.exit(1)
    elif args.name:
        # Remove specific key
        if config_manager.remove_key(args.name):
            logger.info(f"SSH key '{args.name}' removed")
        else:
            logger.error(f"Failed to remove SSH key '{args.name}' (not found)")
            sys.exit(1)
    else:
        logger.error("No key specified to remove")
        sys.exit(1)


def export_config(args):
    """Export configuration.

    Args:
        args: Command line arguments
    """
    config_manager = ConfigManager()

    # Export configuration
    config = config_manager.export_config(include_sensitive=args.include_sensitive)

    # Print configuration
    if args.output:
        # Write to file
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration exported to {args.output}")
        except IOError as e:
            logger.error(f"Failed to export configuration: {e}")
            sys.exit(1)
    else:
        # Print to console
        print(json.dumps(config, indent=2))


def import_config(args):
    """Import configuration.

    Args:
        args: Command line arguments
    """
    config_manager = ConfigManager()
    config = {}  # Initialize config to avoid UnboundLocalError

    # Read configuration
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Failed to import configuration: {e}")
        sys.exit(1)

    # Import configuration
    if config_manager.import_config(config):
        logger.info("Configuration imported successfully")
    else:
        logger.error("Failed to import configuration")
        sys.exit(1)


@click.group(help="Persistent SSH Agent CLI")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def main(ctx, debug):
    """Main entry point for CLI."""
    # Ensure that ctx.obj exists and is a dict (for subcommands)
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    # Configure logging based on debug flag
    if debug:
        _configure_debug_logging()
    else:
        _configure_default_logging()


def _configure_debug_logging():
    """Configure debug logging with detailed format."""
    logger.remove()
    logger.add(
        sys.stderr,
        format=LoggingConstants.DEBUG_LOG_FORMAT,
        level=LoggingConstants.DEBUG_LEVEL,
    )


def _configure_default_logging():
    """Configure default logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        format=LoggingConstants.DEFAULT_LOG_FORMAT,
        level=LoggingConstants.INFO_LEVEL,
    )


@main.command("config", help="Configure SSH agent")
@click.option("--identity-file", help="Path to SSH identity file")
@click.option("--passphrase", help="SSH key passphrase (not recommended, use --prompt-passphrase instead)")
@click.option("--prompt-passphrase", is_flag=True, help="Prompt for SSH key passphrase")
@click.option("--expiration", type=int, help="Expiration time in hours")
@click.option("--reuse-agent", type=bool, help="Whether to reuse existing SSH agent")
def config_cmd(identity_file, passphrase, prompt_passphrase, expiration, reuse_agent):
    """Configure SSH agent settings."""
    args = Args(
        identity_file=identity_file,
        passphrase=passphrase,
        prompt_passphrase=prompt_passphrase,
        expiration=expiration,
        reuse_agent=reuse_agent,
    )

    setup_config(args)


@main.command("test", help="Test SSH connection")
@click.argument("hostname")
@click.option("--identity-file", help="Path to SSH identity file (overrides config)")
@click.option("--expiration", type=int, help="Expiration time in hours (overrides config)")
@click.option("--reuse-agent", type=bool, help="Whether to reuse existing SSH agent (overrides config)")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def test_cmd(hostname, identity_file, expiration, reuse_agent, verbose):
    """Test SSH connection to a host."""
    args = Args(
        hostname=hostname, identity_file=identity_file, expiration=expiration, reuse_agent=reuse_agent, verbose=verbose
    )

    run_ssh_connection_test(args)


@main.command("list", help="List configured SSH keys")
def list_cmd():
    """List all configured SSH keys."""
    list_keys(None)


@main.command("add", help="Add a configured SSH key")
@click.option("--name", required=True, help="Name of the key to add")
@click.option("--identity-file", required=True, help="Path to SSH identity file")
def add(name, identity_file):
    """Add a configured SSH key."""
    args = Args(name=name, identity_file=identity_file)
    add_key(args)


@main.command("remove", help="Remove configured SSH keys")
@click.option("--name", help="Name of the key to remove")
@click.option("--all", "all_keys", is_flag=True, help="Remove all keys")
def remove(name, all_keys):
    """Remove configured SSH keys."""
    if not name and not all_keys:
        click.echo("Error: Either --name or --all must be specified")
        sys.exit(1)

    args = Args(name=name, all=all_keys)
    remove_key(args)


@main.command("export", help="Export configuration")
@click.option("--output", help="Output file path")
@click.option("--include-sensitive", is_flag=True, help="Include sensitive information in export")
def export_cmd(output, include_sensitive):
    """Export configuration."""
    args = Args(output=output, include_sensitive=include_sensitive)
    export_config(args)


@main.command("import", help="Import configuration")
@click.argument("input_file")
def import_config_cmd(input_file):
    """Import configuration from a file."""
    args = Args(input=input_file)
    import_config(args)


@main.command("git-setup", help="Set up Git credentials")
@click.option("--username", help="Git username")
@click.option("--password", help="Git password/token")
@click.option("--prompt", is_flag=True, help="Prompt for credentials")
@click.pass_context
def git_setup_cmd(ctx, username, password, prompt):
    """Set up Git credential helper.

    This command configures Git to use username/password authentication
    and is completely independent of SSH keys or SSH agent configuration.
    """
    try:
        if prompt:
            username = click.prompt("Git username")
            password = click.prompt("Git password/token", hide_input=True)

        # Get debug flag from context
        debug_mode = ctx.obj.get("debug", False)

        if debug_mode:
            logger.debug("Debug mode enabled for git-setup command")
            logger.debug("Username provided: %s", bool(username))
            logger.debug("Password provided: %s", bool(password))
            logger.debug("Prompt mode: %s", prompt)

        ssh_agent = PersistentSSHAgent()
        if ssh_agent.git.setup_git_credentials(username, password):
            logger.info("✅ Git credentials configured successfully")
        else:
            logger.error("❌ Failed to configure Git credentials")
            sys.exit(1)

    except Exception as e:
        logger.error("Failed to set up Git credentials: %s", str(e))
        if ctx.obj.get("debug", False):
            logger.exception("Full traceback:")
        sys.exit(1)


@main.command("git-debug", help="Debug Git credential configuration")
@click.pass_context
def git_debug_cmd(ctx):
    """Debug Git credential helper configuration."""
    try:
        ssh_agent = PersistentSSHAgent()

        # Get current credential helpers
        current_helpers = ssh_agent.git.get_current_credential_helpers()

        logger.info("🔍 Git Credential Configuration Debug")
        logger.info("=" * 50)

        if current_helpers:
            logger.info("📋 Current credential helpers:")
            for i, helper in enumerate(current_helpers, 1):
                logger.info(f"  {i}. {helper}")
        else:
            logger.info("📋 No credential helpers currently configured")

        # Show Git config file locations
        logger.info("\n📁 Git configuration file locations:")

        # Global config
        try:
            result = run_command(["git", "config", "--global", "--list", "--show-origin"])
            if result and result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                global_config_file = None
                for line in lines:
                    if "credential.helper=" in line:
                        parts = line.split("\t", 1)
                        if len(parts) == 2:
                            config_file = parts[0].replace("file:", "")
                            if global_config_file != config_file:
                                global_config_file = config_file
                                logger.info(f"  Global: {config_file}")
                            logger.info(f"    - {parts[1]}")

                if not global_config_file:
                    # Try to get global config file location
                    result = run_command(["git", "config", "--global", "--list", "--show-origin"])
                    if result and result.returncode == 0 and result.stdout:
                        first_line = result.stdout.strip().split("\n")[0]
                        if "\t" in first_line:
                            config_file = first_line.split("\t")[0].replace("file:", "")
                            logger.info(f"  Global: {config_file}")
        except Exception as e:
            logger.warning(f"Could not determine Git config file location: {e}")

        # Show environment variables
        logger.info("\n🌍 Environment variables:")
        git_username = os.environ.get("GIT_USERNAME")
        git_password = os.environ.get("GIT_PASSWORD")

        if git_username:
            logger.info(f"  GIT_USERNAME: {git_username}")
        else:
            logger.info("  GIT_USERNAME: (not set)")

        if git_password:
            logger.info("  GIT_PASSWORD: (set, hidden)")
        else:
            logger.info("  GIT_PASSWORD: (not set)")

        logger.info("\n💡 Troubleshooting tips:")
        if len(current_helpers) > 1:
            logger.info("  - Multiple credential helpers detected")
            logger.info("  - Use 'uvx persistent_ssh_agent git-clear' to clear all")
            logger.info("  - Then run 'uvx persistent_ssh_agent git-setup' again")
        elif not current_helpers:
            logger.info("  - No credential helpers configured")
            logger.info("  - Run 'uvx persistent_ssh_agent git-setup --prompt' to configure")
        else:
            logger.info("  - Single credential helper configured (normal)")

    except Exception as e:
        logger.error("Failed to debug Git configuration: %s", str(e))
        if ctx.obj.get("debug", False):
            logger.exception("Full traceback:")
        sys.exit(1)


@main.command("git-clear", help="Clear all Git credential helpers")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def git_clear_cmd(ctx, confirm):
    """Clear all Git credential helpers.

    This command removes Git credential helper configurations
    and is completely independent of SSH keys or SSH agent configuration.
    """
    try:
        ssh_agent = PersistentSSHAgent()

        # Get current credential helpers
        current_helpers = ssh_agent.git.get_current_credential_helpers()

        if not current_helpers:
            logger.info("✅ No credential helpers found to clear")
            return

        # Show what will be cleared
        logger.info("🔍 Found %d credential helper(s) to clear:", len(current_helpers))
        for i, helper in enumerate(current_helpers, 1):
            logger.info(f"  {i}. {helper}")

        # Confirm action unless --confirm flag is used
        if not confirm and not click.confirm("\n⚠️  Are you sure you want to clear all credential helpers?"):
            logger.info("❌ Operation cancelled")
            return

        # Clear credential helpers
        if ssh_agent.git.clear_credential_helpers():
            logger.info("✅ Successfully cleared all Git credential helpers")
            logger.info("💡 You can now run 'uvx persistent_ssh_agent git-setup --prompt' to configure new credentials")
        else:
            logger.error("❌ Failed to clear Git credential helpers")
            sys.exit(1)

    except Exception as e:
        logger.error("Failed to clear Git credential helpers: %s", str(e))
        if ctx.obj.get("debug", False):
            logger.exception("Full traceback:")
        sys.exit(1)


@main.command("git-run", help="Run Git command with automatic passwordless authentication")
@click.argument("git_args", nargs=-1, required=True)
@click.option("--username", "-u", help="Git username (overrides GIT_USERNAME env var)")
@click.option("--password", "-p", help="Git password/token (overrides GIT_PASSWORD env var)")
@click.option("--prefer-credentials", is_flag=True, help="Prefer credential helper over SSH")
@click.option("--prompt", is_flag=True, help="Prompt for credentials if not provided")
@click.pass_context
def git_run_cmd(ctx, git_args, username, password, prefer_credentials, prompt):
    """Run Git command with automatic passwordless authentication.

    This command intelligently chooses between SSH and credential helper authentication
    to execute Git commands without requiring manual password input.

    Examples:
        uvx persistent_ssh_agent git-run clone git@github.com:user/repo.git
        uvx persistent_ssh_agent git-run pull origin main
        uvx persistent_ssh_agent git-run --prefer-credentials push origin main
        uvx persistent_ssh_agent git-run --prompt submodule update --init --recursive
    """
    try:
        if prompt and not username:
            username = click.prompt("Git username", default=os.environ.get("GIT_USERNAME", ""))
        if prompt and not password:
            password = click.prompt("Git password/token", hide_input=True,
                                   default=os.environ.get("GIT_PASSWORD", ""))

        # Get debug flag from context
        debug_mode = ctx.obj.get("debug", False)

        if debug_mode:
            logger.debug("Debug mode enabled for git-run command")
            logger.debug("Git arguments: %s", git_args)
            logger.debug("Username provided: %s", bool(username))
            logger.debug("Password provided: %s", bool(password))
            logger.debug("Prefer credentials: %s", prefer_credentials)

        # Build Git command
        git_command = ["git"] + list(git_args)

        logger.info("🚀 Running Git command: %s", " ".join(git_command))

        # Create SSH agent instance
        ssh_agent = PersistentSSHAgent()

        # Run Git command with passwordless authentication
        result = ssh_agent.run_git_command_passwordless(
            git_command,
            username=username,
            password=password,
            prefer_ssh=not prefer_credentials
        )

        if result is None:
            logger.error("❌ Git command failed to execute")
            sys.exit(1)
        elif result.returncode == 0:
            logger.info("✅ Git command completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            logger.error("❌ Git command failed with return code: %d", result.returncode)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)

    except KeyboardInterrupt:
        logger.info("❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Failed to run Git command: %s", str(e))
        if ctx.obj.get("debug", False):
            logger.exception("Full traceback:")
        sys.exit(1)



if __name__ == "__main__":
    main(obj={})
