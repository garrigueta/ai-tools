#!/usr/bin/env python3
"""
Tests for the shell integration tools.
"""

import os
import pytest
import shutil
import tempfile
from unittest.mock import patch, mock_open

from ai_tools.modules.shell_tools import (
    get_user_home,
    get_shell_config_file,
    is_shell_integration_installed,
    install_shell_integration,
    install_shell_integration_command
)


@pytest.fixture
def temp_home_dir():
    """Create a temporary home directory for testing"""
    original_home = os.environ.get('HOME')
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['HOME'] = temp_dir
        # Create a fake bashrc file
        bashrc_file = os.path.join(temp_dir, '.bashrc')
        with open(bashrc_file, 'w') as f:
            f.write('# Existing bashrc content\n')
        
        yield temp_dir
        
        # Restore the original HOME
        if original_home:
            os.environ['HOME'] = original_home
        else:
            del os.environ['HOME']


@pytest.fixture
def mock_bash_script(temp_home_dir):
    """Mock the bash script path"""
    with patch('ai_tools.modules.shell_tools.get_bash_script_path') as mock:
        # Use a path within the temp directory instead of /fake/path
        mock.return_value = os.path.join(temp_home_dir, 'mock_path', 'bash_aitools')
        yield mock


def test_get_shell_config_file(temp_home_dir):
    """Test that the shell config file detection works"""
    # Should find the .bashrc we created in the fixture
    config_file = get_shell_config_file()
    assert config_file == os.path.join(temp_home_dir, '.bashrc')
    
    # If we add a .zshrc it should still use .bashrc by default
    with open(os.path.join(temp_home_dir, '.zshrc'), 'w') as f:
        f.write('# zsh config\n')
    
    config_file = get_shell_config_file()
    assert config_file == os.path.join(temp_home_dir, '.bashrc')
    
    # But if SHELL env var is set to zsh, it should use .zshrc
    os.environ['SHELL'] = '/bin/zsh'
    config_file = get_shell_config_file()
    assert config_file == os.path.join(temp_home_dir, '.zshrc')


def test_is_shell_integration_installed(temp_home_dir, mock_bash_script):
    """Test detection of shell integration installation"""
    # Initially not installed
    assert not is_shell_integration_installed()
    
    # Add the integration line
    bashrc_file = os.path.join(temp_home_dir, '.bashrc')
    with open(bashrc_file, 'a') as f:
        f.write('source ~/.bash_aitools\n')
    
    # Now it should be detected as installed
    assert is_shell_integration_installed()


def test_install_shell_integration_new(temp_home_dir, mock_bash_script):
    """Test installing shell integration when not previously installed"""
    # Create a fake script file that will be copied
    os.makedirs(os.path.dirname(mock_bash_script.return_value), exist_ok=True)
    with open(mock_bash_script.return_value, 'w') as f:
        f.write('# Test bash script content\n')
    
    # Test with auto_source=True
    result = install_shell_integration(auto_source=True)
    
    # Check result
    assert result["status"] == "success"
    assert result["auto_source"] is True
    
    # Verify the file was copied
    user_script_path = os.path.join(temp_home_dir, '.bash_aitools')
    assert os.path.exists(user_script_path)
    
    # Verify the source line was added to bashrc
    bashrc_file = os.path.join(temp_home_dir, '.bashrc')
    with open(bashrc_file, 'r') as f:
        content = f.read()
    assert f"source {user_script_path}" in content


def test_install_shell_integration_already_installed(temp_home_dir, mock_bash_script):
    """Test installing shell integration when already installed"""
    # Create a fake script file that will be copied
    os.makedirs(os.path.dirname(mock_bash_script.return_value), exist_ok=True)
    with open(mock_bash_script.return_value, 'w') as f:
        f.write('# Test bash script content\n')
    
    # Pre-install the integration
    bashrc_file = os.path.join(temp_home_dir, '.bashrc')
    with open(bashrc_file, 'a') as f:
        f.write('source ~/.bash_aitools\n')
    
    # Test with auto_source=True but it shouldn't add another line
    result = install_shell_integration(auto_source=True)
    
    # Check result
    assert result["status"] == "success"
    assert result["auto_source"] is False  # Indicates no changes were made
    
    # Verify the source line is in bashrc exactly once
    with open(bashrc_file, 'r') as f:
        content = f.read()
    assert content.count('source ~/.bash_aitools') == 1


@patch('builtins.print')
def test_install_shell_integration_command_new(mock_print, temp_home_dir, mock_bash_script):
    """Test the command-line function for shell integration installation when not previously installed"""
    # Create a fake script file that will be copied
    os.makedirs(os.path.dirname(mock_bash_script.return_value), exist_ok=True)
    with open(mock_bash_script.return_value, 'w') as f:
        f.write('# Test bash script content\n')
    
    result = install_shell_integration_command()
    
    # Check result
    assert result == 0  # Success
    
    # Verify the source line was added to bashrc
    bashrc_file = os.path.join(temp_home_dir, '.bashrc')
    with open(bashrc_file, 'r') as f:
        content = f.read()
    # Check for the absolute path source command - using the full path is more reliable
    user_script_path = os.path.join(temp_home_dir, '.bash_aitools')
    assert f"source {user_script_path}" in content
    
    # Check that the appropriate success message was printed
    mock_print.assert_any_call(f"\nShell integration has been automatically added to your {bashrc_file}")


@patch('builtins.print')
def test_install_shell_integration_command_already_installed(mock_print, temp_home_dir, mock_bash_script):
    """Test the command-line function when shell integration is already installed"""
    # Create a fake script file that will be copied
    os.makedirs(os.path.dirname(mock_bash_script.return_value), exist_ok=True)
    with open(mock_bash_script.return_value, 'w') as f:
        f.write('# Test bash script content\n')
    
    # Pre-install the integration
    bashrc_file = os.path.join(temp_home_dir, '.bashrc')
    with open(bashrc_file, 'a') as f:
        f.write('source ~/.bash_aitools\n')
    
    result = install_shell_integration_command()
    
    # Check result
    assert result == 0  # Success
    
    # Check that the appropriate message was printed
    mock_print.assert_any_call(f"\nShell integration was already configured in your {bashrc_file}")
    
    # Verify the source line is in bashrc exactly once
    with open(bashrc_file, 'r') as f:
        content = f.read()
    assert content.count('source ~/.bash_aitools') == 1