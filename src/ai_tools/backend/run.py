"""
Command execution utility module.
Provides functionality to run shell commands and capture their output.
"""
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    """Result of a command execution"""
    stdout: str
    stderr: str
    exit_code: int


def run_command(command: str, timeout: int = 10) -> CommandResult:
    """
    Execute a shell command and return its output.
    
    Args:
        command: The shell command to execute
        timeout: Maximum time to wait for the command to complete (seconds)
        
    Returns:
        CommandResult object containing stdout, stderr and exit code
        
    Raises:
        TimeoutError: If the command execution times out
        RuntimeError: If another exception occurs during execution
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return CommandResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout} seconds: {command}")
    except Exception as exc:
        raise RuntimeError(f"Error executing command: {str(exc)}")
