"""Unit tests for the MCP actions module."""
import os
import json
import pytest
from unittest.mock import patch, MagicMock

import requests

from ai_tools.mcp.actions import (
    get_ollama_url,
    get_ollama_model,
    ask_llm_to_explain_error,
    ask_llm_for_command,
    run_command,
    run_ai_command,
    prompt_ollama_http,
    handle_mcp_action,
    MCP_ACTIONS
)


# Fixtures for common test setup
@pytest.fixture
def setup_env():
    """Set up test environment variables and restore them after the test."""
    # Save original environment variables
    original_env = {
        'OLLAMA_HOST': os.environ.get('OLLAMA_HOST'),
        'OLLAMA_PORT': os.environ.get('OLLAMA_PORT'),
        'OLLAMA_MODEL': os.environ.get('OLLAMA_MODEL'),
    }
    
    # Set test environment variables
    os.environ['OLLAMA_HOST'] = 'localhost'
    os.environ['OLLAMA_PORT'] = '11434'
    os.environ['OLLAMA_MODEL'] = 'test-model'
    
    # Yield to the test
    yield
    
    # Restore original environment variables
    for key, value in original_env.items():
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value


# Test functions
def test_get_ollama_url(setup_env):
    """Test the get_ollama_url function."""
    expected_url = "http://localhost:11434/api/generate"
    assert get_ollama_url() == expected_url
    
    # Test with different environment variables
    os.environ['OLLAMA_HOST'] = 'test-host'
    os.environ['OLLAMA_PORT'] = '8000'
    expected_url = "http://test-host:8000/api/generate"
    assert get_ollama_url() == expected_url

def test_get_ollama_model(setup_env):
    """Test the get_ollama_model function."""
    assert get_ollama_model() == 'test-model'
    
    # Test with different environment variable
    os.environ['OLLAMA_MODEL'] = 'different-model'
    assert get_ollama_model() == 'different-model'

@patch('requests.post')
def test_ask_llm_to_explain_error(mock_post, setup_env):
    """Test the ask_llm_to_explain_error function."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "This is a test explanation"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    result = ask_llm_to_explain_error("test command", "test error")
    
    # Verify the API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert 'json' in call_args
    assert call_args['json']['model'] == 'test-model'
    assert 'test command' in call_args['json']['prompt']
    assert 'test error' in call_args['json']['prompt']
    
    # Check the result
    assert result == "This is a test explanation"

@patch('requests.post')
def test_ask_llm_to_explain_error_timeout(mock_post, setup_env):
    """Test the ask_llm_to_explain_error function when timeout occurs."""
    mock_post.side_effect = requests.exceptions.ReadTimeout()
    
    result = ask_llm_to_explain_error("test command", "test error")
    assert result == "Error: The request to the Ollama server timed out."

@patch('requests.post')
def test_ask_llm_to_explain_error_request_exception(mock_post, setup_env):
    """Test the ask_llm_to_explain_error function when request exception occurs."""
    mock_post.side_effect = requests.exceptions.RequestException("test exception")
    
    result = ask_llm_to_explain_error("test command", "test error")
    assert result == "Error: Failed to connect to the Ollama server. test exception"

@patch('requests.post')
def test_ask_llm_for_command(mock_post, setup_env):
    """Test the ask_llm_for_command function."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "ls -la"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    result = ask_llm_for_command("list all files in detail")
    
    # Verify the API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert 'json' in call_args
    assert call_args['json']['model'] == 'test-model'
    assert 'list all files in detail' in call_args['json']['prompt']
    
    # Check the result
    assert result == "ls -la"

@patch('subprocess.check_output')
def test_run_command_success(mock_check_output, setup_env):
    """Test the run_command function on successful execution."""
    mock_check_output.return_value = "command output"
    
    result = run_command("ls")
    
    # Verify subprocess.check_output was called correctly
    mock_check_output.assert_called_once_with(['/bin/bash', '-c', 'ls'], 
                                              stderr=-2, 
                                              text=True, 
                                              timeout=5)
    
    # Check the result
    assert result == "command output"

@patch('subprocess.check_output')
def test_run_command_shell_function(mock_check_output, setup_env):
    """Test the run_command function with shell function."""
    result = run_command("return 0")
    
    # Verify subprocess.check_output was not called
    mock_check_output.assert_not_called()
    
    # Check the result
    assert result == "Error: The command contains shell function syntax that cannot be executed directly."

@patch('subprocess.check_output')
def test_run_command_error(mock_check_output, setup_env):
    """Test the run_command function when command execution fails."""
    import subprocess
    mock_check_output.side_effect = subprocess.CalledProcessError(1, "test", output="error output")
    
    result = run_command("invalid_command")
    
    # Check the result
    assert result == "Command error:\nerror output"

@patch('ai_tools.mcp.actions.ask_llm_for_command')
@patch('ai_tools.mcp.actions.run_command')
def test_run_ai_command(mock_run_command, mock_ask_llm, setup_env):
    """Test the run_ai_command function."""
    # Setup mocks
    mock_ask_llm.return_value = "ls -la"
    mock_run_command.return_value = "total 0\ndrwxr-xr-x 2 user user 40 Apr 17 10:00 ."
    
    command, output = run_ai_command("list all files with details")
    
    # Verify ask_llm_for_command was called correctly
    mock_ask_llm.assert_called_once_with("list all files with details")
    
    # Verify run_command was called correctly
    mock_run_command.assert_called_once_with("ls -la")
    
    # Check the results
    assert command == "ls -la"
    assert output == "total 0\ndrwxr-xr-x 2 user user 40 Apr 17 10:00 ."

@patch('requests.post')
@patch('requests.get')
def test_prompt_ollama_http_non_streaming(mock_get, mock_post, setup_env):
    """Test the prompt_ollama_http function in non-streaming mode."""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "This is a test response"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    result = prompt_ollama_http("test prompt", use_streaming=False, verbose=True)
    
    # Verify the API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args[1]
    assert 'json' in call_args
    assert call_args['json']['model'] == 'test-model'
    assert call_args['json']['prompt'] == 'test prompt'
    assert call_args['json']['stream'] == False
    
    # Check the result
    assert result == "This is a test response"

@patch('requests.post')
def test_prompt_ollama_http_timeout(mock_post, setup_env):
    """Test the prompt_ollama_http function when timeout occurs."""
    mock_post.side_effect = requests.exceptions.ReadTimeout()
    
    result = prompt_ollama_http("test prompt", use_streaming=False)
    assert result.startswith("Error: The request to the Ollama server timed out.")

def test_handle_mcp_action_unknown_action(setup_env):
    """Test handle_mcp_action with unknown action."""
    result = handle_mcp_action("unknown_action", {})
    
    assert result["status"] == "error"
    assert "Unknown action: unknown_action" in result["message"]
    assert "available_actions" in result

def test_handle_mcp_action_success(setup_env):
    """Test handle_mcp_action with a valid action."""
    # Import actions in the test to access the original actions module
    from ai_tools.mcp import actions
    
    # Save original run_command function
    original_run_command = actions.MCP_ACTIONS["run_command"]
    
    try:
        # Create mock function for run_command
        mock_run_command = MagicMock(return_value="command output")
        # Replace the actual function in the MCP_ACTIONS dict
        actions.MCP_ACTIONS["run_command"] = mock_run_command
        
        result = handle_mcp_action("run_command", {"command": "ls"})
        
        # Verify our mock function was called with the correct parameters
        mock_run_command.assert_called_once_with(command="ls")
        
        assert result["status"] == "success"
        assert result["result"] == "command output"
    finally:
        # Restore original function
        actions.MCP_ACTIONS["run_command"] = original_run_command