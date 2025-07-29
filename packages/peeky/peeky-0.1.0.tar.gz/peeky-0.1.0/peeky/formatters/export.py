"""
Export functions for Peeky.

This module provides functions to export data in various formats.
"""

import json
import socket
import sys
from typing import Dict, List, Any, Optional

def clean_for_serialization(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean connection data for serialization (convert non-serializable types).
    
    Args:
        data: List of connection dictionaries
        
    Returns:
        Cleaned list of dictionaries
    """
    cleaned_data = []
    
    # Protocol mapping
    protocol_map = {
        socket.SOCK_STREAM: "TCP",
        socket.SOCK_DGRAM: "UDP"
    }
    
    for item in data:
        cleaned_item = {}
        
        # Process each field and make it serializable
        for key, value in item.items():
            # Handle protocol specifically
            if key == "protocol":
                cleaned_item[key] = protocol_map.get(value, str(value))
            # Handle lists and other complex types
            elif isinstance(value, (list, dict, set)):
                cleaned_item[key] = value
            # Handle everything else as strings
            else:
                cleaned_item[key] = str(value) if value is not None else None
        
        cleaned_data.append(cleaned_item)
    
    return cleaned_data


def format_as_text(data: List[Dict[str, Any]]) -> str:
    """
    Format connection data as plain text.
    
    Args:
        data: List of connection dictionaries
        
    Returns:
        Formatted text string
    """
    # Clean data first
    cleaned_data = clean_for_serialization(data)
    
    # Format as text
    text = "PEEKY CONNECTION EXPORT\n"
    text += "======================\n\n"
    
    for i, conn in enumerate(cleaned_data, 1):
        text += f"Connection {i}\n"
        text += "-" * (12 + len(str(i))) + "\n"
        
        # Format each field
        for key, value in conn.items():
            # Skip complex types or format them specially
            if isinstance(value, list):
                text += f"{key}: {', '.join(str(v) for v in value)}\n"
            elif isinstance(value, dict):
                text += f"{key}:\n"
                for subkey, subvalue in value.items():
                    text += f"  {subkey}: {subvalue}\n"
            else:
                text += f"{key}: {value}\n"
        
        text += "\n"
    
    return text


def write_export(data: List[Dict[str, Any]], output_file: Optional[str], format_type: str = "text") -> None:
    """
    Export connection data to the specified format.
    
    Args:
        data: List of connection dictionaries
        output_file: Output file path or None for stdout
        format_type: Export format ("json" or "text")
    """
    # Clean data for serialization
    cleaned_data = clean_for_serialization(data)
    
    # Format data
    if format_type == "json":
        output = json.dumps(cleaned_data, indent=2)
    else:  # text
        output = format_as_text(data)
    
    # Write to file or stdout
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Data exported to {output_file}")
    else:
        sys.stdout.write(output) 