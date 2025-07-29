"""
Standardized Error Response Handler for MCP Testing Framework.

This module provides a standardized way to handle error responses in the MCP testing framework,
ensuring all error responses comply with the MCP specification by using "type": "text".
"""

import json
from typing import Any, Dict, List, Optional, Union


def create_error_response(error_message: str) -> Dict[str, Any]:
    """
    Create a standardized error response that complies with MCP specification.
    
    Instead of using "type": "error", which causes validation issues,
    this function creates a response with "type": "text" and formats the
    error message as JSON within the text field.
    
    Args:
        error_message: The error message to include in the response
        
    Returns:
        A dictionary with the standardized error response format
    """
    return {
        "type": "text",
        "text": json.dumps({"error": error_message})
    }


def format_validation_error(error_message: str) -> Dict[str, Any]:
    """
    Format a validation error message in a standardized way.
    
    Args:
        error_message: The validation error message
        
    Returns:
        A dictionary with the standardized error response format
    """
    return create_error_response(f"Validation error: {error_message}")


def format_tool_error(error_message: str) -> Dict[str, Any]:
    """
    Format a tool execution error message in a standardized way.
    
    Args:
        error_message: The tool execution error message
        
    Returns:
        A dictionary with the standardized error response format
    """
    return create_error_response(f"Tool execution error: {error_message}")


def is_error_response(response: Dict[str, Any]) -> bool:
    """
    Check if a response is an error response.
    
    This function checks both the new standardized format and the old
    non-compliant format to ensure backward compatibility during migration.
    
    Args:
        response: The response to check
        
    Returns:
        True if the response is an error response, False otherwise
    """
    # Check for isError flag
    if response.get("isError") is True:
        return True
    
    # Check for the new standardized format
    if response.get("type") == "text":
        try:
            text_content = json.loads(response.get("text", "{}"))
            if "error" in text_content:
                return True
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Check for the old non-compliant format
    if response.get("type") == "error":
        return True
    
    return False


def standardize_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize a response to ensure it complies with MCP specification.
    
    If the response uses the old non-compliant format with "type": "error",
    convert it to the new standardized format with "type": "text".
    
    Args:
        response: The response to standardize
        
    Returns:
        The standardized response
    """
    if response.get("type") == "error":
        return create_error_response(response.get("text", "Unknown error"))
    
    return response
