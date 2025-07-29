"""
Tests for the standardized error handler module.

This module tests the error_handler.py module to ensure it correctly
standardizes error responses according to the MCP specification.
"""

import json
import pytest

from mcp_client_cli.testing.error_handler import (
    create_error_response,
    format_validation_error,
    format_tool_error,
    is_error_response,
    standardize_response
)


def test_create_error_response():
    """Test creating a standardized error response."""
    response = create_error_response("Test error message")
    
    # Verify the response has the correct structure
    assert response["type"] == "text"
    assert "text" in response
    
    # Verify the error message is properly encoded in JSON
    error_data = json.loads(response["text"])
    assert "error" in error_data
    assert error_data["error"] == "Test error message"


def test_format_validation_error():
    """Test formatting a validation error message."""
    response = format_validation_error("Invalid input")
    
    # Verify the response has the correct structure
    assert response["type"] == "text"
    assert "text" in response
    
    # Verify the error message is properly formatted
    error_data = json.loads(response["text"])
    assert "error" in error_data
    assert error_data["error"] == "Validation error: Invalid input"


def test_format_tool_error():
    """Test formatting a tool execution error message."""
    response = format_tool_error("Tool failed")
    
    # Verify the response has the correct structure
    assert response["type"] == "text"
    assert "text" in response
    
    # Verify the error message is properly formatted
    error_data = json.loads(response["text"])
    assert "error" in error_data
    assert error_data["error"] == "Tool execution error: Tool failed"


def test_is_error_response():
    """Test detecting error responses in various formats."""
    # Test with isError flag
    assert is_error_response({"isError": True, "content": []})
    
    # Test with new standardized format
    assert is_error_response({
        "type": "text",
        "text": json.dumps({"error": "Test error"})
    })
    
    # Test with old non-compliant format
    assert is_error_response({
        "type": "error",
        "text": "Test error"
    })
    
    # Test with non-error response
    assert not is_error_response({
        "type": "text",
        "text": "Success message"
    })


def test_standardize_response():
    """Test standardizing responses to comply with MCP specification."""
    # Test with old non-compliant format
    old_response = {
        "type": "error",
        "text": "Test error"
    }
    
    standardized = standardize_response(old_response)
    
    # Verify the response has been standardized
    assert standardized["type"] == "text"
    assert "text" in standardized
    
    # Verify the error message is preserved
    error_data = json.loads(standardized["text"])
    assert "error" in error_data
    assert error_data["error"] == "Test error"
    
    # Test with already compliant response
    compliant_response = {
        "type": "text",
        "text": "Success message"
    }
    
    # Verify the response is unchanged
    assert standardize_response(compliant_response) == compliant_response
