"""Unit tests for the database configuration module."""
import os
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
import tempfile
import shutil

from ai_tools.config.database import DatabaseConfig, db_config


# Fixtures for common test setup
@pytest.fixture
def setup_env():
    """Set up test environment variables and restore them after the test."""
    # Save original environment variables
    original_env = {}
    for key in list(os.environ.keys()):
        if key.startswith('OLLAMA_') or key.startswith('VECTOR_') or key.startswith('HISTORY_') or key == 'LLM_API_KEY':
            original_env[key] = os.environ[key]
            del os.environ[key]
    
    # Yield to the test
    yield
    
    # Restore original environment variables
    for key in list(os.environ.keys()):
        if key.startswith('OLLAMA_') or key.startswith('VECTOR_') or key.startswith('HISTORY_') or key == 'LLM_API_KEY':
            del os.environ[key]
            
    for key, value in original_env.items():
        os.environ[key] = value


@pytest.fixture
def captured_stdout():
    """Capture stdout during test execution."""
    with StringIO() as captured_output:
        original_stdout = sys.stdout
        sys.stdout = captured_output
        yield captured_output
        sys.stdout = original_stdout


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data paths."""
    temp_dir_path = tempfile.mkdtemp()
    yield temp_dir_path
    # Clean up the temporary directory
    shutil.rmtree(temp_dir_path)


@pytest.fixture
def reset_singleton():
    """Reset the DatabaseConfig singleton before and after test."""
    # Reset the singleton instance before the test
    DatabaseConfig._reset_instance()
    # Run the test
    yield
    # Reset the singleton instance after the test
    DatabaseConfig._reset_instance()


def test_singleton_pattern(reset_singleton):
    """Test that DatabaseConfig is a singleton."""
    config1 = DatabaseConfig()
    config2 = DatabaseConfig()
    assert config1 is config2


def test_default_configuration(setup_env, reset_singleton):
    """Test default configuration values."""
    config = DatabaseConfig()
    
    # Check default database settings
    assert config.db_enabled is False
    assert config.db_host == 'localhost'
    assert config.db_port == 5432
    assert config.db_user == 'postgres'
    assert config.db_password == ''
    assert config.db_name == 'ai_tools_db'
    
    # Check vector database settings
    assert config.vector_db_enabled is False
    assert config.vector_db_host == 'localhost'
    assert config.vector_db_port == 5432
    
    # Check history database settings
    assert config.history_db_enabled is False
    assert config.history_db_host == 'localhost'
    assert config.history_db_port == 5432
    
    # Check LLM settings
    assert config.llm_host == 'localhost'
    assert config.llm_port == 11434
    assert config.llm_model == 'gemma3:27b'


def test_environment_variable_override(setup_env, reset_singleton):
    """Test overriding configuration with environment variables."""
    # Set environment variables
    os.environ['OLLAMA_DB_ENABLED'] = 'true'
    os.environ['OLLAMA_DB_HOST'] = 'test-host'
    os.environ['OLLAMA_DB_PORT'] = '5433'
    os.environ['VECTOR_DB_HOST'] = 'vector-host'
    os.environ['HISTORY_DB_HOST'] = 'history-host'
    os.environ['OLLAMA_MODEL'] = 'test-model'
    
    config = DatabaseConfig(force_init=True)
    
    # Check overridden values
    assert config.db_enabled is True
    assert config.db_host == 'test-host'
    assert config.db_port == 5433
    assert config.vector_db_host == 'vector-host'
    assert config.history_db_host == 'history-host'
    assert config.llm_model == 'test-model'


def test_get_vector_db_config(setup_env, temp_dir, reset_singleton):
    """Test get_vector_db_config method."""
    # Set up test values
    os.environ['VECTOR_DB_ENABLED'] = 'true'
    os.environ['VECTOR_DB_HOST'] = 'vector-host'
    os.environ['VECTOR_DB_PORT'] = '5433'
    os.environ['VECTOR_DB_USER'] = 'vector-user'
    os.environ['VECTOR_DB_PASSWORD'] = 'vector-password'
    os.environ['VECTOR_DB_NAME'] = 'vector-db'
    os.environ['VECTOR_TABLE_PREFIX'] = 'v_'
    os.environ['VECTOR_DB_PATH'] = os.path.join(temp_dir, 'vector')
    
    config = DatabaseConfig(force_init=True)
    vector_config = config.get_vector_db_config()
    
    # Verify all fields are present with correct values
    assert vector_config['enabled'] is True
    assert vector_config['host'] == 'vector-host'
    assert vector_config['port'] == 5433
    assert vector_config['user'] == 'vector-user'
    assert vector_config['password'] == 'vector-password'
    assert vector_config['dbname'] == 'vector-db'
    assert vector_config['table_prefix'] == 'v_'
    assert vector_config['local_path'] == os.path.join(temp_dir, 'vector')


def test_get_history_db_config(setup_env, temp_dir, reset_singleton):
    """Test get_history_db_config method."""
    # Set up test values
    os.environ['HISTORY_DB_ENABLED'] = 'true'
    os.environ['HISTORY_DB_HOST'] = 'history-host'
    os.environ['HISTORY_DB_PORT'] = '5434'
    os.environ['HISTORY_DB_USER'] = 'history-user'
    os.environ['HISTORY_DB_PASSWORD'] = 'history-password'
    os.environ['HISTORY_DB_NAME'] = 'history-db'
    os.environ['HISTORY_TABLE_PREFIX'] = 'h_'
    os.environ['HISTORY_DB_PATH'] = os.path.join(temp_dir, 'history')
    
    config = DatabaseConfig(force_init=True)
    history_config = config.get_history_db_config()
    
    # Verify all fields are present with correct values
    assert history_config['enabled'] is True
    assert history_config['host'] == 'history-host'
    assert history_config['port'] == 5434
    assert history_config['user'] == 'history-user'
    assert history_config['password'] == 'history-password'
    assert history_config['dbname'] == 'history-db'
    assert history_config['table_prefix'] == 'h_'
    assert history_config['local_path'] == os.path.join(temp_dir, 'history')


def test_get_llm_config(setup_env, reset_singleton):
    """Test get_llm_config method."""
    # Set up test values
    os.environ['OLLAMA_HOST'] = 'ollama-host'
    os.environ['OLLAMA_PORT'] = '11435'
    os.environ['OLLAMA_MODEL'] = 'llama2'
    os.environ['LLM_API_KEY'] = 'test-api-key'
    
    config = DatabaseConfig(force_init=True)
    llm_config = config.get_llm_config()
    
    # Verify all fields are present with correct values
    assert llm_config['host'] == 'ollama-host'
    assert llm_config['port'] == 11435
    assert llm_config['model'] == 'llama2'
    assert llm_config['api_key'] == 'test-api-key'


def test_get_vector_table_name(setup_env, reset_singleton):
    """Test get_vector_table_name method."""
    os.environ['VECTOR_TABLE_PREFIX'] = 'v_'
    
    config = DatabaseConfig(force_init=True)
    table_name = config.get_vector_table_name('test')
    
    assert table_name == 'v_test'


def test_get_history_table_name(setup_env, reset_singleton):
    """Test get_history_table_name method."""
    os.environ['HISTORY_TABLE_PREFIX'] = 'h_'
    
    config = DatabaseConfig(force_init=True)
    table_name = config.get_history_table_name('session123')
    
    assert table_name == 'h_session123'


def test_get_connection_string_local(setup_env, temp_dir, reset_singleton):
    """Test get_connection_string method for local storage."""
    os.environ['VECTOR_DB_ENABLED'] = 'false'
    os.environ['HISTORY_DB_ENABLED'] = 'false'
    os.environ['VECTOR_DB_PATH'] = os.path.join(temp_dir, 'vector')
    os.environ['HISTORY_DB_PATH'] = os.path.join(temp_dir, 'history')
    
    config = DatabaseConfig(force_init=True)
    vector_conn = config.get_connection_string('vector')
    history_conn = config.get_connection_string('history')
    
    assert vector_conn == f"local://{os.path.join(temp_dir, 'vector')}"
    assert history_conn == f"local://{os.path.join(temp_dir, 'history')}"


def test_get_connection_string_postgresql(setup_env, reset_singleton):
    """Test get_connection_string method for PostgreSQL."""
    os.environ['VECTOR_DB_ENABLED'] = 'true'
    os.environ['HISTORY_DB_ENABLED'] = 'true'
    os.environ['VECTOR_DB_HOST'] = 'vector-host'
    os.environ['VECTOR_DB_PORT'] = '5433'
    os.environ['VECTOR_DB_USER'] = 'vector-user'
    os.environ['VECTOR_DB_PASSWORD'] = 'vector-password'
    os.environ['VECTOR_DB_NAME'] = 'vector-db'
    os.environ['HISTORY_DB_HOST'] = 'history-host'
    os.environ['HISTORY_DB_PORT'] = '5434'
    os.environ['HISTORY_DB_USER'] = 'history-user'
    os.environ['HISTORY_DB_PASSWORD'] = 'history-password'
    os.environ['HISTORY_DB_NAME'] = 'history-db'
    
    config = DatabaseConfig(force_init=True)
    vector_conn = config.get_connection_string('vector')
    history_conn = config.get_connection_string('history')
    
    assert vector_conn == 'postgresql://vector-user:vector-password@vector-host:5433/vector-db'
    assert history_conn == 'postgresql://history-user:history-password@history-host:5434/history-db'


def test_get_connection_string_invalid_type(setup_env, reset_singleton):
    """Test get_connection_string method with invalid database type."""
    config = DatabaseConfig()
    
    with pytest.raises(ValueError):
        config.get_connection_string('invalid')


def test_set_verbose(setup_env, reset_singleton):
    """Test set_verbose method."""
    config = DatabaseConfig()
    
    # Mock the _log_config method to verify it's called
    original_log_config = config._log_config
    called = [False]
    
    def mock_log_config():
        called[0] = True
    
    config._log_config = mock_log_config
    
    # Set verbose to True and verify it calls _log_config
    config.set_verbose(True)
    assert config.verbose is True
    assert called[0] is True
    
    # Reset for next test
    config._log_config = original_log_config
    
    # Set verbose to False and verify it doesn't call _log_config
    called[0] = False
    config.set_verbose(False)
    assert config.verbose is False
    assert called[0] is False


def test_log_config(setup_env, reset_singleton):
    """Test _log_config method."""
    os.environ['OLLAMA_DB_ENABLED'] = 'true'
    os.environ['VECTOR_DB_ENABLED'] = 'true'
    os.environ['HISTORY_DB_ENABLED'] = 'false'
    
    config = DatabaseConfig()
    # Just verify the function runs without errors
    config._log_config()  # Will raise an exception if there's an issue


def test_global_instance(setup_env, reset_singleton):
    """Test the global db_config instance."""
    from ai_tools.config.database import db_config
    assert isinstance(db_config, DatabaseConfig)
    
    # Verify it's the same instance
    local_config = DatabaseConfig()
    assert db_config is local_config
    
    # Verify that modifying the global instance also affects new instances
    db_config.custom_attr = "test_value"
    another_config = DatabaseConfig()
    assert hasattr(another_config, "custom_attr")
    assert another_config.custom_attr == "test_value"