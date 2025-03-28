# endpoint_processor.py
"""
Endpoint processing module for JALAPI.

This module provides utilities for processing, normalizing, and validating API endpoints
found during analysis.
"""

import re
from typing import List, Dict, Any


class EndpointProcessor:
    """Utility class for processing and normalizing API endpoints."""
    @staticmethod
    def normalize_path(url: str) -> str:
        """
        Normalize API endpoint paths to a consistent format.
        
        Args:
            url (str): The URL or path to normalize
            
        Returns:
            str: Normalized path with consistent formatting
        """
        # Convert template variables
        url = re.sub(r"\${([^}]+)}", r"{\1}", url)

        # Strip quotes
        url = url.strip("`'\"")

        # Normalize slashes
        url = re.sub(r"/+", "/", url)

        return url

    @staticmethod
    def is_endpoint(url: str) -> bool:
        """
        Determine if a URL string is likely an API endpoint.
        
        Uses pattern matching against common API path patterns to identify
        whether a URL represents an actual API endpoint.
        
        Args:
            url (str): The URL or path to check
            
        Returns:
            bool: True if the URL likely represents an API endpoint, False otherwise
        """
        # Normalize the URL string
        url = url.strip("`'\"")

        # More comprehensive patterns for API endpoints
        api_patterns = [
            r"/api/",
            r"/v\d+/",
            r"/graphql",
            r"/rest/",
            r"/auth/",
            r"/oauth2?/",
            r"/rpc/",
            r"/webhook",
            r"/data",
            r"/service",
            r"/events?/",
            r"/users?/",
            r"/\w+/\{\w+\}",  # Parameterized routes
            r"/ml[-/]",
            r"/sync",
            r"/reports?/",
            r"/tasks/",
            r"/export/",
            r"/version-info/",
            r"/features/",
            r"/preferences",
            r"/profile$",
            r"/activity/",
            r"/mfa/",
            r"/challenge$",
            r"/predict$",
            r"/token$",
            r"/refresh$",
            r"/revoke$",
            r"/test$",
        ]

        # Simply check if the URL contains any of these patterns
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in api_patterns)
