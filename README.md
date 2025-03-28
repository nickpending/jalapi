# JALAPI: JavaScript API Analyzer

## Overview

JALAPI is a sophisticated system for discovering and analyzing API endpoints in JavaScript code. It uses a combination of regex pattern matching and LLM-based analysis to identify API endpoints, authentication methods, and potential security vulnerabilities.

## Key Features

- Automated JavaScript API endpoint discovery
- Multi-agent architecture for comprehensive analysis
- Regex-based pattern identification
- LLM-powered semantic analysis
- Security-focused vulnerability detection
- Authentication flow mapping

## Upcoming Features

- Name/value pair extraction from requests
- Header analysis, especially authorization headers
- FQDN (Fully Qualified Domain Name) detection
- GraphQL operation discovery
- WebSocket endpoint identification
- Cross-reference ID usage across endpoints
- Role-based access pattern detection

## Components

- **JavaScript Analysis Agent**: Extracts API-related patterns from JavaScript code
- **Regex Analyzer**: Uses pattern matching to identify endpoints
- **LLM Analyzer**: Employs large language models for semantic understanding
- **Endpoint Processor**: Consolidates findings from various analysis methods

## Getting Started

### Prerequisites

- Python 3.8+
- Required Python packages (see requirements.txt)

### Installation

```bash
# Clone the repository
git clone <repository-url>

# Navigate to the project directory
cd jalapi

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Basic usage
python main.py --js <javascript-file-path>

# Enable debug logging
python main.py --js <javascript-file-path> --debug

# Output results to a JSON file
python main.py --js <javascript-file-path> --output results.json

# Output results as JSON to stdout
python main.py --js <javascript-file-path> --json

# Use a custom configuration file
python main.py --js <javascript-file-path> --config custom_config.yaml
```

## Configuration

Configuration is managed through the `config.yaml` file, which includes:

- System prompts for LLM analysis
- Analysis settings and parameters
- Logging configuration

## Architecture

The system follows a modular architecture as outlined in the master-plan.md file, with specialized components working together to provide comprehensive API analysis.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the project.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.