"""
URL Cleaner module for Sanitizr.

This module handles the core functionality of URL cleaning including:
- Query parameter cleaning
- Redirection decoding
- Parameter whitelisting/blacklisting
- Custom domain handling
"""

import re
import urllib.parse
from typing import Dict, List, Optional, Set, Union


class URLCleaner:
    """Core URL cleaning engine for Sanitizr."""

    # Known redirect parameters by domain
    DEFAULT_REDIRECT_PARAMS = {
        "google.com": ["url", "q"],
        "facebook.com": ["u"],
        "youtube.com": ["q"],
        "linkedin.com": ["url"],
        "t.co": [],  # Twitter's URL shortener needs special handling
    }

    # Common tracking parameters to remove
    DEFAULT_TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "fbclid", "gclid", "ocid", "ncid", "mc_cid", "mc_eid",
        "yclid", "dclid", "_hsenc", "_hsmi", "igshid", "mkt_tok",
        "soc_src", "soc_trk", "wt_mc", "WT.mc_id", "ref", "referrer",
        "WT.tsrc", "_ga", "ref_src", "ref_url", "ref_map",
        "rb_clickid", "s_cid", "zanpid", "guccounter", "_openstat"
    }

    def __init__(
        self,
        config: Optional[Dict] = None,
        custom_tracking_params: Optional[Set[str]] = None,
        custom_redirect_params: Optional[Dict[str, List[str]]] = None,
        whitelist_params: Optional[Set[str]] = None,
        blacklist_params: Optional[Set[str]] = None,
    ):
        """
        Initialize the URL cleaner with optional configuration.

        Args:
            config: Dictionary containing configuration options
            custom_tracking_params: Additional tracking parameters to remove
            custom_redirect_params: Additional redirect parameters by domain
            whitelist_params: Parameters to keep regardless of other settings
            blacklist_params: Parameters to always remove
        """
        self.tracking_params = self.DEFAULT_TRACKING_PARAMS.copy()
        self.redirect_params = self.DEFAULT_REDIRECT_PARAMS.copy()
        
        # Update with custom parameters if provided
        if custom_tracking_params:
            self.tracking_params.update(custom_tracking_params)
            
        if custom_redirect_params:
            for domain, params in custom_redirect_params.items():
                if domain in self.redirect_params:
                    self.redirect_params[domain].extend(params)
                else:
                    self.redirect_params[domain] = params
                    
        self.whitelist_params = whitelist_params or set()
        self.blacklist_params = blacklist_params or set()
        
    def clean_url(self, url: str) -> str:
        """
        Clean a URL by handling redirects and removing tracking parameters.
        
        Args:
            url: The URL to clean
            
        Returns:
            The cleaned URL
        """
        # Basic URL validation
        if not url or not isinstance(url, str):
            return ""
            
        # Try to parse the URL
        try:
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.netloc:  # No domain
                return url
        except Exception:
            return url
            
        # First, handle redirections
        cleaned_url = self._decode_redirects(url)
        
        # Then clean parameters
        return self._clean_parameters(cleaned_url)
    
    def _get_domain(self, url: str) -> str:
        """Extract the base domain from a URL."""
        try:
            netloc = urllib.parse.urlparse(url).netloc
            # Remove 'www.' prefix if present
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return ""
    
    def _decode_redirects(self, url: str) -> str:
        """
        Decode redirect URLs (like Google search results, Facebook t.co links).
        
        Args:
            url: The URL to decode
            
        Returns:
            Decoded URL if it was a redirect, original URL otherwise
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = self._get_domain(url)
            
            # Special case for t.co (Twitter)
            if domain == "t.co":
                # Would need to actually follow the URL to get the real destination
                # For now, we'll just return as is
                return url
                
            # Check if this domain has known redirect parameters
            if domain in self.redirect_params:
                query_params = urllib.parse.parse_qs(parsed_url.query)
                
                # Try each known redirect parameter
                for param in self.redirect_params[domain]:
                    if param in query_params and query_params[param]:
                        redirect_url = query_params[param][0]
                        if redirect_url:
                            # Make sure the redirect URL is valid
                            try:
                                redirect_parsed = urllib.parse.urlparse(redirect_url)
                                if redirect_parsed.scheme and redirect_parsed.netloc:
                                    # Recursively clean the redirect URL
                                    return self.clean_url(redirect_url)
                            except Exception:
                                pass
            
            return url
        except Exception:
            return url
            
    def _clean_parameters(self, url: str) -> str:
        """
        Remove tracking parameters from a URL.
        
        Args:
            url: The URL to clean
            
        Returns:
            URL with tracking parameters removed
        """
        try:
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.query:
                return url
                
            # Parse query parameters
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # Filter parameters
            filtered_params = {}
            for param, values in query_params.items():
                # Keep parameter if it's whitelisted
                if param in self.whitelist_params:
                    filtered_params[param] = values
                # Remove parameter if it's blacklisted or in tracking params
                elif param not in self.blacklist_params and param not in self.tracking_params:
                    filtered_params[param] = values
                    
            # Rebuild the query string
            new_query = urllib.parse.urlencode(filtered_params, doseq=True)
            
            # Rebuild the URL with the new query string
            clean_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            return clean_url
        except Exception:
            return url
