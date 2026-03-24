"""Configuration module for the Financial Feature Store."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Default configuration file path
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"


class Config:
    """Configuration manager for the application."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure single config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports nested keys with dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


# Global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config
