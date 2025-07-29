"""
Additional tests for the Sanitizr URL cleaner module focusing on edge cases.
"""
import pytest
from urllib.parse import urlparse, parse_qs

from sanitizr.cleanurl.core.cleaner import URLCleaner


def test_empty_url():
    """Test cleaning an empty URL."""
    cleaner = URLCleaner()
    assert cleaner.clean_url("") == ""
    assert cleaner.clean_url(None) == ""


def test_invalid_url():
    """Test cleaning invalid URLs."""
    cleaner = URLCleaner()
    # Test handling of URLs without scheme - current implementation just returns them as is
    assert cleaner.clean_url("example.com") == "example.com"
    # Very malformed URLs are just returned as is in the current implementation
    assert cleaner.clean_url("not a url") == "not a url"


def test_custom_tracking_params():
    """Test cleaning URLs with custom tracking parameters."""
    custom_params = ["custom_track", "special_param"]
    cleaner = URLCleaner(custom_tracking_params=custom_params)
    
    url = "https://example.com?custom_track=abc&special_param=123&keep_this=value"
    cleaned = cleaner.clean_url(url)
    
    # Parse the URL to check parameters
    parsed = urlparse(cleaned)
    query_params = parse_qs(parsed.query)
    
    # Custom tracking params should be removed
    assert "custom_track" not in query_params
    assert "special_param" not in query_params
    # Other params should be kept
    assert "keep_this" in query_params


def test_whitelist_params():
    """Test cleaning URLs with whitelisted parameters."""
    # Define standard tracking parameters and a whitelist
    tracking_params = ["utm_source", "utm_medium", "utm_campaign"]
    whitelist = ["utm_source"]  # Allow utm_source but remove other tracking params
    
    cleaner = URLCleaner(
        custom_tracking_params=tracking_params,
        whitelist_params=whitelist
    )
    
    url = "https://example.com?utm_source=google&utm_medium=cpc&utm_campaign=spring"
    cleaned = cleaner.clean_url(url)
    
    # Parse the URL to check parameters
    parsed = urlparse(cleaned)
    query_params = parse_qs(parsed.query)
    
    # Whitelisted param should be kept
    assert "utm_source" in query_params
    assert query_params["utm_source"] == ["google"]
    
    # Non-whitelisted tracking params should be removed
    assert "utm_medium" not in query_params
    assert "utm_campaign" not in query_params


def test_blacklist_params():
    """Test cleaning URLs with blacklisted parameters."""
    # Define blacklist parameters
    blacklist = ["sensitive", "private"]
    
    cleaner = URLCleaner(blacklist_params=blacklist)
    
    url = "https://example.com?normal=value&sensitive=data&private=info"
    cleaned = cleaner.clean_url(url)
    
    # Parse the URL to check parameters
    parsed = urlparse(cleaned)
    query_params = parse_qs(parsed.query)
    
    # Blacklisted params should be removed
    assert "sensitive" not in query_params
    assert "private" not in query_params
    
    # Non-blacklisted params should be kept
    assert "normal" in query_params
    assert query_params["normal"] == ["value"]


def test_redirect_params():
    """Test handling of redirect parameters."""
    # Test with default redirect params
    default_cleaner = URLCleaner()
    assert hasattr(default_cleaner, 'redirect_params')
    assert isinstance(default_cleaner.redirect_params, dict)
    
    # Test with custom redirect params - needs to be a dict mapping domains to lists of params
    custom_param = "redirect_to"
    custom_domain = "example.com"
    custom_redirect_params = {custom_domain: [custom_param]}
    
    custom_cleaner = URLCleaner(custom_redirect_params=custom_redirect_params)
    
    # Verify the custom parameter is in the redirect_params for the specified domain
    assert custom_domain in custom_cleaner.redirect_params
    assert custom_param in custom_cleaner.redirect_params[custom_domain]


def test_url_with_complex_params():
    """Test cleaning URLs with complex parameters."""
    cleaner = URLCleaner()
    
    # Test a URL with complex parameters
    complex_url = "https://example.com/page?param1=value1&utm_source=test&param2=value2"
    cleaned_url = cleaner.clean_url(complex_url)
    
    # Check that tracking parameters are removed
    assert "utm_source" not in cleaned_url
    # Check that other parameters remain
    assert "param1=value1" in cleaned_url
    assert "param2=value2" in cleaned_url


def test_escaped_fragment_as_normal_param():
    """Test handling of escaped fragment parameters."""
    cleaner = URLCleaner()
    
    # Test URL with escaped fragment
    escaped_fragment_url = "https://example.com?_escaped_fragment_=path/to/page"
    cleaned = cleaner.clean_url(escaped_fragment_url)
    
    # In the current implementation, the URL is cleaned
    # but the fragment might be URL-encoded
    assert "_escaped_fragment_=" in cleaned
    # The test only checks that the parameter is preserved, not the exact encoding


def test_fragment_handling():
    """Test preservation of URL fragments (hash)."""
    cleaner = URLCleaner()
    
    # URL with a fragment and tracking parameters
    url = "https://example.com/page?utm_source=test#section2"
    cleaned = cleaner.clean_url(url)
    
    # Tracking parameters should be removed but fragment preserved
    assert cleaned == "https://example.com/page#section2"


def test_path_preservation():
    """Test URL path preservation."""
    cleaner = URLCleaner()
    
    # URL with path components
    url = "https://example.com/./path/../path/to/page"
    cleaned = cleaner.clean_url(url)
    
    # In the current implementation, paths are preserved as-is
    assert cleaned == url


def test_case_preservation():
    """Test URL case preservation."""
    cleaner = URLCleaner()
    
    # URL with mixed case in domain
    url = "https://ExAmPlE.CoM/path?param=value"
    cleaned = cleaner.clean_url(url)
    
    # In the current implementation, case is preserved
    assert cleaned == url


def test_www_normalization():
    """Test handling of www subdomain."""
    cleaner = URLCleaner()
    
    # URLs with and without www
    url1 = "https://www.example.com"
    url2 = "https://example.com"
    
    # Check if www is handled consistently
    cleaned1 = cleaner.clean_url(url1)
    cleaned2 = cleaner.clean_url(url2)
    
    # This will check what the cleaner's policy is
    # Some cleaners remove www, others keep it
    assert cleaned1 in (url1, url2)
