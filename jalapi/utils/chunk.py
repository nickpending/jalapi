# chunk.py
"""
Code chunking utilities for JALAPI.

This module provides functions for breaking large JavaScript files into
manageable chunks for analysis, while preserving context and ensuring
critical configuration sections are included.
"""

import re
from typing import List, Dict, Optional, Tuple


def chunk_code(code: str, max_chunk_size: int = 4000) -> List[Tuple[str, str]]:
    """
    Break code into analyzable chunks with context preservation.
    
    Splits code primarily at function boundaries to preserve logical units,
    and includes context information with each chunk.
    
    Args:
        code (str): JavaScript code to chunk
        max_chunk_size (int, optional): Maximum size of each chunk. Defaults to 4000.
        
    Returns:
        List[Tuple[str, str]]: List of (chunk, context) tuples where context contains
                              relevant surrounding code for better analysis
    """
    # Split on function boundaries or large blocks
    chunks = []
    lines = code.split("\n")
    current_chunk = []
    current_context = []

    for line in lines:
        # Look for function/block starts
        if re.match(
            r"^\s*(async\s+)?function|^\s*const\s+\w+\s*=\s*(?:async\s+)?function",
            line,
        ):
            if current_chunk:
                chunks.append(
                    ("\n".join(current_chunk), "\n".join(current_context[-5:]))
                )
            current_chunk = []
            current_context = []
        current_chunk.append(line)
        # Keep last 5 lines as context
        if len(line.strip()) > 0:
            current_context.append(line)
            if len(current_context) > 5:
                current_context.pop(0)

        # Check chunk size and split if needed
        if len("\n".join(current_chunk)) > max_chunk_size:
            chunks.append(("\n".join(current_chunk), "\n".join(current_context[-5:])))
            current_chunk = []
            current_context = []

    if current_chunk:
        chunks.append(("\n".join(current_chunk), "\n".join(current_context[-5:])))

    return chunks


def simple_chunk_code(code: str, max_size: int = 3000, overlap: int = 1000) -> List[Tuple[str, str, int]]:
    """
    Improved chunking with better overlap and context preservation.
    
    Splits code at logical boundaries with overlap between chunks, and extracts
    configuration sections to include as context with each chunk for better analysis.
    
    Args:
        code (str): JavaScript code to chunk
        max_size (int, optional): Maximum size of each chunk. Defaults to 3000.
        overlap (int, optional): Overlap size between consecutive chunks. Defaults to 1000.
        
    Returns:
        List[Tuple[str, str, int]]: List of (chunk, context, start_line) tuples where:
                                  - chunk: the code segment
                                  - context: configuration objects that define URLs/endpoints
                                  - start_line: the starting line number of the chunk
    """
    chunks = []
    start = 0

    # Find key configuration objects that define URLs/endpoints
    config_matches = list(
        re.finditer(
            r"const\s+(?:CONFIG|config|API|api|endpoints|ENDPOINTS|routes|ROUTES)\s*=",
            code,
        )
    )
    config_sections = []

    for match in config_matches:
        # Extract roughly 500 chars after the config definition
        config_start = match.start()
        config_end = min(match.end() + 500, len(code))
        config_sections.append(code[config_start:config_end])

    config_context = "\n\n".join(config_sections)

    while start < len(code):
        end = min(start + max_size, len(code))

        # Try to end at logical boundaries
        if end < len(code):
            for delimiter in ["\n}", "\n});", "\n  });", "\n    });"]:
                last_delimiter = code.rfind(delimiter, start, end)
                if last_delimiter > start:
                    end = last_delimiter + len(delimiter)
                    break

        chunk = code[start:end]

        # Calculate starting line number of this chunk
        start_line = code[:start].count('\n') + 1
        
        # Add config context to each chunk
        if config_context:
            context = f"IMPORTANT CONFIGURATION:\n{config_context}"
        else:
            context = ""

        chunks.append((chunk, context, start_line))

        # Ensure we make meaningful progress but maintain overlap
        progress = max(max_size // 3, max_size - overlap)
        start = min(end, start + progress)

    return chunks
