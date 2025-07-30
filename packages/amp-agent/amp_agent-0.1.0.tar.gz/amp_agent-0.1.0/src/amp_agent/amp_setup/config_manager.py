"""
Configuration management for AMP agents.
Handles environment variables, secrets, and configuration in a structured way.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import yaml
from dotenv import load_dotenv, set_key
from dataclasses import dataclass
import logging

from amp_agent.amp_setup.auth_constants import AUTH_ENV_MAPPING, ENV_AUTH_MAPPING

# Configure logging
logger = logging.getLogger(__name__)

# Default configuration paths
DEFAULT_CONFIG_DIR = "amp_agents"
DEFAULT_CONFIG_FILE = "agents.yaml"

@dataclass
class AuthConfig:
    """Authentication configuration data class"""
    token: Optional[str] = None
    organization_id: Optional[str] = None
    platform_id: Optional[str] = None
    platform_client_id: Optional[str] = None
    platform_client_secret: Optional[str] = None
    platform_api_key: Optional[str] = None
    platform_api_key_expires_at: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        """Check if all required fields are present"""
        return all([
            self.token,
            self.organization_id,
            self.platform_id,
            self.platform_api_key
        ])

    @property
    def is_api_key_valid(self) -> bool:
        """Check if API key is valid and not expired"""
        if not self.platform_api_key or not self.platform_api_key_expires_at:
            return False
        try:
            expires_at = datetime.fromisoformat(
                self.platform_api_key_expires_at.replace('Z', '+00:00')
            )
            return expires_at > datetime.now(timezone.utc)
        except (ValueError, TypeError):
            return False

class ConfigManager:
    """
    Manages configuration and environment variables for AMP agents.
    
    This class provides a centralized way to:
    - Load and save environment variables
    - Handle authentication configuration
    - Manage agent-specific configuration
    - Validate configuration state
    """
    
    def __init__(self, root_dir: Path = None, config_dir: str = None, config_file: str = None):
        """
        Initialize the configuration manager.
        
        Args:
            root_dir: Root directory containing .env and config files
            config_dir: Directory containing agent configuration (default: from AMP_CONFIG_DIR env var or 'amp_agents')
            config_file: Name of the agent configuration file (default: from AMP_CONFIG_FILE env var or 'agents.yaml')
        """
        self.root_dir = root_dir or Path.cwd()
        self.env_path = self.root_dir / ".env"
        self.config_dir = config_dir or os.getenv("AMP_CONFIG_DIR", DEFAULT_CONFIG_DIR)
        self.config_file = config_file or os.getenv("AMP_CONFIG_FILE", DEFAULT_CONFIG_FILE)
        self.auth_config = AuthConfig()
        self._load_env()

    def _load_env(self):
        """Load environment variables and update auth config"""
        load_dotenv(self.env_path)
        
        # Update auth config from environment
        for auth_key, env_key in AUTH_ENV_MAPPING.items():
            value = os.getenv(env_key)
            if hasattr(self.auth_config, auth_key):
                setattr(self.auth_config, auth_key, value)

    def save_env_variable(self, key: str, value: str):
        """
        Save a single environment variable.
        
        Args:
            key: Environment variable key
            value: Value to save
        """
        if not self.env_path.exists():
            self.env_path.touch()
        
        set_key(self.env_path, key, value)
        os.environ[key] = value  # Update current environment
        
        # Update auth config if applicable
        auth_key = ENV_AUTH_MAPPING.get(key)
        if auth_key and hasattr(self.auth_config, auth_key):
            setattr(self.auth_config, auth_key, value)

    def save_auth_data(self, auth_data: Dict[str, str]):
        """
        Save authentication data to environment and update config.
        
        Args:
            auth_data: Dictionary of authentication data
        """
        for auth_key, env_key in AUTH_ENV_MAPPING.items():
            if auth_key in auth_data and auth_data[auth_key]:
                self.save_env_variable(env_key, auth_data[auth_key])

    def get_agent_env_var(self, agent_id: str) -> Optional[str]:
        """
        Get environment variable for specific agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Environment variable value if exists, None otherwise
        """
        env_var = f"AMP_AGENT_ID_{agent_id.upper()}"
        return os.getenv(env_var)

    def set_agent_env_var(self, agent_id: str, value: str):
        """
        Set environment variable for specific agent.
        
        Args:
            agent_id: Agent identifier
            value: Value to set
        """
        env_var = f"AMP_AGENT_ID_{agent_id.upper()}"
        self.save_env_variable(env_var, value)

    def load_agent_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load agent configuration from YAML.
        
        Args:
            config_path: Optional path to config file. If relative, it's relative to current working directory.
            
        Returns:
            Dictionary containing agent configuration
        """
        try:
            if config_path is None:
                # Use default path relative to current working directory
                config_path = Path.cwd() / self.config_dir / self.config_file
            elif not config_path.is_absolute():
                # Make relative paths relative to current working directory
                config_path = Path.cwd() / config_path
                
            logger.debug(f"Loading agent config from: {config_path}")
            
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Agent configuration file not found at: {config_path}")
            return {"agents": {}}
        except Exception as e:
            logger.error(f"Error loading agent configuration: {str(e)}")
            return {"agents": {}}

    def needs_authentication(self) -> bool:
        """Check if authentication is needed"""
        return not (self.auth_config.is_complete and self.auth_config.is_api_key_valid)

    def get_platform_api_key(self) -> Optional[str]:
        """Get the platform API key if valid"""
        if self.auth_config.is_api_key_valid:
            return self.auth_config.platform_api_key
        return None

    def get_agent_yaml_path(self) -> Path:
        """Get the path to the agents configuration file."""
        return Path.cwd() / self.config_dir / self.config_file

    def get_agent_id(self, agent_id: str) -> Optional[str]:
        """Get the agent_id for a specific agent from YAML config."""
        config = self.load_agent_config()
        return config["agents"].get(agent_id, {}).get("amp_agent_id")

    def set_agent_id(self, agent_id: str, value: str):
        """Set the agent_id for a specific agent in YAML config."""
        config_path = self.get_agent_yaml_path()
        config = self.load_agent_config(config_path)
        if agent_id in config["agents"]:
            config["agents"][agent_id]["amp_agent_id"] = value
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f, sort_keys=False)

    def get_agent_api_key(self, agent_id: str) -> Optional[str]:
        """Get the API key for a specific agent from YAML config."""
        config = self.load_agent_config()
        return config["agents"].get(agent_id, {}).get("amp_api_key")

    def set_agent_api_key(self, agent_id: str, value: str):
        """Set the API key for a specific agent in YAML config."""
        config_path = self.get_agent_yaml_path()
        config = self.load_agent_config(config_path)
        if agent_id in config["agents"]:
            config["agents"][agent_id]["amp_api_key"] = value
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f, sort_keys=False)

    def get_agent_api_key_expiration(self, agent_id: str) -> Optional[str]:
        """Get the API key expiration for a specific agent from YAML config."""
        config = self.load_agent_config()
        return config["agents"].get(agent_id, {}).get("amp_api_key_expires_at")

    def set_agent_api_key_expiration(self, agent_id: str, value: str):
        """Set the API key expiration for a specific agent in YAML config."""
        config_path = self.get_agent_yaml_path()
        config = self.load_agent_config(config_path)
        if agent_id in config["agents"]:
            config["agents"][agent_id]["amp_api_key_expires_at"] = value
            with open(config_path, "w") as f:
                yaml.safe_dump(config, f, sort_keys=False) 