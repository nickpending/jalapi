#!/usr/bin/env python3
"""
JALAPI - JavaScript API Analyzer

Main script for running the JavaScript API analyzer. This script provides a command-line
interface for analyzing JavaScript files to discover API endpoints.
"""

import argparse
import json

from jalapi.core.analysis_agent import JavaScriptAnalysisAgent
from jalapi.config.config_manager import load_config
from jalapi.logging.log_setup import setup_logging


def main():
    """Main entry point for the JALAPI application.
    
    Parses command-line arguments, sets up logging, initializes the analysis agent,
    and runs the analysis process. Outputs results to console (in human-readable or JSON format)
    and optionally to a file.
    
    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="JavaScript API Endpoint Discovery")
    parser.add_argument("--js", required=True, help="JavaScript file to analyze")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument(
        "--config", type=str, default="config.yaml", help="Path to configuration file"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON instead of human-readable format"
    )
    args = parser.parse_args()

    try:
        setup_logging(debug=args.debug)
        config = load_config(args.config)

        agent = JavaScriptAnalysisAgent(config)
        results = agent.analyze(args.js)

        # Output as JSON if requested
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Print human-readable summary
            print("\nAnalysis Summary:")
            print(f"Total Endpoints: {results['summary']['total_endpoints']}")
            print(f"Found by Regex: {results['summary']['regex_findings']}")
            print(f"Found by LLM: {results['summary']['llm_findings']}")

            # Print endpoints
            print("\nDiscovered Endpoints:")
            for endpoint in results["endpoints"]:
                print(f"\n  Path: {endpoint['path']}")
                print(f"  Method: {endpoint['method']}")
                print(f"  Detector: {endpoint['detector']}")
                print(f"  Confidence: {endpoint['confidence']}")
                
                # Display line number if available
                if 'line_number' in endpoint:
                    print(f"  Line: {endpoint['line_number']}")

                if "auth" in endpoint:
                    print(f"  Auth Required: {endpoint['auth']['required']}")
                    if endpoint["auth"].get("type"):
                        print(f"  Auth Type: {endpoint['auth']['type']}")
                    if endpoint["auth"].get("location"):
                        print(f"  Auth Location: {endpoint['auth']['location']}")

        # Save to file if output path provided
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            if not args.json:
                print(f"\nFull results saved to {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            raise


if __name__ == "__main__":
    main()
