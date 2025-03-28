# analysis_agent.py

import json
from typing import List, Dict, Any
import jsbeautifier

from jalapi.models.models import Endpoint
from jalapi.core.llm_analyzer import LLMAnalyzer
from jalapi.core.regex_analyzer import RegexAnalyzer
from jalapi.core.endpoint_processor import EndpointProcessor
from jalapi.logging.log_setup import logger


class JavaScriptAnalysisAgent:
    """Simple agent to discover API endpoints in JavaScript"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the JavaScript Analysis Agent.
        
        Args:
            config (Dict[str, Any]): Configuration parameters for the analysis process
        """
        logger.debug("Initializing JavaScript Analysis Agent")
        self.config = config
        self.regex = RegexAnalyzer()
        self.llm = LLMAnalyzer("anthropic", "claude-3-5-sonnet-20241022")

    def analyze(self, filepath: str) -> Dict[str, Any]:
        """
        Analyze a JavaScript file to find API endpoints.
        
        Performs analysis using both regex pattern matching and LLM-based analysis,
        then combines and deduplicates the results.
        
        Args:
            filepath (str): Path to the JavaScript file to analyze
            
        Returns:
            Dict[str, Any]: Analysis results containing source, summary, and endpoints
        """
        # Load JavaScript
        js_content = self._load_javascript(filepath)

        # Find endpoints using regex
        regex_endpoints = self.regex.discover_endpoints(js_content)

        # Find endpoints using LLM
        llm_endpoints = self.llm.analyze_endpoints(js_content, self.config)

        # Combine endpoints (deduplicating identical paths)
        all_endpoints = self._deduplicate_endpoints(regex_endpoints + llm_endpoints)

        # Generate basic stats
        stats = self._generate_stats(all_endpoints)

        return {
            "source": filepath,
            "summary": stats,
            "endpoints": [self._endpoint_to_dict(ep) for ep in all_endpoints],
        }

    def _load_javascript(self, filepath: str) -> str:
        """
        Load and process JavaScript content from a file.
        
        Args:
            filepath (str): Path to the JavaScript file to load
            
        Returns:
            str: The content of the JavaScript file, beautified if minified
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(filepath, "r", encoding="latin-1") as f:
                content = f.read()

        # Beautify minified files
        if len(content.split("\n")) < 10:
            try:
                content = jsbeautifier.beautify(content)
            except Exception as e:
                logger.error(f"Failed to beautify content: {e}")

        return content

    def _deduplicate_endpoints(self, endpoints: List[Endpoint]) -> List[Endpoint]:
        """
        Remove duplicate endpoints while properly preserving detector information.
        Ensures detector types are only counted once.
        """
        unique_endpoints = {}

        for endpoint in endpoints:
            key = (endpoint.path, endpoint.method)

            if key not in unique_endpoints:
                # First time seeing this endpoint
                unique_endpoints[key] = endpoint
            else:
                # This is a duplicate endpoint
                existing = unique_endpoints[key]

                # Parse existing detector types to avoid duplicates
                existing_detectors = set(existing.detector.split("+"))
                current_detector = endpoint.detector

                # Add the new detector if it's not already included
                if current_detector not in existing_detectors:
                    existing_detectors.add(current_detector)

                    # Sort detectors for consistent output
                    combined_detector = "+".join(sorted(existing_detectors))

                    # Use the highest confidence score
                    highest_confidence = max(existing.confidence, endpoint.confidence)

                    # Determine the best method to use
                    final_method = existing.method
                    if final_method == "UNKNOWN" and endpoint.method != "UNKNOWN":
                        final_method = endpoint.method

                    # Create a new endpoint with combined information
                    combined_endpoint = Endpoint(
                        path=endpoint.path,
                        method=final_method,
                        # Prefer auth info that says auth is required
                        auth=endpoint.auth if endpoint.auth.required else existing.auth,
                        confidence=highest_confidence,
                        detector=combined_detector,
                        # Combine context information if available
                        context=f"{existing.context or ''}\n{endpoint.context or ''}".strip(),
                    )

                    unique_endpoints[key] = combined_endpoint
                else:
                    # Same detector type, just keep the one with higher confidence
                    if endpoint.confidence > existing.confidence:
                        unique_endpoints[key] = endpoint

        return list(unique_endpoints.values())

    def _generate_stats(self, endpoints: List[Endpoint]) -> Dict[str, int]:
        """
        Generate statistics about the discovered endpoints.
        
        Computes various metrics about endpoint detection methods and authentication requirements.
        
        Args:
            endpoints (List[Endpoint]): List of discovered endpoints
            
        Returns:
            Dict[str, int]: Dictionary containing various statistics about the endpoints
        """

        # Initialize counters
        total_endpoints = len(endpoints)
        regex_findings = 0
        llm_findings = 0
        combined_findings = 0
        endpoints_with_auth = 0

        for ep in endpoints:
            # Check if detector is combined
            if "+" in ep.detector:
                combined_findings += 1
                # Also count in individual detector stats since both found it
                regex_findings += 1
                llm_findings += 1
            elif ep.detector == "regex":
                regex_findings += 1
            elif ep.detector == "llm":
                llm_findings += 1

            # Count endpoints with auth requirements
            if ep.auth.required:
                endpoints_with_auth += 1

        return {
            "total_endpoints": total_endpoints,
            "regex_findings": regex_findings,
            "llm_findings": llm_findings,
            "combined_findings": combined_findings,  # New stat
            "endpoints_with_auth": endpoints_with_auth,
        }

    def _endpoint_to_dict(self, endpoint: Endpoint) -> Dict[str, Any]:
        """
        Convert an Endpoint object to a dictionary for serialization.
        
        Args:
            endpoint (Endpoint): The endpoint object to convert
            
        Returns:
            Dict[str, Any]: Dictionary representation of the endpoint
        """
        result = {
            "path": endpoint.path,
            "method": endpoint.method,
            "detector": endpoint.detector,
            "confidence": endpoint.confidence,
        }

        # Include line number if available
        if endpoint.line_number is not None:
            result["line_number"] = endpoint.line_number
            
        # Include context/usage_context if available
        if endpoint.context:
            result["usage_context"] = endpoint.context

        if endpoint.auth.required:
            result["auth"] = {
                "required": endpoint.auth.required,
                "type": endpoint.auth.type,
                "location": endpoint.auth.location,
            }

        return result
