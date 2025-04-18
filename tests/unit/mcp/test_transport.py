"""Unit tests for the MCP transport module."""
import json
import uuid
import datetime
import pytest
from unittest.mock import patch, MagicMock
from ai_tools.mcp.transport import MCPMessage


def test_mcp_message_init():
    """Test MCPMessage initialization with default parameters."""
    message = MCPMessage(
        role="user",
        content="Hello, world!"
    )
    
    assert message.role == "user"
    assert message.content == "Hello, world!"
    assert message.context == {}
    assert uuid.UUID(message.id)  # Verify ID is a valid UUID
    # Verify timestamp is a valid ISO format datetime
    datetime.datetime.fromisoformat(message.timestamp)


def test_mcp_message_init_with_all_params():
    """Test MCPMessage initialization with all parameters provided."""
    test_id = "12345678-1234-5678-1234-567812345678"
    test_timestamp = "2025-04-18T10:30:45.123456"
    test_context = {"language": "Python", "framework": "FastAPI"}
    
    message = MCPMessage(
        role="assistant",
        content="I can help with that",
        context=test_context,
        msg_id=test_id,
        timestamp=test_timestamp
    )
    
    assert message.role == "assistant"
    assert message.content == "I can help with that"
    assert message.context == test_context
    assert message.id == test_id
    assert message.timestamp == test_timestamp


def test_mcp_message_to_dict():
    """Test converting MCPMessage to dictionary."""
    test_id = "test-id-123"
    test_timestamp = "2025-04-18T10:30:45"
    test_context = {"key": "value"}
    
    message = MCPMessage(
        role="system",
        content="System instruction",
        context=test_context,
        msg_id=test_id,
        timestamp=test_timestamp
    )
    
    result_dict = message.to_dict()
    
    assert result_dict["id"] == test_id
    assert result_dict["timestamp"] == test_timestamp
    assert result_dict["role"] == "system"
    assert result_dict["content"] == "System instruction"
    assert result_dict["context"] == test_context


def test_mcp_message_to_json():
    """Test converting MCPMessage to JSON string."""
    test_id = "json-test-id"
    test_timestamp = "2025-04-18T10:30:45"
    
    message = MCPMessage(
        role="user",
        content="Convert to JSON",
        msg_id=test_id,
        timestamp=test_timestamp
    )
    
    json_string = message.to_json()
    parsed_json = json.loads(json_string)
    
    assert isinstance(json_string, str)
    assert parsed_json["id"] == test_id
    assert parsed_json["timestamp"] == test_timestamp
    assert parsed_json["role"] == "user"
    assert parsed_json["content"] == "Convert to JSON"
    assert parsed_json["context"] == {}


def test_mcp_message_from_json():
    """Test creating MCPMessage from JSON string."""
    test_json = """
    {
      "id": "from-json-test",
      "timestamp": "2025-04-18T15:45:30",
      "role": "assistant",
      "content": "Created from JSON",
      "context": {"source": "test"}
    }
    """
    
    message = MCPMessage.from_json(test_json)
    
    assert message.id == "from-json-test"
    assert message.timestamp == "2025-04-18T15:45:30"
    assert message.role == "assistant"
    assert message.content == "Created from JSON"
    assert message.context == {"source": "test"}


def test_mcp_message_auto_generation():
    """Test auto-generation of id and timestamp."""
    # Create message with auto-generated fields
    message = MCPMessage(
        role="user",
        content="Test auto-generation"
    )
    
    # Verify UUID format
    assert uuid.UUID(message.id)
    
    # Verify timestamp format (without testing exact value)
    timestamp = datetime.datetime.fromisoformat(message.timestamp)
    assert isinstance(timestamp, datetime.datetime)


def test_round_trip_conversion():
    """Test round-trip conversion from message to JSON and back."""
    original_message = MCPMessage(
        role="user",
        content="Round trip test",
        context={"test": True},
        msg_id="round-trip-id",
        timestamp="2025-04-18T12:34:56"
    )
    
    # Convert to JSON
    json_string = original_message.to_json()
    
    # Convert back to message
    reconstructed_message = MCPMessage.from_json(json_string)
    
    # Verify all attributes are preserved
    assert reconstructed_message.id == original_message.id
    assert reconstructed_message.timestamp == original_message.timestamp
    assert reconstructed_message.role == original_message.role
    assert reconstructed_message.content == original_message.content
    assert reconstructed_message.context == original_message.context


def test_from_json_missing_fields():
    """Test from_json with missing optional fields."""
    test_json = """
    {
      "id": "minimal-json",
      "timestamp": "2025-04-18T15:45:30",
      "role": "user",
      "content": "Minimal JSON"
    }
    """
    
    message = MCPMessage.from_json(test_json)
    
    assert message.id == "minimal-json"
    assert message.timestamp == "2025-04-18T15:45:30"
    assert message.role == "user"
    assert message.content == "Minimal JSON"
    assert message.context == {}  # Context is initialized as empty dict when not provided


def test_from_json_invalid_format():
    """Test from_json with invalid JSON format."""
    invalid_json = "{not valid json"
    
    with pytest.raises(json.JSONDecodeError):
        MCPMessage.from_json(invalid_json)


def test_from_json_missing_required_fields():
    """Test from_json with missing required fields."""
    # Missing "role" field
    test_json = """
    {
      "id": "missing-role",
      "timestamp": "2025-04-18T15:45:30",
      "content": "Missing role field"
    }
    """
    
    with pytest.raises(KeyError):
        MCPMessage.from_json(test_json)