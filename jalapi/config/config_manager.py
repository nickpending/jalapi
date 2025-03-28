# config_manager.py
"""
Configuration management module for JALAPI.

This module provides functionality to load and validate the application's configuration.
"""

import yaml
from typing import Dict, Any


class ConfigurationError(Exception):
    """Base exception for configuration-related errors in the JALAPI system."""

    pass


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        file_path (str): Path to the configuration file.
        
    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary.
        
    Raises:
        ConfigurationError: If the file is not found or has invalid YAML syntax.
    """
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except (FileNotFoundError, yaml.YAMLError) as e:
        raise ConfigurationError(f"Error loading configuration file: {str(e)}")
