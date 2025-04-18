"""Unit tests for the MCP database connector module."""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open

from ai_tools.mcp.db_connector import (
    mcp_vectorize_documents,
    mcp_query_documents,
    mcp_list_vector_databases,
    _mcp_list_external_vector_databases,
    mcp_start_chat_session,
    mcp_add_chat_message,
    mcp_get_chat_history,
    mcp_load_chat_session,
    mcp_list_chat_sessions,
    mcp_query_context_for_prompt,
    mcp_get_recent_conversations,
    mcp_get_document_metadata,
    chat_history_manager
)


@pytest.fixture
def reset_chat_manager():
    """Reset the chat history manager after tests"""
    # Save original manager
    original_manager = chat_history_manager
    yield
    # Replace with a fresh manager
    from ai_tools.mcp.db_connector import chat_history_manager as current_manager
    from ai_tools.chat.history import ChatHistoryManager
    if hasattr(current_manager, 'session_id'):
        current_manager.session_id = None
    if hasattr(current_manager, 'current_history'):
        current_manager.current_history = []


@pytest.fixture
def mock_vector_config():
    """Mock the vector database configuration"""
    return {
        'enabled': False,
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
        'dbname': 'test_db',
        'table_prefix': 'vector_',
        'local_path': '/tmp/test_vectors'
    }


@pytest.fixture
def mock_llm_config():
    """Mock the LLM configuration"""
    return {
        'host': 'localhost',
        'port': 11434,
        'model': 'test-model',
        'api_key': ''
    }


@pytest.fixture
def mock_history_config():
    """Mock the history database configuration"""
    return {
        'enabled': False,
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'postgres',
        'dbname': 'test_db',
        'table_prefix': 'history_',
        'local_path': '/tmp/test_history'
    }


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.vectorize_documents')
def test_mcp_vectorize_documents_success(mock_vectorize, mock_db_config, mock_vector_config, mock_llm_config, capsys):
    """Test successful document vectorization"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    mock_vectorize.return_value = '/tmp/test_vectors/test_db'
    
    # Call the function
    result = mcp_vectorize_documents('/path/to/docs', 'test_db')
    
    # Verify function was called with correct arguments
    mock_vectorize.assert_called_once_with('/path/to/docs', db_name='test_db')
    
    # Check the result
    assert result['status'] == 'success'
    assert result['message'] == 'Documents vectorized successfully from /path/to/docs'
    assert result['db_path'] == '/tmp/test_vectors/test_db'
    assert result['db_name'] == 'test_db'
    assert result['storage_type'] == 'local'
    
    # Check console output
    captured = capsys.readouterr()
    assert "Vectorizing documents from /path/to/docs to database test_db" in captured.out
    assert "Using LLM at localhost:11434 with model test-model" in captured.out
    assert "Vector storage: Local files" in captured.out


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.vectorize_documents')
def test_mcp_vectorize_documents_no_docs(mock_vectorize, mock_db_config, mock_vector_config, mock_llm_config, capsys):
    """Test vectorization with no documents found"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    mock_vectorize.return_value = None
    
    # Call the function
    result = mcp_vectorize_documents('/path/to/docs', 'test_db')
    
    # Check the result
    assert result['status'] == 'error'
    assert result['message'] == 'No documents found in /path/to/docs'


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.vectorize_documents')
def test_mcp_vectorize_documents_exception(mock_vectorize, mock_db_config, mock_vector_config, mock_llm_config):
    """Test vectorization with an exception"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    mock_vectorize.side_effect = Exception("Test error")
    
    # Call the function
    result = mcp_vectorize_documents('/path/to/docs', 'test_db')
    
    # Check the result
    assert result['status'] == 'error'
    assert result['message'] == 'Error vectorizing documents: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.search_documents')
def test_mcp_query_documents_success(mock_search, mock_db_config, mock_vector_config, mock_llm_config, capsys):
    """Test successful document query"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    mock_search.return_value = [
        {'content': 'Test content 1', 'metadata': {'source': 'file1.txt'}, 'relevance_score': 0.95},
        {'content': 'Test content 2', 'metadata': {'source': 'file2.txt'}, 'relevance_score': 0.85}
    ]
    
    # Call the function
    result = mcp_query_documents('test query', 'test_db', 2)
    
    # Verify function was called with correct arguments
    mock_search.assert_called_once_with('test query', 'test_db', k=2)
    
    # Check the result
    assert result['status'] == 'success'
    assert result['query'] == 'test query'
    assert len(result['results']) == 2
    assert result['result_count'] == 2
    assert result['db_name'] == 'test_db'
    assert result['storage_type'] == 'local'
    
    # Check console output
    captured = capsys.readouterr()
    assert "Searching for 'test query' in database test_db" in captured.out
    assert "Using LLM at localhost:11434 with model test-model" in captured.out
    assert "Vector storage: Local files" in captured.out


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.search_documents')
def test_mcp_query_documents_no_results(mock_search, mock_db_config, mock_vector_config, mock_llm_config):
    """Test document query with no results"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    mock_search.return_value = []
    
    # Call the function
    result = mcp_query_documents('test query', 'test_db', 5)
    
    # Check the result
    assert result['status'] == 'no_results'
    assert 'No results found for query: test query' in result['message']
    assert result['db_name'] == 'test_db'


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.search_documents')
def test_mcp_query_documents_exception(mock_search, mock_db_config, mock_vector_config, mock_llm_config):
    """Test document query with an exception"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    mock_search.side_effect = Exception("Test error")
    
    # Call the function
    result = mcp_query_documents('test query', 'test_db', 5)
    
    # Check the result
    assert result['status'] == 'error'
    assert result['message'] == 'Error searching documents: Test error'


@patch('ai_tools.mcp.db_connector.os.path.exists')
@patch('ai_tools.mcp.db_connector.os.listdir')
@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_list_vector_databases_local_success(mock_db_config, mock_listdir, mock_exists, mock_vector_config):
    """Test listing local vector databases successfully"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_exists.return_value = True
    mock_listdir.return_value = ['db1', 'db2']
    
    # Mock isdir and open function
    with patch('ai_tools.mcp.db_connector.os.path.isdir', return_value=True), \
         patch('ai_tools.mcp.db_connector.os.path.join', side_effect=lambda *args: '/'.join(args)), \
         patch('ai_tools.mcp.db_connector.open', mock_open(read_data='{"document_count": 10}')):
        
        # Call the function
        result = mcp_list_vector_databases()
        
        # Check the result
        assert result['status'] == 'success'
        assert len(result['databases']) == 2
        assert result['count'] == 2
        assert result['databases'][0]['name'] == 'db1'
        assert result['databases'][1]['name'] == 'db2'
        assert result['databases'][0]['storage_type'] == 'local'
        
        # Verify that exists was called with the path from config (relaxing the once condition)
        mock_exists.assert_any_call('/tmp/test_vectors')
        mock_listdir.assert_called_once_with('/tmp/test_vectors')


@patch('ai_tools.mcp.db_connector.os.path.exists')
@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_list_vector_databases_local_no_dir(mock_db_config, mock_exists, mock_vector_config):
    """Test listing local vector databases when directory doesn't exist"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_exists.return_value = False
    
    # Call the function
    result = mcp_list_vector_databases()
    
    # Check the result
    assert result['status'] == 'no_databases'
    assert result['message'] == 'No vector databases found'


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector._mcp_list_external_vector_databases')
def test_mcp_list_vector_databases_external(mock_list_external, mock_db_config):
    """Test listing external vector databases"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = {'enabled': True}
    mock_list_external.return_value = {
        'status': 'success',
        'databases': [{'name': 'ext_db1'}, {'name': 'ext_db2'}],
        'count': 2
    }
    
    # Call the function
    result = mcp_list_vector_databases()
    
    # Check the result
    assert result['status'] == 'success'
    assert len(result['databases']) == 2
    assert result['count'] == 2
    
    # Verify that the external function was called
    mock_list_external.assert_called_once()


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_list_external_vector_databases(mock_db_config, mock_vector_config, capsys):
    """Test the _mcp_list_external_vector_databases function"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    
    # Call the function
    result = _mcp_list_external_vector_databases()
    
    # Check the result
    assert result['status'] == 'success'
    assert len(result['databases']) == 2
    assert result['count'] == 2
    assert result['databases'][0]['name'] == 'mock_db_1'
    assert result['databases'][1]['name'] == 'mock_db_2'
    
    # Check console output
    captured = capsys.readouterr()
    assert "Listing vector databases from external source" in captured.out


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_list_external_vector_databases_exception(mock_db_config):
    """Test the _mcp_list_external_vector_databases function with an exception"""
    # Setup mocks
    mock_db_config.get_vector_db_config.side_effect = Exception("Test error")
    
    # Call the function
    result = _mcp_list_external_vector_databases()
    
    # Check the result
    assert result['status'] == 'error'
    assert result['message'] == 'Error listing external vector databases: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_start_chat_session(mock_db_config, mock_history_config, mock_llm_config, capsys, reset_chat_manager):
    """Test starting a new chat session"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'start_new_session', return_value='test-session-123'):
        # Call the function
        result = mcp_start_chat_session()
        
        # Check the result
        assert result['status'] == 'success'
        assert result['session_id'] == 'test-session-123'
        assert result['message'] == 'Chat session test-session-123 started'
        assert result['storage_type'] == 'local'
        
        # Check console output
        captured = capsys.readouterr()
        assert "Starting new chat session" in captured.out
        assert "Using local chat history storage" in captured.out


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_start_chat_session_custom_id(mock_db_config, mock_history_config, mock_llm_config, reset_chat_manager):
    """Test starting a new chat session with a custom ID"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    mock_db_config.get_llm_config.return_value = mock_llm_config
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'start_new_session', return_value='custom-id'):
        # Call the function
        result = mcp_start_chat_session('custom-id')
        
        # Check the result
        assert result['status'] == 'success'
        assert result['session_id'] == 'custom-id'
        assert result['message'] == 'Chat session custom-id started'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_start_chat_session_exception(mock_db_config, reset_chat_manager):
    """Test starting a chat session with an exception"""
    # Setup mocks
    mock_db_config.get_history_db_config.side_effect = Exception("Test error")
    
    # Call the function
    result = mcp_start_chat_session()
    
    # Check the result
    assert result['status'] == 'error'
    assert result['message'] == 'Error starting chat session: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_add_chat_message(mock_db_config, mock_history_config, reset_chat_manager):
    """Test adding a chat message"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'add_message', return_value=0) as mock_add_message, \
         patch.object(chat_history_manager, 'session_id', 'test-session-123'):
        
        # Call the function
        result = mcp_add_chat_message('user', 'Hello, world!')
        
        # Check that add_message was called with right arguments
        mock_add_message.assert_called_once_with('user', 'Hello, world!', None)
        
        # Check the result
        assert result['status'] == 'success'
        assert result['message_idx'] == 0
        assert result['session_id'] == 'test-session-123'
        assert 'Message added to session test-session-123' in result['message']
        assert result['storage_type'] == 'local'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_add_chat_message_with_context(mock_db_config, mock_history_config, reset_chat_manager):
    """Test adding a chat message with context"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    context = {'source': 'test', 'timestamp': 123456789}
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'add_message', return_value=0) as mock_add_message, \
         patch.object(chat_history_manager, 'session_id', 'test-session-123'):
        
        # Call the function
        result = mcp_add_chat_message('user', 'Hello, world!', context)
        
        # Check that add_message was called with right arguments
        mock_add_message.assert_called_once_with('user', 'Hello, world!', context)


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_add_chat_message_exception(mock_db_config, reset_chat_manager):
    """Test adding a chat message with an exception"""
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'add_message', side_effect=Exception("Test error")):
        
        # Call the function
        result = mcp_add_chat_message('user', 'Hello, world!')
        
        # Check the result
        assert result['status'] == 'error'
        assert result['message'] == 'Error adding chat message: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_get_chat_history(mock_db_config, mock_history_config, reset_chat_manager):
    """Test getting chat history messages"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    messages = [
        {'role': 'user', 'content': 'Hello', 'timestamp': 123456789},
        {'role': 'assistant', 'content': 'Hi there!', 'timestamp': 123456790}
    ]
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'get_messages', return_value=messages) as mock_get_messages, \
         patch.object(chat_history_manager, 'session_id', 'test-session-123'):
        
        # Call the function
        result = mcp_get_chat_history(0, 2)
        
        # Check that get_messages was called with right arguments
        mock_get_messages.assert_called_once_with(0, 2)
        
        # Check the result
        assert result['status'] == 'success'
        assert result['session_id'] == 'test-session-123'
        assert result['messages'] == messages
        assert result['message_count'] == 2
        assert result['storage_type'] == 'local'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_get_chat_history_exception(mock_db_config, reset_chat_manager):
    """Test getting chat history with an exception"""
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'get_messages', side_effect=Exception("Test error")):
        
        # Call the function
        result = mcp_get_chat_history()
        
        # Check the result
        assert result['status'] == 'error'
        assert result['message'] == 'Error getting chat history: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_load_chat_session_success(mock_db_config, mock_history_config, reset_chat_manager):
    """Test loading a chat session successfully"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'load_session', return_value=True) as mock_load_session, \
         patch.object(chat_history_manager, 'current_history', [{'role': 'user', 'content': 'Hello'}, {'role': 'assistant', 'content': 'Hi'}]):
        
        # Call the function
        result = mcp_load_chat_session('test-session-123')
        
        # Check that load_session was called with right arguments
        mock_load_session.assert_called_once_with('test-session-123')
        
        # Check the result
        assert result['status'] == 'success'
        assert result['session_id'] == 'test-session-123'
        assert result['message'] == 'Chat session test-session-123 loaded'
        assert result['message_count'] == 2
        assert result['storage_type'] == 'local'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_load_chat_session_failure(mock_db_config, mock_history_config, reset_chat_manager):
    """Test loading a chat session with failure"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'load_session', return_value=False) as mock_load_session:
        
        # Call the function
        result = mcp_load_chat_session('invalid-session')
        
        # Check the result
        assert result['status'] == 'error'
        assert result['message'] == 'Failed to load chat session invalid-session'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_load_chat_session_exception(mock_db_config, reset_chat_manager):
    """Test loading a chat session with an exception"""
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'load_session', side_effect=Exception("Test error")):
        
        # Call the function
        result = mcp_load_chat_session('test-session-123')
        
        # Check the result
        assert result['status'] == 'error'
        assert result['message'] == 'Error loading chat session: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_list_chat_sessions_success(mock_db_config, mock_history_config, reset_chat_manager):
    """Test listing chat sessions successfully"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    sessions = [
        {'id': 'session1', 'created_at': '2025-04-01T10:00:00Z', 'message_count': 5},
        {'id': 'session2', 'created_at': '2025-04-02T10:00:00Z', 'message_count': 3}
    ]
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'list_sessions', return_value=sessions) as mock_list_sessions:
        
        # Call the function
        result = mcp_list_chat_sessions()
        
        # Check that list_sessions was called
        mock_list_sessions.assert_called_once()
        
        # Check the result
        assert result['status'] == 'success'
        assert result['sessions'] == sessions
        assert result['count'] == 2
        assert result['storage_type'] == 'local'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_list_chat_sessions_exception(mock_db_config, reset_chat_manager):
    """Test listing chat sessions with an exception"""
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'list_sessions', side_effect=Exception("Test error")):
        
        # Call the function
        result = mcp_list_chat_sessions()
        
        # Check the result
        assert result['status'] == 'error'
        assert result['message'] == 'Error listing chat sessions: Test error'


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector._mcp_list_external_vector_databases')
@patch('ai_tools.mcp.db_connector.search_documents')
def test_mcp_query_context_for_prompt_success(mock_search, mock_list_external, mock_db_config, mock_vector_config):
    """Test querying context for a prompt successfully"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    
    # Mock external DBs listing
    mock_list_external.return_value = {
        'status': 'success',
        'databases': [{'name': 'ext_db1'}, {'name': 'ext_db2'}],
        'count': 2
    }
    
    # Mock search results
    search_results = [
        {
            'content': 'Test content 1', 
            'metadata': {'source': 'file1.txt'}, 
            'relevance_score': 0.95
        },
        {
            'content': 'Test content 2', 
            'metadata': {'source': 'file2.txt'}, 
            'relevance_score': 0.85
        },
        {
            'content': 'Test content 3', 
            'metadata': {'source': 'file3.txt'}, 
            'relevance_score': 0.75
        },
        {
            'content': 'Test content 4', 
            'metadata': {'source': 'file4.txt'}, 
            'relevance_score': 0.65
        },
        {
            'content': 'Test content 5', 
            'metadata': {'source': 'file5.txt'}, 
            'relevance_score': 0.55
        }
    ]
    mock_search.return_value = search_results
    
    # Mock os.path exists and listdir for local DBs
    with patch('ai_tools.mcp.db_connector.os.path.exists', return_value=True), \
         patch('ai_tools.mcp.db_connector.os.listdir', return_value=['local_db1', 'local_db2']), \
         patch('ai_tools.mcp.db_connector.os.path.isdir', return_value=True):
        
        # Call the function
        result = mcp_query_context_for_prompt('test query', max_results=2, min_score=0.7)
        
        # Check that search was called multiple times (once per DB)
        assert mock_search.call_count >= 2
        
        # Check the result
        assert result['status'] == 'success'
        assert len(result['context_items']) == 2
        assert result['count'] == 2
        assert result['prompt'] == 'test query'
        
        # Verify we got the highest relevance items above our min_score threshold
        assert result['context_items'][0]['relevance'] >= 0.7
        assert result['context_items'][1]['relevance'] >= 0.7
        assert result['context_items'][0]['relevance'] >= result['context_items'][1]['relevance']


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.os.path.exists')
@patch('ai_tools.mcp.db_connector.os.listdir')
def test_mcp_query_context_for_prompt_no_databases(mock_listdir, mock_exists, mock_db_config, mock_vector_config):
    """Test querying context when no databases are available"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_exists.return_value = False
    mock_listdir.return_value = []
    
    # Call the function
    result = mcp_query_context_for_prompt('test query')
    
    # Check the result
    assert result['status'] == 'no_databases'
    assert 'No vector databases available' in result['message']


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.os.path.exists')
@patch('ai_tools.mcp.db_connector.os.listdir')
@patch('ai_tools.mcp.db_connector.search_documents')
def test_mcp_query_context_for_prompt_no_results(mock_search, mock_listdir, mock_exists, mock_db_config, mock_vector_config):
    """Test querying context when no results are found"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_exists.return_value = True
    mock_listdir.return_value = ['local_db1']
    
    # Mock search with low relevance results below threshold
    mock_search.return_value = [
        {'content': 'Low relevance', 'metadata': {'source': 'file1.txt'}, 'relevance_score': 0.3}
    ]
    
    with patch('ai_tools.mcp.db_connector.os.path.isdir', return_value=True):
        # Call the function with high min_score
        result = mcp_query_context_for_prompt('test query', min_score=0.6)
        
        # Check the result
        assert result['status'] == 'no_results'
        assert 'No relevant context found for prompt' in result['message']


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_get_recent_conversations_no_sessions(mock_db_config, mock_history_config, reset_chat_manager):
    """Test getting recent conversations when no sessions exist"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'list_sessions', return_value=[]):
        
        # Call the function
        result = mcp_get_recent_conversations()
        
        # Check the result
        assert result['status'] == 'no_sessions'
        assert result['message'] == 'No chat history sessions available'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_get_recent_conversations_with_current(mock_db_config, mock_history_config, reset_chat_manager):
    """Test getting recent conversations with a current session"""
    # Setup mocks
    mock_db_config.get_history_db_config.return_value = mock_history_config
    
    current_messages = [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there!'}
    ]
    
    sessions = [
        {'id': 'session1', 'created_at': '2025-04-01T10:00:00Z'},
        {'id': 'session2', 'created_at': '2025-04-02T10:00:00Z'}
    ]
    
    # Replace chat_history_manager methods
    with patch.object(chat_history_manager, 'session_id', 'current-session'), \
         patch.object(chat_history_manager, 'get_messages', return_value=current_messages), \
         patch.object(chat_history_manager, 'list_sessions', return_value=sessions), \
         patch.object(chat_history_manager, 'current_history', current_messages):
            
        # Create a mock ChatHistoryManager for loading other sessions
        mock_temp_manager = MagicMock()
        mock_temp_manager.load_session.return_value = True
        mock_temp_manager.get_messages.return_value = [{'role': 'user', 'content': 'Old message'}]
        
        with patch('ai_tools.mcp.db_connector.ChatHistoryManager', return_value=mock_temp_manager):
            # Call the function
            result = mcp_get_recent_conversations(max_sessions=2, max_messages_per_session=5)
            
            # Check the result
            assert result['status'] == 'success'
            assert len(result['sessions']) == 2
            assert result['count'] == 2
            
            # Verify current session is included
            assert any(s['is_current'] for s in result['sessions'])
            assert any(s['session_id'] == 'current-session' for s in result['sessions'])


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.os.path.exists')
@patch('ai_tools.mcp.db_connector.os.listdir')
@patch('ai_tools.mcp.db_connector.os.path.isdir')
@patch('ai_tools.mcp.db_connector.open', new_callable=mock_open)
def test_mcp_get_document_metadata_local(mock_open, mock_isdir, mock_listdir, mock_exists, mock_db_config, mock_vector_config):
    """Test getting document metadata from local storage"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_exists.return_value = True
    mock_listdir.return_value = ['db1', 'db2']
    mock_isdir.return_value = True
    
    # Mock reading metadata file
    metadata_content = json.dumps({
        "document_count": 10,
        "source_directory": "/path/to/docs",
        "model": "test-model",
        "created_at": "2025-04-01T10:00:00Z"
    })
    mock_open.return_value.__enter__.return_value.read.return_value = metadata_content
    
    # Call the function
    result = mcp_get_document_metadata()
    
    # Check the result
    assert result['status'] == 'success'
    assert len(result['databases']) == 2
    assert result['count'] == 2
    assert result['databases'][0]['name'] == 'db1'
    assert result['databases'][0]['storage_type'] == 'local'
    assert result['databases'][0]['document_count'] == 10
    assert result['databases'][0]['source_directory'] == '/path/to/docs'


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector.os.path.exists')
def test_mcp_get_document_metadata_no_databases(mock_exists, mock_db_config, mock_vector_config):
    """Test getting document metadata when no databases are available"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    mock_exists.return_value = False
    
    # Call the function
    result = mcp_get_document_metadata()
    
    # Check the result
    assert result['status'] == 'no_databases'
    assert 'No vector databases available' in result['message']


@patch('ai_tools.mcp.db_connector.db_config')
@patch('ai_tools.mcp.db_connector._mcp_list_external_vector_databases')
def test_mcp_get_document_metadata_external(mock_list_external, mock_db_config):
    """Test getting document metadata from external storage"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = {'enabled': True}
    mock_list_external.return_value = {
        'status': 'success',
        'databases': [{'name': 'ext_db1'}, {'name': 'ext_db2'}],
        'count': 2
    }
    
    # Call the function
    result = mcp_get_document_metadata()
    
    # Check the result
    assert result['status'] == 'success'
    assert len(result['databases']) == 2
    assert result['count'] == 2
    assert result['databases'][0]['name'] == 'ext_db1'
    assert result['databases'][0]['storage_type'] == 'external'


@patch('ai_tools.mcp.db_connector.db_config')
def test_mcp_get_document_metadata_specific_db(mock_db_config, mock_vector_config):
    """Test getting document metadata for a specific database"""
    # Setup mocks
    mock_db_config.get_vector_db_config.return_value = mock_vector_config
    
    # Mock path exists, isdir and open functions
    with patch('ai_tools.mcp.db_connector.os.path.exists', return_value=True), \
         patch('ai_tools.mcp.db_connector.os.path.isdir', return_value=True), \
         patch('ai_tools.mcp.db_connector.os.path.join', side_effect=lambda *args: '/'.join(args)), \
         patch('ai_tools.mcp.db_connector.open', mock_open(read_data='{"document_count": 5}')):
        
        # Call the function
        result = mcp_get_document_metadata('specific_db')
        
        # Check the result
        assert result['status'] == 'success'
        assert len(result['databases']) == 1
        assert result['count'] == 1
        assert result['databases'][0]['name'] == 'specific_db'