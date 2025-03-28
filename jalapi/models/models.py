# models.py
"""
Data models for the JALAPI system.

This module contains dataclass definitions used throughout the application
to represent API endpoints and related information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthInfo:
    """
    Represents authentication information for an API endpoint.
    
    Attributes:
        required (bool): Whether authentication is required for the endpoint
        type (Optional[str]): The type of authentication (e.g., "Bearer", "Basic", "OAuth")
        location (Optional[str]): Where authentication is applied (e.g., "header", "query", "body")
    """

    required: bool = False
    type: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Endpoint:
    """
    Represents an API endpoint discovered during analysis.
    
    Attributes:
        path (str): The URL path of the endpoint
        method (str): The HTTP method (GET, POST, etc.) or "UNKNOWN" if not determined
        auth (Optional[AuthInfo]): Authentication information for this endpoint
        confidence (float): Confidence score (0.0-1.0) for this discovery
        detector (str): Detection method used ("regex", "llm", or combinations like "regex+llm")
        context (Optional[str]): Additional context about how/where the endpoint was found
        line_number (Optional[int]): Line number in the source file where the endpoint was found
    """

    path: str
    method: str = "UNKNOWN"
    auth: Optional[AuthInfo] = None
    confidence: float = 1.0
    detector: str = "regex"
    context: Optional[str] = None
    line_number: Optional[int] = None

    def __post_init__(self):
        """
        Initialize auth attribute if not provided.
        
        This method is automatically called after the dataclass is initialized.
        It ensures that the auth attribute is never None by setting it to a
        default AuthInfo instance if needed.
        """
        if self.auth is None:
            self.auth = AuthInfo()
