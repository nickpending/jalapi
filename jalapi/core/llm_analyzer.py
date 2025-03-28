# llm_analyzer.py

import json
import voidwire_parlai

from typing import List, Dict, Optional, Tuple, Any

from jalapi.utils.chunk import chunk_code, simple_chunk_code
from jalapi.models.models import AuthInfo, Endpoint
from jalapi.logging.log_setup import logger
from jalapi.core.endpoint_processor import EndpointProcessor


class LLMAnalyzerError(Exception):
    """Base exception for SecurityAssistant-specific errors"""

    pass


class LLMAnalyzer:
    """
    Responsible for sending javascript to an LLM for endpoint
    extraction.
    """

    def __init__(self, provider: str, model: str, debug: bool = False):
        """
        Initialize the LLM Analyzer with the specified provider and model.
        
        Args:
            provider (str): The name of the LLM provider (e.g., "anthropic")
            model (str): The specific model to use (e.g., "claude-3-5-sonnet-20241022")
            debug (bool, optional): Whether to enable debug mode. Defaults to False.
        """
        logger.debug("Initializing LLM Analyzer")
        self.model = model
        self.client = voidwire_parlai.create_provider(provider)

    def analyze_endpoints(self, js: str, config: Dict[str, Any]) -> List[Endpoint]:
        """
        Analyze JavaScript code to identify API endpoints using a language model.
        
        Args:
            js (str): JavaScript code to analyze
            config (Dict[str, Any]): Configuration for the analysis, including prompts
            
        Returns:
            List[Endpoint]: List of discovered API endpoints
        """
        logger.debug("Starting enhanced LLM analysis")
        all_endpoints = []
        chunks = simple_chunk_code(js)
        system_prompt = config["system_prompt"]
        analysis_prompt = config["analysis_prompt"]

        for chunk, context, start_line in chunks:
            logger.debug(f"Context: #{context}")
            ap = analysis_prompt.format(code_chunk=chunk, context=context)
            logger.debug(ap)
            try:
                logger.debug(f"Analyzing chunk of size {len(chunk)}")
                response = self.client.chat(
                    self.model,
                    "",
                    ap,
                    system_prompt,
                )

                logger.debug("LLM Response:")
                logger.debug(response)

                for ep in response["endpoints"]:
                    if not isinstance(ep, dict) or "path" not in ep:
                        continue

                    # Enhanced confidence scoring
                    base_confidence = ep.get("confidence", 0.8)
                    # Boost confidence for well-evidenced endpoints
                    if ep.get("evidence") and ep.get("usage_context"):
                        base_confidence = min(1.0, base_confidence + 0.1)

                    auth_info = AuthInfo(
                        required=ep.get("auth", {}).get("required", False),
                        type=ep.get("auth", {}).get("type"),
                        location=ep.get("auth", {}).get("location"),
                    )

                    # Get relative line number from LLM if available, or use chunk start line
                    relative_line = ep.get("line_number", 0)
                    if relative_line > 0:
                        # If LLM provided a line number within the chunk, add it to chunk start line
                        absolute_line = start_line + relative_line - 1
                    else:
                        # Otherwise just use chunk start line
                        absolute_line = start_line
                    
                    endpoint = Endpoint(
                        path=ep["path"],
                        method=ep.get("method", "UNKNOWN"),
                        auth=auth_info,
                        confidence=base_confidence,
                        detector="llm",
                        context=ep.get("usage_context", ep.get("evidence", "")),
                        line_number=absolute_line
                    )

                    # Only add if it's a valid endpoint
                    # if EndpointProcessor.is_endpoint(endpoint.path):
                    all_endpoints.append(endpoint)

            except Exception as e:
                logger.error(f"Unexpected error in LLM analysis: {e}")
                logger.debug(f"Error details: {str(e)}")

        logger.info(f"LLM analysis complete - found {len(all_endpoints)} endpoints")
        return all_endpoints
