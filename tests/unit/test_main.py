"""Unit tests for the main module."""
import os
import sys
import logging
import pytest
from unittest.mock import patch, MagicMock, call
from io import StringIO

from ai_tools.main import (
    main,
    parse_args,
    handle_run_command,
    handle_prompt_command,
    handle_error_command,
    handle_load_command,
    handle_speak_command,
    print_environment_info,
    install_shell_integration_command
)


@pytest.fixture
def argv_backup():
    """Backup and restore sys.argv during test execution."""
    original_argv = sys.argv.copy()
    yield
    sys.argv = original_argv


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


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.argparse.ArgumentParser.print_help')
def test_main_no_command(mock_print_help, mock_parse_args, argv_backup):
    """Test the main function with no command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = None
    mock_args.verbose = False
    mock_args.mode = 'shell'
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify print_help was called
    mock_print_help.assert_called_once()


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.logging.basicConfig')
def test_main_verbose_mode(mock_logging_config, mock_parse_args, argv_backup):
    """Test the main function with verbose mode."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = None
    mock_args.verbose = True
    mock_args.mode = 'shell'
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    with patch('ai_tools.main.print') as mock_print:
        main()
    
    # Verify logging.basicConfig was called with DEBUG level
    mock_logging_config.assert_called_with(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    mock_print.assert_any_call("Starting AI Tools in verbose mode")


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
def test_main_with_config(mock_parse_args, argv_backup, capsys):
    """Test the main function with a config file."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = None
    mock_args.verbose = False
    mock_args.mode = 'shell'
    mock_args.config = 'test_config.yaml'
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify config message was printed
    captured = capsys.readouterr()
    assert "Note: Config file 'test_config.yaml' specified but config loading is not implemented" in captured.out


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
def test_main_with_non_shell_mode(mock_parse_args, argv_backup, capsys):
    """Test the main function with a non-shell mode."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = None
    mock_args.verbose = False
    mock_args.mode = 'api'
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify mode message was printed
    captured = capsys.readouterr()
    assert "Note: Mode 'api' is not implemented" in captured.out


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.handle_run_command')
def test_main_run_command(mock_handle_run, mock_parse_args, argv_backup):
    """Test the main function with run command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "run"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify handle_run_command was called
    mock_handle_run.assert_called_once_with(mock_args)


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.handle_prompt_command')
def test_main_prompt_command(mock_handle_prompt, mock_parse_args, argv_backup):
    """Test the main function with prompt command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "prompt"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify handle_prompt_command was called
    mock_handle_prompt.assert_called_once_with(mock_args)


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.handle_error_command')
def test_main_error_command(mock_handle_error, mock_parse_args, argv_backup):
    """Test the main function with error command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "error"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify handle_error_command was called
    mock_handle_error.assert_called_once_with(mock_args)


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.handle_load_command')
def test_main_load_command(mock_handle_load, mock_parse_args, argv_backup):
    """Test the main function with load command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "load"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify handle_load_command was called
    mock_handle_load.assert_called_once_with(mock_args)


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.print_environment_info')
def test_main_info_command(mock_print_env, mock_parse_args, argv_backup):
    """Test the main function with info command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "info"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify print_environment_info was called
    mock_print_env.assert_called_once()


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.handle_speak_command')
def test_main_speak_command(mock_handle_speak, mock_parse_args, argv_backup):
    """Test the main function with speak command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "speak"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify handle_speak_command was called
    mock_handle_speak.assert_called_once_with(mock_args)


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.install_shell_integration_command')
def test_main_install_shell_command(mock_install_shell, mock_parse_args, argv_backup):
    """Test the main function with install-shell command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "install-shell"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify install_shell_integration_command was called
    mock_install_shell.assert_called_once()


@patch('ai_tools.main.argparse.ArgumentParser.parse_args')
@patch('ai_tools.main.argparse.ArgumentParser.print_help')
def test_main_unknown_command(mock_print_help, mock_parse_args, argv_backup):
    """Test the main function with an unknown command."""
    # Setup mock args
    mock_args = MagicMock()
    mock_args.command = "unknown"
    mock_args.verbose = False
    mock_args.config = None
    mock_parse_args.return_value = mock_args
    
    # Call main function
    main()
    
    # Verify print_help was called
    mock_print_help.assert_called_once()


@patch('ai_tools.main.get_ollama_url')
@patch('ai_tools.main.get_ollama_model')
def test_print_environment_info(mock_get_model, mock_get_url, setup_env, capsys):
    """Test the print_environment_info function."""
    mock_get_model.return_value = "test-model"
    mock_get_url.return_value = "http://localhost:11434/api/generate"
    
    print_environment_info()
    
    captured = capsys.readouterr()
    assert "Ollama Configuration:" in captured.out
    assert "Host: localhost" in captured.out
    assert "Port: 11434" in captured.out
    assert "Model: test-model" in captured.out
    assert "API URL: http://localhost:11434/api/generate" in captured.out


@patch('ai_tools.main.run_ai_command')
def test_handle_run_command(mock_run_ai_command, capsys):
    """Test the handle_run_command function."""
    mock_run_ai_command.return_value = ("ls -la", "sample output")
    
    # Create mock args
    args = MagicMock()
    args.prompt = ["list", "files"]
    
    handle_run_command(args)
    
    # Verify function was called with correct arguments
    mock_run_ai_command.assert_called_once_with("list files")
    
    # Check the output
    captured = capsys.readouterr()
    assert "Generating command for: 'list files'" in captured.out
    assert "Command: ls -la" in captured.out
    assert "Output: sample output" in captured.out


@patch('ai_tools.main.prompt_ollama_http')
@patch('ai_tools.main.db_config')
def test_handle_prompt_command(mock_db_config, mock_prompt, capsys):
    """Test the handle_prompt_command function."""
    mock_prompt.return_value = "AI response"
    
    # Create mock args
    args = MagicMock()
    args.prompt = ["hello", "world"]
    args.verbose = True
    
    handle_prompt_command(args)
    
    # Verify function was called with correct arguments
    mock_db_config.set_verbose.assert_called_once_with(True)
    mock_prompt.assert_called_once_with("hello world", use_streaming=True, verbose=True)
    
    # Check the output
    captured = capsys.readouterr()
    assert "Sending prompt to Ollama: 'hello world'" in captured.out
    assert "Response" in captured.out
    assert "AI response" in captured.out


@patch('ai_tools.main.ask_llm_to_explain_error')
def test_handle_error_command(mock_ask_llm, capsys):
    """Test the handle_error_command function."""
    mock_ask_llm.return_value = "Command not found"
    
    # Create mock args
    args = MagicMock()
    args.command = "invalid_cmd"
    args.error = ["command", "not", "found"]
    
    handle_error_command(args)
    
    # Verify function was called with correct arguments
    mock_ask_llm.assert_called_once_with("invalid_cmd", "command not found")
    
    # Check the output
    captured = capsys.readouterr()
    assert "Analyzing error for command: 'invalid_cmd'" in captured.out
    assert "Explanation" in captured.out
    assert "Command not found" in captured.out


@patch('os.path.exists')
@patch('os.path.isdir')
@patch('ai_tools.main.MCP_ACTIONS')
@patch('ai_tools.main.db_config')
def test_handle_load_command_success(mock_db_config, mock_actions, mock_isdir, mock_exists, capsys):
    """Test the handle_load_command function with successful load."""
    # Setup mocks
    mock_exists.return_value = True
    mock_isdir.return_value = True
    
    mock_vectorize = MagicMock()
    mock_vectorize.return_value = {
        "status": "success",
        "storage_type": "local"
    }
    mock_actions.get.return_value = mock_vectorize
    
    # Create mock args
    args = MagicMock()
    args.directory = "/test/docs"
    args.verbose = True
    
    handle_load_command(args)
    
    # Verify functions were called with correct arguments
    mock_exists.assert_called_once_with("/test/docs")
    mock_isdir.assert_called_once_with("/test/docs")
    mock_db_config.set_verbose.assert_called_once_with(True)
    mock_actions.get.assert_called_once_with("vectorize_documents")
    mock_vectorize.assert_called_once_with("/test/docs", db_name="knowledge")
    
    # Check the output
    captured = capsys.readouterr()
    assert "Loading documents from '/test/docs'" in captured.out
    assert "Successfully loaded documents" in captured.out


@patch('os.path.exists')
@patch('os.path.isdir')
def test_handle_load_command_invalid_dir(mock_isdir, mock_exists, capsys):
    """Test the handle_load_command function with an invalid directory."""
    # Setup mocks
    mock_exists.return_value = False
    
    # Create mock args
    args = MagicMock()
    args.directory = "/invalid/path"
    args.verbose = False
    
    handle_load_command(args)
    
    # Check the output
    captured = capsys.readouterr()
    assert "Error: '/invalid/path' is not a valid directory" in captured.out


@patch('os.path.exists')
@patch('os.path.isdir')
@patch('ai_tools.main.MCP_ACTIONS')
def test_handle_load_command_action_not_available(mock_actions, mock_isdir, mock_exists, capsys):
    """Test the handle_load_command function when vectorize_documents is not available."""
    # Setup mocks
    mock_exists.return_value = True
    mock_isdir.return_value = True
    mock_actions.get.return_value = None
    
    # Create mock args
    args = MagicMock()
    args.directory = "/test/docs"
    args.verbose = False
    
    handle_load_command(args)
    
    # Check the output
    captured = capsys.readouterr()
    assert "Error: Document loading functionality is not available" in captured.out


@patch('os.path.exists')
@patch('os.path.isdir')
@patch('ai_tools.main.MCP_ACTIONS')
def test_handle_load_command_failure(mock_actions, mock_isdir, mock_exists, capsys):
    """Test the handle_load_command function when vectorize_documents fails."""
    # Setup mocks
    mock_exists.return_value = True
    mock_isdir.return_value = True
    
    mock_vectorize = MagicMock()
    mock_vectorize.return_value = {
        "status": "error",
        "message": "Failed to process documents"
    }
    mock_actions.get.return_value = mock_vectorize
    
    # Create mock args
    args = MagicMock()
    args.directory = "/test/docs"
    args.verbose = False
    
    handle_load_command(args)
    
    # Check the output
    captured = capsys.readouterr()
    assert "Error: Failed to process documents" in captured.out


@patch('ai_tools.main.prompt_ollama_http')
@patch('ai_tools.main.SpeechToText')
@patch('ai_tools.main.db_config')
def test_handle_speak_command(mock_db_config, mock_speech, mock_prompt, capsys):
    """Test the handle_speak_command function."""
    # Setup mocks
    mock_prompt.return_value = "AI response"
    mock_speech_instance = MagicMock()
    mock_speech.return_value = mock_speech_instance
    
    # Create mock args
    args = MagicMock()
    args.prompt = ["tell", "me", "a", "joke"]
    args.verbose = False
    
    handle_speak_command(args)
    
    # Verify functions were called with correct arguments
    mock_db_config.set_verbose.assert_called_once_with(False)
    mock_speech.assert_called_once()
    mock_prompt.assert_called_once_with("tell me a joke", use_streaming=False, verbose=False)
    mock_speech_instance.speech.assert_called_once_with("AI response")
    
    # Check the output
    captured = capsys.readouterr()
    assert "Sending prompt to Ollama: 'tell me a joke'" in captured.out
    assert "Please wait while getting response..." in captured.out
    assert "Response:" in captured.out
    assert "AI response" in captured.out
    assert "Speaking response..." in captured.out


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


def test_parse_args_run_command():
    """Test parse_args with 'run' command."""
    args = parse_args(['run', 'list', 'files'])
    
    assert args.command == 'run'
    assert args.prompt == ['list', 'files']


def test_parse_args_prompt_command():
    """Test parse_args with 'prompt' command."""
    args = parse_args(['prompt', 'hello', 'world'])
    
    assert args.command == 'prompt'
    assert args.prompt == ['hello', 'world']
    assert args.verbose is False


def test_parse_args_prompt_command_verbose():
    """Test parse_args with 'prompt' command and verbose flag."""
    args = parse_args(['prompt', '-v', 'hello', 'world'])
    
    assert args.command == 'prompt'
    assert args.prompt == ['hello', 'world']
    assert args.verbose is True


def test_parse_args_error_command():
    """Test parse_args with 'error' command."""
    args = parse_args(['error', 'ls', 'command', 'not', 'found'])
    
    # The actual behavior is that the first argument after 'error' is parsed as the command
    assert args.command == 'ls'
    assert args.error == ['command', 'not', 'found']


def test_parse_args_load_command():
    """Test parse_args with 'load' command."""
    args = parse_args(['load', '/path/to/docs'])
    
    assert args.command == 'load'
    assert args.directory == '/path/to/docs'
    assert args.verbose is False


def test_parse_args_speak_command():
    """Test parse_args with 'speak' command."""
    args = parse_args(['speak', 'tell', 'me', 'a', 'joke'])
    
    assert args.command == 'speak'
    assert args.prompt == ['tell', 'me', 'a', 'joke']
    assert args.verbose is False


def test_parse_args_install_shell_command():
    """Test parse_args with 'install-shell' command."""
    args = parse_args(['install-shell'])
    
    assert args.command == 'install-shell'
    assert args.auto is False


def test_parse_args_install_shell_command_auto():
    """Test parse_args with 'install-shell' command and auto flag."""
    args = parse_args(['install-shell', '--auto'])
    
    assert args.command == 'install-shell'
    assert args.auto is True