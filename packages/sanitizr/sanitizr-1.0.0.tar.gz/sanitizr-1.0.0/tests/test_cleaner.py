"""
Unit tests for the Sanitizr URL cleaner.
"""

import unittest
from sanitizr.cleanurl.core.cleaner import URLCleaner


class TestURLCleaner(unittest.TestCase):
    """Test cases for the URLCleaner class."""

    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = URLCleaner()
        
    def test_clean_url_empty(self):
        """Test cleaning an empty URL."""
        self.assertEqual(self.cleaner.clean_url(""), "")
        self.assertEqual(self.cleaner.clean_url(None), "")
        
    def test_clean_url_no_query(self):
        """Test cleaning a URL with no query parameters."""
        url = "https://example.com/page"
        self.assertEqual(self.cleaner.clean_url(url), url)
        
    def test_clean_url_tracking_params(self):
        """Test cleaning a URL with tracking parameters."""
        url = "https://example.com/page?id=123&utm_source=newsletter&utm_medium=email"
        expected = "https://example.com/page?id=123"
        self.assertEqual(self.cleaner.clean_url(url), expected)
        
    def test_clean_url_all_tracking_params(self):
        """Test cleaning a URL with only tracking parameters."""
        url = "https://example.com/page?utm_source=newsletter&utm_medium=email"
        expected = "https://example.com/page"
        self.assertEqual(self.cleaner.clean_url(url), expected)
        
    def test_clean_url_mixed_params(self):
        """Test cleaning a URL with mixed parameters."""
        url = "https://example.com/page?id=123&utm_source=newsletter&q=search&fbclid=abc"
        expected = "https://example.com/page?id=123&q=search"
        self.assertEqual(self.cleaner.clean_url(url), expected)
        
    def test_google_redirect(self):
        """Test cleaning a Google redirect URL."""
        url = "https://www.google.com/url?q=https://example.com/page?id=123&sa=D&source=editors"
        expected = "https://example.com/page?id=123"
        self.assertEqual(self.cleaner.clean_url(url), expected)
        
    def test_facebook_redirect(self):
        """Test cleaning a Facebook redirect URL."""
        url = "https://facebook.com/l.php?u=https://example.com/page?id=123&h=AT1234"
        expected = "https://example.com/page?id=123"
        self.assertEqual(self.cleaner.clean_url(url), expected)
        
    def test_whitelist_params(self):
        """Test whitelisting parameters."""
        cleaner = URLCleaner(whitelist_params={"utm_source"})
        url = "https://example.com/page?id=123&utm_source=newsletter&utm_medium=email"
        expected = "https://example.com/page?id=123&utm_source=newsletter"
        self.assertEqual(cleaner.clean_url(url), expected)
        
    def test_blacklist_params(self):
        """Test blacklisting parameters."""
        cleaner = URLCleaner(blacklist_params={"id"})
        url = "https://example.com/page?id=123&q=search"
        expected = "https://example.com/page?q=search"
        self.assertEqual(cleaner.clean_url(url), expected)
        
    def test_custom_tracking_params(self):
        """Test adding custom tracking parameters."""
        cleaner = URLCleaner(custom_tracking_params={"custom_track"})
        url = "https://example.com/page?id=123&custom_track=abc"
        expected = "https://example.com/page?id=123"
        self.assertEqual(cleaner.clean_url(url), expected)
        
    def test_custom_redirect_params(self):
        """Test adding custom redirect parameters."""
        cleaner = URLCleaner(custom_redirect_params={"example.com": ["goto"]})
        url = "https://example.com/goto?goto=https://target.com/page"
        expected = "https://target.com/page"
        self.assertEqual(cleaner.clean_url(url), expected)
        
    def test_nested_redirects(self):
        """Test handling nested redirects."""
        url = ("https://www.google.com/url?q=https://facebook.com/l.php"
               "?u=https://example.com/page%3Fid%3D123&h=AT1234&sa=D&source=editors")
        expected = "https://example.com/page?id=123"
        self.assertEqual(self.cleaner.clean_url(url), expected)


if __name__ == "__main__":
    unittest.main()