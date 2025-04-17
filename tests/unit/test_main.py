"""Unit tests for the main module."""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from ai_tools.main import (
    main,
    parse_args
)


@pytest.fixture
def argv_backup():
    """Backup and restore sys.argv during test execution."""
    original_argv = sys.argv.copy()
    yield
    sys.argv = original_argv


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.argparse.ArgumentParser.print_help')
def test_main_no_command(mock_print_help, mock_parse_args, argv_backup):
    """Test the main function with no command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = None
    mock_args.verbose = False
    mock_args.mode = 'shell'
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify print_help was called
    mock_print_help.assert_called_once()


def test_parse_args_default():
    """Test parse_args with default arguments."""
    args = parse_args([])
    
    assert args.verbose is False
    assert args.config is None
    assert args.mode == 'shell'


def test_parse_args_verbose():
    """Test parse_args with verbose flag."""
    args = parse_args(['--verbose'])
    
    assert args.verbose is True
    assert args.config is None
    assert args.mode == 'shell'


def test_parse_args_config():
    """Test parse_args with config file."""
    args = parse_args(['--config', 'test_config.yaml'])
    
    assert args.verbose is False
    assert args.config == 'test_config.yaml'
    assert args.mode == 'shell'


def test_parse_args_mode():
    """Test parse_args with different modes."""
    args = parse_args(['--mode', 'web'])
    assert args.mode == 'web'
    
    args = parse_args(['--mode', 'api'])
    assert args.mode == 'api'
    
    args = parse_args(['--mode', 'shell'])
    assert args.mode == 'shell'


def test_parse_args_invalid_mode():
    """Test parse_args with invalid mode raises error."""
    with pytest.raises(SystemExit):
        parse_args(['--mode', 'invalid'])