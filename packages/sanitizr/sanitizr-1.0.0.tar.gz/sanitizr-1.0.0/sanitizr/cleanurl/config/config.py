"""
Configuration module for Sanitizr.

This module handles loading and parsing configuration files in JSON or YAML format.
"""

import json
import os
import pathlib
from typing import Any, Dict, Optional, Set, Union

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigManager:
    """Configuration manager for Sanitizr."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to configuration file (JSON or YAML)
        """
        self.config_path = config_path
        self.config = {}
        
        # Load default configuration
        self.load_default_config()
        
        # If a config path was provided, load it
        if config_path:
            self.load_config(config_path)
            
    def load_default_config(self) -> Dict[str, Any]:
        """
        Load the default configuration from the package data.
        
        Returns:
            The default configuration dictionary
        """
        # Get the path to the default config file
        default_config_path = pathlib.Path(__file__).parent.parent / "data" / "default_params.json"
        
        try:
            if default_config_path.exists():
                with open(default_config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "tracking_params": [],
                    "redirect_params": {},
                    "whitelist_params": [],
                    "blacklist_params": []
                }
        except Exception as e:
            print(f"Error loading default configuration: {e}")
            self.config = {
                "tracking_params": [],
                "redirect_params": {},
                "whitelist_params": [],
                "blacklist_params": []
            }
            
        return self.config
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from a file (JSON or YAML).
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The loaded configuration dictionary
        """
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        file_ext = os.path.splitext(config_path)[1].lower()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if file_ext in (".yml", ".yaml"):
                    if not YAML_AVAILABLE:
                        raise ImportError("YAML support requires PyYAML. Install with: pip install pyyaml")
                    loaded_config = yaml.safe_load(f)
                elif file_ext == ".json":
                    loaded_config = json.load(f)
                else:
                    raise ValueError(f"Unsupported configuration file format: {file_ext}")
                    
                # Merge with existing config
                self._merge_config(loaded_config)
                
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
            
        return self.config
        
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Merge a new configuration with the existing one.
        
        Args:
            new_config: New configuration to merge
        """
        # Merge tracking parameters
        if "tracking_params" in new_config and isinstance(new_config["tracking_params"], list):
            if "tracking_params" not in self.config:
                self.config["tracking_params"] = []
            self.config["tracking_params"].extend(new_config["tracking_params"])
            # Remove duplicates
            self.config["tracking_params"] = list(set(self.config["tracking_params"]))
            
        # Merge redirect parameters
        if "redirect_params" in new_config and isinstance(new_config["redirect_params"], dict):
            if "redirect_params" not in self.config:
                self.config["redirect_params"] = {}
                
            for domain, params in new_config["redirect_params"].items():
                if domain in self.config["redirect_params"]:
                    # Merge parameters for existing domain
                    self.config["redirect_params"][domain].extend(params)
                    # Remove duplicates
                    self.config["redirect_params"][domain] = list(set(self.config["redirect_params"][domain]))
                else:
                    # Add new domain
                    self.config["redirect_params"][domain] = params
                    
        # Merge whitelist parameters
        if "whitelist_params" in new_config and isinstance(new_config["whitelist_params"], list):
            if "whitelist_params" not in self.config:
                self.config["whitelist_params"] = []
            self.config["whitelist_params"].extend(new_config["whitelist_params"])
            # Remove duplicates
            self.config["whitelist_params"] = list(set(self.config["whitelist_params"]))
            
        # Merge blacklist parameters
        if "blacklist_params" in new_config and isinstance(new_config["blacklist_params"], list):
            if "blacklist_params" not in self.config:
                self.config["blacklist_params"] = []
            self.config["blacklist_params"].extend(new_config["blacklist_params"])
            # Remove duplicates
            self.config["blacklist_params"] = list(set(self.config["blacklist_params"]))
            
    def get_tracking_params(self) -> Set[str]:
        """Get the set of tracking parameters from the configuration."""
        return set(self.config.get("tracking_params", []))
        
    def get_redirect_params(self) -> Dict[str, list]:
        """Get the dictionary of redirect parameters by domain."""
        return self.config.get("redirect_params", {})
        
    def get_whitelist_params(self) -> Set[str]:
        """Get the set of whitelisted parameters."""
        return set(self.config.get("whitelist_params", []))
        
    def get_blacklist_params(self) -> Set[str]:
        """Get the set of blacklisted parameters."""
        return set(self.config.get("blacklist_params", []))