import asyncio
import json
import pytest
from unittest.mock import MagicMock, AsyncMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the package structure
from src.mcp_client_and_server.server import (
    handle_initialize, 
    handle_ping, 
    handle_list_resources,
    handle_list_prompts,
    handle_list_tools,
    handle_read_resource,
    handle_call_tool,
    server_instance
)
from mcp.server import request_ctx
import mcp.types as types
import mcp.server as server

class MockRequestContext:
    def __init__(self, progress_token=None):
        self.meta = MagicMock()
        self.meta.progressToken = progress_token
        self.session = AsyncMock()
        self.session.send_progress_notification = AsyncMock()

@pytest.mark.asyncio
async def test_initialize_request():
    """Test that initialize request returns expected response with correct fields."""
    # Create mock request context
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Call initialize handler
    result = await handle_initialize(None)

    # Verify response structure and required fields
    assert isinstance(result, dict)
    assert "capabilities" in result
    assert isinstance(result["capabilities"], dict)
    
    assert "protocolVersion" in result
    assert isinstance(result["protocolVersion"], str)
    
    assert "serverInfo" in result
    assert isinstance(result["serverInfo"], dict)
    assert "name" in result["serverInfo"]
    assert result["serverInfo"]["name"] == "notes-server"

@pytest.mark.asyncio
async def test_initialize_request_with_options():
    """Test initialize request with initialization options."""
    # Create mock request context
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Create test options
    test_options = {
        "capabilities": {
            "test": True
        }
    }

    # Call initialize handler with options
    result = await handle_initialize(test_options)

    # Verify response structure and required fields
    assert isinstance(result, dict)
    assert "capabilities" in result
    assert isinstance(result["capabilities"], dict)
    
    assert "protocolVersion" in result
    assert isinstance(result["protocolVersion"], str)
    
    assert "serverInfo" in result
    assert isinstance(result["serverInfo"], dict)
    assert "name" in result["serverInfo"]
    assert "version" in result["serverInfo"]

@pytest.mark.asyncio
async def test_initialize_request_with_invalid_options():
    """Test initialize request with invalid options."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Test with invalid option types
    invalid_options = [
        {"capabilities": "not_a_dict"},  # capabilities should be a dict
        {"protocolVersion": 123},  # protocol version should be string
        {"serverInfo": "not_a_dict"}  # server info should be a dict
    ]

    for options in invalid_options:
        with pytest.raises(ValueError):
            await handle_initialize(options)

@pytest.mark.asyncio
async def test_initialize_request_with_malformed_data():
    """Test initialize request with malformed data."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Test with various malformed inputs
    malformed_inputs = [
        123,  # Not a dict
        "string",  # Not a dict
        [],  # Not a dict
        {"unexpected_key": "value"},  # Unexpected key
    ]

    for options in malformed_inputs:
        with pytest.raises((TypeError, ValueError)):
            await handle_initialize(options)

@pytest.mark.asyncio
async def test_ping_request():
    """Test that ping request returns empty response."""
    # Create mock request context
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Call ping handler
    result = await handle_ping()

    # Verify empty response
    assert result == {}

@pytest.mark.asyncio
async def test_ping_request_with_params():
    """Test that ping request ignores any parameters passed."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Test with various parameter types
    test_params = [
        {"param": "value"},
        123,
        "string",
        [],
        None
    ]

    for params in test_params:
        result = await handle_ping(params)
        assert result == {}, f"Ping should return empty dict even with params: {params}"

@pytest.mark.asyncio
async def test_list_resources_empty():
    """Test that resources/list returns empty list when no resources are defined."""
    # Create mock request context
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Call list_resources handler
    result = await handle_list_resources()

    # Verify response structure and content
    assert isinstance(result, list), "Response should be a list"
    assert len(result) == 0, "Response should be an empty list"

@pytest.mark.asyncio
async def test_list_resources_response_structure():
    """Test that resources/list returns correct response structure even when empty."""
    # Create mock request context
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Call list_resources handler
    result = await handle_list_resources()

    # Verify response is a list
    assert isinstance(result, list), "Response should be a list"

    # Verify each resource in the list (if any) has the correct structure
    for resource in result:
        assert isinstance(resource, types.Resource), "Each item should be a Resource type"
        assert hasattr(resource, "uri"), "Resource should have uri field"
        assert hasattr(resource, "title"), "Resource should have title field"
        assert hasattr(resource, "supportedMethods"), "Resource should have supportedMethods field"
        assert isinstance(resource.supportedMethods, list), "supportedMethods should be a list"

@pytest.mark.asyncio
async def test_list_prompts_empty():
    """Test that prompts/list returns empty list when no prompts are defined."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    result = await handle_list_prompts()

    # Verify response is a list and empty
    assert isinstance(result, list), "Response should be a list"
    assert len(result) == 0, "Response should be an empty list"

@pytest.mark.asyncio
async def test_list_prompts_response_structure():
    """Test that prompts/list returns correct response structure even when empty."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    result = await handle_list_prompts()

    # Verify response is a list
    assert isinstance(result, list), "Response should be a list"

    # Verify each prompt in the list (if any) has the correct structure
    for prompt in result:
        assert isinstance(prompt, types.Prompt), "Each item should be a Prompt type"
        assert hasattr(prompt, "name"), "Prompt should have name field"
        assert hasattr(prompt, "description"), "Prompt should have description field"
        assert hasattr(prompt, "parameters"), "Prompt should have parameters field"
        assert isinstance(prompt.parameters, dict), "parameters should be a dict"

@pytest.mark.asyncio
async def test_list_tools_empty():
    """Test that tools/list returns empty list when no tools are defined."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    result = await handle_list_tools()

    # Verify response is a list and empty
    assert isinstance(result, list), "Response should be a list"
    assert len(result) == 0, "Response should be an empty list"

@pytest.mark.asyncio
async def test_list_tools_response_structure():
    """Test that tools/list returns correct response structure even when empty."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    result = await handle_list_tools()

    # Verify response is a list
    assert isinstance(result, list), "Response should be a list"

    # Verify each tool in the list (if any) has the correct structure
    for tool in result:
        assert isinstance(tool, types.Tool), "Each item should be a Tool type"
        assert hasattr(tool, "name"), "Tool should have name field"
        assert hasattr(tool, "description"), "Tool should have description field"
        assert hasattr(tool, "parameters"), "Tool should have parameters field"
        assert isinstance(tool.parameters, dict), "parameters should be a dict"

@pytest.mark.asyncio
async def test_read_resource_failure():
    """Test that resources/read returns error for non-existent resource."""
    # Create mock request context
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Test with non-existent resource
    with pytest.raises(ValueError) as exc_info:
        await handle_read_resource(types.AnyUrl("notes://non-existent"))
    assert "Unknown resource path: non-existent" in str(exc_info.value)

    # Test with invalid scheme
    with pytest.raises(ValueError) as exc_info:
        await handle_read_resource(types.AnyUrl("invalid://test"))
    assert "Unsupported URI scheme: invalid" in str(exc_info.value)

@pytest.mark.asyncio
async def test_unsupported_method():
    """Test that server returns appropriate error for unsupported methods."""
    mock_ctx = MockRequestContext()
    request_ctx.set(mock_ctx)

    # Try to access a resource with an unsupported scheme
    with pytest.raises(ValueError) as exc_info:
        await handle_read_resource(types.AnyUrl("unsupported://test"))
    
    error_message = str(exc_info.value).lower()
    assert "unsupported" in error_message and "scheme" in error_message

if __name__ == '__main__':
    pytest.main([__file__])
