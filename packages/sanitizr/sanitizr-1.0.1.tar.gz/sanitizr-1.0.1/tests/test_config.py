"""
Tests for the Sanitizr config module.
"""
import json
import os
import sys
import pytest
from unittest import mock
import tempfile

from sanitizr.sanitizr.config.config import ConfigManager


def create_temp_config(config_data, file_format="json"):
    """Helper to create a temporary config file."""
    with tempfile.NamedTemporaryFile(suffix=f".{file_format}", mode="w", encoding="utf-8", delete=False) as temp_file:
        if file_format == "json":
            json.dump(config_data, temp_file)
        elif file_format == "yaml":
            pytest.importorskip("yaml")
            import yaml
            yaml.dump(config_data, temp_file)
    
    return temp_file.name


def test_config_manager_default():
    """Test ConfigManager with default configuration."""
    config_manager = ConfigManager()
    
    # Test that default tracking parameters are loaded
    tracking_params = config_manager.get_tracking_params()
    assert isinstance(tracking_params, set)
    assert "utm_source" in tracking_params
    assert "fbclid" in tracking_params
    
    # Test that default redirect parameters are loaded
    redirect_params = config_manager.get_redirect_params()
    assert isinstance(redirect_params, dict)
    assert "google.com" in redirect_params
    assert "url" in redirect_params["google.com"]
    
    # Test that default whitelist parameters are loaded
    whitelist_params = config_manager.get_whitelist_params()
    assert isinstance(whitelist_params, set)
    
    # Test that default blacklist parameters are loaded
    blacklist_params = config_manager.get_blacklist_params()
    assert isinstance(blacklist_params, set)


def test_config_manager_custom_json():
    """Test ConfigManager with a custom JSON config."""
    custom_config = {
        "tracking_params": ["custom_tracking", "another_param"],
        "redirect_params": {
            "example.com": ["custom_redirect"],
            "google.com": ["additional_param"]
        },
        "whitelist_params": ["keep_this_param"],
        "blacklist_params": ["remove_this_param"]
    }
    
    config_file = create_temp_config(custom_config)
    try:
        config_manager = ConfigManager(config_file)
        
        # Test that custom tracking parameters are loaded
        tracking_params = config_manager.get_tracking_params()
        assert "custom_tracking" in tracking_params
        assert "another_param" in tracking_params
        
        # Default params should be merged
        assert "utm_source" in tracking_params
        
        # Test that custom redirect parameters are loaded
        redirect_params = config_manager.get_redirect_params()
        assert "example.com" in redirect_params
        assert "custom_redirect" in redirect_params["example.com"]
        
        # Test that custom whitelist parameters are loaded
        whitelist_params = config_manager.get_whitelist_params()
        assert "keep_this_param" in whitelist_params
        
        # Test that custom blacklist parameters are loaded
        blacklist_params = config_manager.get_blacklist_params()
        assert "remove_this_param" in blacklist_params
    finally:
        # Clean up temporary file
        os.unlink(config_file)


@pytest.mark.skipif(not sys.modules['sanitizr.sanitizr.config.config'].YAML_AVAILABLE, 
                reason="PyYAML not installed")
def test_config_manager_custom_yaml():
    """Test ConfigManager with a custom YAML config."""
    custom_config = {
        "tracking_params": ["yaml_tracking", "yaml_param"],
        "redirect_params": {
            "example.org": ["yaml_redirect"],
            "twitter.com": ["yaml_param"]
        },
        "whitelist_params": ["yaml_whitelist"],
        "blacklist_params": ["yaml_blacklist"]
    }
    
    config_file = create_temp_config(custom_config, "yaml")
    try:
        config_manager = ConfigManager(config_file)
        
        # Test that custom tracking parameters are loaded
        tracking_params = config_manager.get_tracking_params()
        assert "yaml_tracking" in tracking_params
        assert "yaml_param" in tracking_params
        
        # Default params should be merged
        assert "utm_source" in tracking_params
        
        # Test that custom redirect parameters are loaded
        redirect_params = config_manager.get_redirect_params()
        assert "example.org" in redirect_params
        assert "yaml_redirect" in redirect_params["example.org"]
        
        # Test that custom whitelist parameters are loaded
        whitelist_params = config_manager.get_whitelist_params()
        assert "yaml_whitelist" in whitelist_params
        
        # Test that custom blacklist parameters are loaded
        blacklist_params = config_manager.get_blacklist_params()
        assert "yaml_blacklist" in blacklist_params
    finally:
        # Clean up temporary file
        os.unlink(config_file)


def test_config_manager_invalid_json():
    """Test ConfigManager with an invalid JSON config."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_file.write(b"{invalid json")
    
    config_file = temp_file.name
    try:
        with pytest.raises(Exception):
            ConfigManager(config_file)
    finally:
        # Clean up temporary file
        os.unlink(config_file)


def test_config_manager_unsupported_format():
    """Test ConfigManager with an unsupported file format."""
    with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", encoding="utf-8", delete=False) as temp_file:
        temp_file.write("not a config file")
    
    config_file = temp_file.name
    try:
        with pytest.raises(ValueError, match="Unsupported configuration file format"):
            ConfigManager(config_file)
    finally:
        # Clean up temporary file
        os.unlink(config_file)


@pytest.mark.skipif(sys.modules['sanitizr.sanitizr.config.config'].YAML_AVAILABLE, 
                reason="PyYAML is installed")
def test_yaml_not_installed():
    """Test handling when PyYAML is not installed."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_file:
        temp_file.write(b"yaml: content")
    
    config_file = temp_file.name
    try:
        with pytest.raises(ImportError, match="PyYAML package is required"):
            ConfigManager(config_file)
    finally:
        # Clean up temporary file
        os.unlink(config_file)


def test_config_manager_nonexistent_file():
    """Test ConfigManager with a nonexistent config file."""
    with pytest.raises(FileNotFoundError):
        ConfigManager("nonexistent_config_file.json")


def test_get_tracking_params_additional():
    """Test getting tracking params with additional parameters manually."""
    config_manager = ConfigManager()
    
    # Get default tracking parameters
    tracking_params = config_manager.get_tracking_params()
    
    # Add additional parameters manually
    additional_params = {"extra_param1", "extra_param2"}
    combined_params = tracking_params.union(additional_params)
    
    # Check that both default and additional parameters are included
    assert "utm_source" in combined_params
    assert "fbclid" in combined_params
    assert "extra_param1" in combined_params
    assert "extra_param2" in combined_params
