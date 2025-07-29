"""
Tests for package imports and initialization.
"""
import pytest
import importlib


def test_package_imports():
    """Test importing the main package."""
    import sanitizr
    assert hasattr(sanitizr, "__version__")
    
    # Check that the main modules can be imported
    from sanitizr import sanitizr
    assert sanitizr is not None
    
    # Check that submodules can be imported
    from sanitizr.sanitizr import core, config, cli
    assert core is not None
    assert config is not None
    assert cli is not None
    
    # Check specific components
    from sanitizr.sanitizr.core import cleaner
    assert hasattr(cleaner, "URLCleaner")
    
    from sanitizr.sanitizr.config import config
    assert hasattr(config, "ConfigManager")


def test_cli_entrypoint():
    """Test that the CLI entrypoint is properly registered."""
    # This test verifies that the CLI entrypoint defined in pyproject.toml works
    try:
        # Python 3.8+ approach using importlib.metadata
        import importlib.metadata
        
        # Get all entrypoints for the 'console_scripts' group
        entry_points = importlib.metadata.entry_points()
        
        # In Python 3.10+, entry_points() returns a dictionary of SelectableGroups
        if hasattr(entry_points, 'select'):  # Python 3.10+
            console_scripts = list(entry_points.select(group='console_scripts'))
        else:  # Python 3.8, 3.9
            console_scripts = entry_points.get('console_scripts', [])
        
        # Find the 'sanitizr' entrypoint
        sanitizr_entry = next((ep for ep in console_scripts if ep.name == 'sanitizr'), None)
        
        # Verify that the 'sanitizr' entrypoint exists
        assert sanitizr_entry is not None
        
        # Verify that the entrypoint points to the correct module/function
        assert sanitizr_entry.value == 'sanitizr.sanitizr.cli.__main__:main'
    except (ImportError, AttributeError):
        pytest.skip("Could not test entrypoints with importlib.metadata")


def test_version_consistency():
    """Test that version is consistent across the package."""
    import sanitizr
    
    # Get version from module
    module_version = sanitizr.__version__
    
    # Try to get version from package metadata
    try:
        import importlib.metadata
        metadata_version = importlib.metadata.version('sanitizr')
        # Check that versions match
        assert module_version == metadata_version
    except (ImportError, importlib.metadata.PackageNotFoundError):
        # Skip this check if we can't get metadata version
        pass
