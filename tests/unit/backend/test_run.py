"""Unit tests for the backend run module."""
import pytest
import subprocess
from unittest.mock import patch, MagicMock

from ai_tools.backend.run import run_command, CommandResult


def test_command_result_dataclass():
    """Test the CommandResult dataclass."""
    result = CommandResult(stdout="output", stderr="error", exit_code=0)
    assert result.stdout == "output"
    assert result.stderr == "error"
    assert result.exit_code == 0


@patch("subprocess.run")
def test_run_command_success(mock_run):
    """Test run_command with a successful command."""
    # Setup mock
    mock_result = MagicMock()
    mock_result.stdout = "command output"
    mock_result.stderr = ""
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    # Call function
    response = run_command("echo hello")

    # Verify
    mock_run.assert_called_once_with(
        "echo hello",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
        check=False
    )
    assert response.stdout == "command output"
    assert response.stderr == ""
    assert response.exit_code == 0


@patch("subprocess.run")
def test_run_command_error(mock_run):
    """Test run_command with a command that returns an error."""
    # Setup mock
    mock_result = MagicMock()
    mock_result.stdout = ""
    mock_result.stderr = "command not found"
    mock_result.returncode = 127
    mock_run.return_value = mock_result

    # Call function
    response = run_command("invalid_command")

    # Verify
    mock_run.assert_called_once_with(
        "invalid_command",
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
        check=False
    )
    assert response.stdout == ""
    assert response.stderr == "command not found"
    assert response.exit_code == 127


@patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 10))
def test_run_command_timeout(mock_run):
    """Test run_command with a command that times out."""
    # Call function and expect exception
    with pytest.raises(TimeoutError) as excinfo:
        run_command("sleep 20")
    
    # Verify
    mock_run.assert_called_once()
    assert "Command timed out after 10 seconds" in str(excinfo.value)


@patch("subprocess.run", side_effect=Exception("Unknown error"))
def test_run_command_exception(mock_run):
    """Test run_command with an unexpected exception."""
    # Call function and expect exception
    with pytest.raises(RuntimeError) as excinfo:
        run_command("problematic command")
    
    # Verify
    mock_run.assert_called_once()
    assert "Error executing command" in str(excinfo.value)
    assert "Unknown error" in str(excinfo.value)