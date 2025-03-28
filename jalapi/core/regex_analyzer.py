# regex_analyzer.py
"""
Regex-based analysis module for JALAPI.

This module provides functionality for discovering API endpoints in JavaScript code
using regular expression pattern matching.
"""

import re
from typing import List, Tuple

from jalapi.models.models import AuthInfo, Endpoint
from jalapi.logging.log_setup import logger
from jalapi.core.endpoint_processor import EndpointProcessor


class RegexAnalyzer:
    """Find API endpoints using regex patterns"""

    def __init__(self):
        # Patterns for finding API endpoints
        self.patterns = [
            # Axios
            r'axios\.(?:get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r'axios\s*\(\s*{\s*url:\s*[\'"`]([^\'"`]+)[\'"`]',
            # Fetch
            r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            r"fetch\s*\(\s*`([^`]+)`",
            # jQuery
            r'\$\.ajax\s*\(\s*{\s*url:\s*[\'"`]([^\'"`]+)[\'"`]',
            r'\$\.(get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
            # Common patterns
            r'url\s*:\s*[\'"`]([^\'"`]+)[\'"`]',
            r'endpoint\s*:\s*[\'"`]([^\'"`]+)[\'"`]',
            r'path\s*:\s*[\'"`]([^\'"`]+)[\'"`]',
            # API endpoints
            r'[\'"`](\/api\/[^\'"`]+)[\'"`]',
            r'[\'"`](\/v\d+\/[^\'"`]+)[\'"`]',
        ]

        # Simple auth detection patterns
        self.auth_patterns = [
            (r'Authorization\s*:\s*[\'"`]Bearer', "Bearer", "header"),
            (r"X-API-Key", "apiKey", "header"),
            (r"api[_-]?key", "apiKey", "query"),
            (r"token\s*:", "token", "body"),
        ]

    def discover_endpoints(self, js_content: str) -> List[Endpoint]:
        """
        Find all API endpoints in JavaScript code using regex pattern matching.
        
        Iterates through multiple regex patterns to identify API endpoints in the code,
        then extracts context to determine HTTP method and authentication requirements.
        
        Args:
            js_content (str): JavaScript code content to analyze
            
        Returns:
            List[Endpoint]: List of discovered API endpoints
        """
        endpoints = []
        seen_paths = set()

        for pattern in self.patterns:
            for match in re.finditer(pattern, js_content, re.IGNORECASE):
                # Extract path
                path = None
                for group in match.groups():
                    if group and ("/" in group or "api" in group.lower()):
                        path = group
                        break

                if not path:
                    continue

                # Normalize path
                path = EndpointProcessor.normalize_path(path)

                # Skip if not an endpoint or already seen
                if not EndpointProcessor.is_endpoint(path) or path in seen_paths:
                    continue

                seen_paths.add(path)

                # Get context for method and auth detection
                context = self._get_context(js_content, match.start(), 200)

                # Detect method
                method = "UNKNOWN"
                method_match = re.search(
                    r"(get|post|put|delete|patch)", context, re.IGNORECASE
                )
                if method_match:
                    method = method_match.group(1).upper()

                # Detect auth
                auth = self._detect_auth(context)

                # Calculate line number
                line_number = js_content[:match.start()].count('\n') + 1
                
                # Create endpoint
                endpoint = Endpoint(
                    path=path,
                    method=method,
                    auth=auth,
                    confidence=0.7,
                    detector="regex",
                    line_number=line_number
                )

                endpoints.append(endpoint)

        return endpoints

    def _get_context(self, content: str, position: int, window: int = 200) -> str:
        """
        Get a window of code surrounding a specific position.
        
        Args:
            content (str): The full JavaScript content
            position (int): Position in the content to center the window on
            window (int, optional): Total size of the context window. Defaults to 200.
            
        Returns:
            str: A substring of the content centered around the position
        """
        start = max(0, position - window // 2)
        end = min(len(content), position + window // 2)
        return content[start:end]

    def _detect_auth(self, context: str) -> AuthInfo:
        """
        Detect authentication requirements from the code context.
        
        Examines the surrounding code context to identify patterns that suggest
        authentication is required for an API endpoint.
        
        Args:
            context (str): Code context surrounding an API endpoint reference
            
        Returns:
            AuthInfo: Authentication information with details if detected
        """
        for pattern, auth_type, location in self.auth_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return AuthInfo(required=True, type=auth_type, location=location)

        # Generic auth detection
        if re.search(r"auth|token|jwt|apikey", context, re.IGNORECASE):
            return AuthInfo(required=True)

        return AuthInfo(required=False)
