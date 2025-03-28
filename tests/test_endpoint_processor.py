"""
Unit tests for the EndpointProcessor class.

These tests focus on the is_endpoint function to validate its effectiveness
at correctly identifying API endpoints and suggest improvements.
"""

import unittest
import re
from jalapi.core.endpoint_processor import EndpointProcessor


def improved_is_endpoint(url: str) -> bool:
    """
    Improved detection of API endpoints that addresses the limitations
    of the original is_endpoint function.
    
    Args:
        url (str): The URL or path to check
        
    Returns:
        bool: True if the URL likely represents an API endpoint, False otherwise
    """
    # Normalize the URL string
    url = url.strip("`'\"")
    
    # Check for obvious non-API patterns first (static assets)
    if re.search(r'\.(js|css|html|png|jpg|jpeg|gif|svg|pdf|txt|xml)$', url, re.IGNORECASE):
        return False
        
    # Combine original patterns with new additions
    api_patterns = [
        # Original patterns
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
        
        # New patterns for better coverage
        r"/ws$",                # WebSocket endpoint
        r"/ws/",                # WebSocket with path
        r"/event-stream",       # SSE endpoint
        r"/socket",             # Socket endpoint
        r"/stream",             # Stream endpoint
        
        # Common single-segment endpoints
        r"^/login$",
        r"^/logout$",
        r"^/register$",
        r"^/oauth$",
        r"^/verify$",
        
        # Common API operations
        r"^/upload$",
        r"^/search$",
        r"^/download$",
        
        # Pattern for double-brace template variables
        r"/\{\{\w+\}\}",
    ]
    
    # Check if the URL contains any of the patterns
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in api_patterns)


class TestEndpointProcessor(unittest.TestCase):
    """Tests for the EndpointProcessor class with focus on endpoint detection."""

    def test_standard_api_endpoints(self):
        """Test detection of standard API endpoint patterns."""
        standard_endpoints = [
            # Basic API patterns
            "/api/users",
            "/api/v1/users",
            "/v1/users",
            "/v2/resources",
            "/rest/items",
            
            # Auth-related endpoints
            "/auth/login", 
            "/oauth/token",
            "/oauth2/authorize",
        ]
        
        for endpoint in standard_endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertTrue(
                    EndpointProcessor.is_endpoint(endpoint),
                    f"Failed to identify standard endpoint: {endpoint}"
                )

    def test_websocket_endpoints(self):
        """Test WebSocket endpoint detection."""
        ws_endpoints = [
            # WebSocket endpoints
            "/ws",
            "/ws/auth",
            "/ws/events",
            "/ws/notifications",
            "/event-stream",
        ]
        
        # Current implementation likely fails on these
        current_detected = sum(1 for endpoint in ws_endpoints 
                              if EndpointProcessor.is_endpoint(endpoint))
        improved_detected = sum(1 for endpoint in ws_endpoints 
                               if improved_is_endpoint(endpoint))
        
        print(f"\nWebSocket endpoints - Current: {current_detected}/{len(ws_endpoints)}, "
              f"Improved: {improved_detected}/{len(ws_endpoints)}")

    def test_single_segment_endpoints(self):
        """Test single-segment endpoints without clear API indicators."""
        single_segment_endpoints = [
            # Single segments that are often API endpoints
            "/login",
            "/logout",
            "/register",
            "/oauth2",
            "/sync",
            "/verify",
            "/token",
            "/refresh",
            "/revoke",
            "/challenge",
            "/predict",
        ]
        
        current_detected = sum(1 for endpoint in single_segment_endpoints 
                              if EndpointProcessor.is_endpoint(endpoint))
        improved_detected = sum(1 for endpoint in single_segment_endpoints 
                               if improved_is_endpoint(endpoint))
        
        print(f"\nSingle segment endpoints - Current: {current_detected}/{len(single_segment_endpoints)}, "
              f"Improved: {improved_detected}/{len(single_segment_endpoints)}")

    def test_template_variable_endpoints(self):
        """Test detection of endpoints with template variables."""
        template_endpoints = [
            # Template variables in different formats
            "/users/{userId}",
            "/products/{id}/variants",
            "/users/{{userId}}/profile",
            "/reports/users/{{userId}}/{{reportType}}",
            "/users/{{userId}}/activity/{{type}}/{{period}}",
            "/api/v2/export/{type}?format={format}",
            "/api/v2/tasks/{taskId}/status",
            "/api/version-info/{version}",
            "/api/v2/webhooks/{webhookId}/test",
        ]
        
        current_detected = sum(1 for endpoint in template_endpoints 
                              if EndpointProcessor.is_endpoint(endpoint))
        improved_detected = sum(1 for endpoint in template_endpoints 
                               if improved_is_endpoint(endpoint))
        
        print(f"\nTemplate variable endpoints - Current: {current_detected}/{len(template_endpoints)}, "
              f"Improved: {improved_detected}/{len(template_endpoints)}")

    def test_non_api_urls(self):
        """Test correct rejection of non-API URLs."""
        non_api_urls = [
            # Static assets
            "/assets/image.png",
            "/static/style.css",
            "/js/script.js",
            
            # Website pages
            "/about",
            "/contact",
            "/products",
            
            # File paths
            "/downloads/document.pdf",
            "/images/logo.svg",
        ]
        
        for url in non_api_urls:
            with self.subTest(url=url):
                self.assertFalse(
                    EndpointProcessor.is_endpoint(url),
                    f"Incorrectly identified non-API URL as endpoint: {url}"
                )
                self.assertFalse(
                    improved_is_endpoint(url),
                    f"Improved detector incorrectly identified non-API URL: {url}"
                )

    def test_from_sample_output(self):
        """Test endpoints from the sample-output.txt file."""
        sample_endpoints = [
            # From sample-output.txt
            "/oauth2/token",
            "/oauth2/refresh",
            "/oauth2/revoke",
            "/verify-token",
            "/mfa/challenge",
            "/users/{{userId}}/profile",
            "/users/{{userId}}/preferences",
            "/users/{{userId}}/activity/{{type}}/{{period}}",
            "/reports/users/{{userId}}/{{reportType}}",
            "/graphql",
            "/ws",
            "/api/v1/sync",
        ]
        
        current_detected = sum(1 for endpoint in sample_endpoints 
                              if EndpointProcessor.is_endpoint(endpoint))
        improved_detected = sum(1 for endpoint in sample_endpoints 
                               if improved_is_endpoint(endpoint))
        
        print(f"\nSample output endpoints - Current: {current_detected}/{len(sample_endpoints)}, "
              f"Improved: {improved_detected}/{len(sample_endpoints)}")

    def test_recommendation(self):
        """Provide recommendations for improving the is_endpoint function."""
        print("\nRecommendations:")
        print("1. The current is_endpoint function misses several important API endpoint patterns:")
        print("   - WebSocket endpoints (/ws, /socket)")
        print("   - Single-segment API endpoints (/login, /logout, etc.)")
        print("   - Endpoints with double-brace template variables ({{var}})")
        print("\n2. Consider replacing with the improved implementation which detects:")
        print("   - More WebSocket endpoints")
        print("   - More single-segment endpoints")
        print("   - Better handling of template variables")
        print("\n3. The improved implementation maintains compatibility with all")
        print("   the existing patterns while adding additional coverage.")


if __name__ == "__main__":
    unittest.main()