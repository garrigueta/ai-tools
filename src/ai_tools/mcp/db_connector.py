""" Add database connector actions to MCP """
import os
import sys
import json
from typing import Dict, List, Any, Optional

# Add parent directory to path to import from lib

from ai_tools.storage.docs import search_documents, vectorize_documents, load_vector_db
from ai_tools.chat.history import ChatHistoryManager
from ai_tools.config.database import db_config

# Initialize a chat history manager
chat_history_manager = ChatHistoryManager()

# Store the vector_db instance
_vector_db_instance = None

def get_vector_db():
    """
    Get or initialize the vector database instance.
    
    Returns:
        The initialized vector database or None if initialization fails
    """
    global _vector_db_instance
    
    if _vector_db_instance is not None:
        return _vector_db_instance
        
    try:
        # Load the vector database using the configuration
        vector_config = db_config.get_vector_db_config()
        db_name = os.getenv("DEFAULT_VECTOR_DB", "default")
        
        # Initialize the vector database
        _vector_db_instance = load_vector_db(db_name)
        
        # Set initialized flag based on whether loading was successful
        if _vector_db_instance:
            _vector_db_instance.initialized = True
        else:
            # Create a simple placeholder for testing
            from types import SimpleNamespace
            _vector_db_instance = SimpleNamespace(
                initialized=False,
                search=lambda query, limit=3: [],
                add_text=lambda text, metadata=None, db_name=None: None
            )
            print("Warning: Using placeholder vector DB - search functionality will be limited")
            
        return _vector_db_instance
    except Exception as e:
        print(f"Error initializing vector database: {str(e)}")
        # Return a placeholder object with minimal functionality for testing
        from types import SimpleNamespace
        _vector_db_instance = SimpleNamespace(
            initialized=False,
            search=lambda query, limit=3: [],
            add_text=lambda text, metadata=None, db_name=None: None
        )
        return _vector_db_instance

def mcp_vectorize_documents(directory_path: str, db_name: str = "default") -> Dict[str, Any]:
    """
    MCP action to vectorize documents from a directory
    
    Args:
        directory_path: Path to directory containing documents
        db_name: Name to give the vector database
        
    Returns:
        Status information about the vectorization process
    """
    try:
        # Get LLM configuration from the unified config
        llm_config = db_config.get_llm_config()
        vector_config = db_config.get_vector_db_config()
        
        print(f"Vectorizing documents from {directory_path} to database {db_name}")
        print(f"Using LLM at {llm_config['host']}:{llm_config['port']} with model {llm_config['model']}")
        print(f"Vector storage: {'External database' if vector_config['enabled'] else 'Local files'}")
        
        db_path = vectorize_documents(directory_path, db_name=db_name)
        
        if db_path:
            return {
                "status": "success",
                "message": f"Documents vectorized successfully from {directory_path}",
                "db_path": db_path,
                "db_name": db_name,
                "storage_type": "external" if vector_config['enabled'] else "local"
            }
        else:
            return {
                "status": "error",
                "message": f"No documents found in {directory_path}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error vectorizing documents: {str(e)}"
        }

def mcp_query_documents(query: str, db_name: str = "default", k: int = 5) -> Dict[str, Any]:
    """
    MCP action to query the vector database for relevant documents
    
    Args:
        query: The query string to search for
        db_name: The name of the vector database to search
        k: Number of results to return
        
    Returns:
        Search results with relevant documents
    """
    try:
        # Get LLM and vector database configuration from the unified config
        llm_config = db_config.get_llm_config()
        vector_config = db_config.get_vector_db_config()
        
        print(f"Searching for '{query}' in database {db_name}")
        print(f"Using LLM at {llm_config['host']}:{llm_config['port']} with model {llm_config['model']}")
        print(f"Vector storage: {'External database' if vector_config['enabled'] else 'Local files'}")
        
        results = search_documents(query, db_name, k=k)
        
        if results:
            return {
                "status": "success",
                "query": query,
                "results": results,
                "result_count": len(results),
                "db_name": db_name,
                "storage_type": "external" if vector_config['enabled'] else "local"
            }
        else:
            return {
                "status": "no_results",
                "message": f"No results found for query: {query}",
                "db_name": db_name
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error searching documents: {str(e)}"
        }

def mcp_list_vector_databases() -> Dict[str, Any]:
    """
    MCP action to list all available vector databases
    
    Returns:
        List of available vector databases
    """
    try:
        # Get vector database configuration from the unified config
        vector_config = db_config.get_vector_db_config()
        
        # Check if using external vector database
        if vector_config['enabled']:
            return _mcp_list_external_vector_databases()
            
        # Get vector DB path from config
        vector_db_path = vector_config['local_path']
        
        if not os.path.exists(vector_db_path):
            return {
                "status": "no_databases",
                "message": "No vector databases found"
            }
        
        databases = []
        for db_name in os.listdir(vector_db_path):
            db_path = os.path.join(vector_db_path, db_name)
            if os.path.isdir(db_path):
                metadata_path = os.path.join(db_path, "metadata.json")
                metadata = {}
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                    except:
                        pass
                
                databases.append({
                    "name": db_name,
                    "path": db_path,
                    "metadata": metadata,
                    "storage_type": "local"
                })
        
        return {
            "status": "success",
            "databases": databases,
            "count": len(databases)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing vector databases: {str(e)}"
        }

def _mcp_list_external_vector_databases() -> Dict[str, Any]:
    """
    MCP action to list all available external vector databases
    
    Returns:
        List of available external vector databases
    """
    try:
        # Get database configuration from the unified config
        vector_config = db_config.get_vector_db_config()
        
        print(f"Listing vector databases from external source")
        print(f"Connection details: {vector_config['host']}:{vector_config['port']}/{vector_config['dbname']}")
        
        # This is a placeholder - in a real implementation, you would:
        # 1. Connect to your external database
        # 2. Query for available vector databases
        
        # For this demo, return mock data
        return {
            "status": "success",
            "databases": [
                {
                    "name": "mock_db_1",
                    "metadata": {
                        "document_count": 100,
                        "created_at": "2025-03-01T00:00:00.000Z"
                    },
                    "storage_type": "external"
                },
                {
                    "name": "mock_db_2",
                    "metadata": {
                        "document_count": 50,
                        "created_at": "2025-04-01T00:00:00.000Z"
                    },
                    "storage_type": "external"
                }
            ],
            "count": 2
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing external vector databases: {str(e)}"
        }

def mcp_start_chat_session(session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP action to start a new chat session
    
    Args:
        session_id: Optional custom session ID
        
    Returns:
        Information about the new session
    """
    try:
        # Get database and LLM configuration from the unified config
        history_config = db_config.get_history_db_config()
        llm_config = db_config.get_llm_config()
        
        print(f"Starting new chat session")
        print(f"Using {'external' if history_config['enabled'] else 'local'} chat history storage")
        print(f"Using LLM at {llm_config['host']}:{llm_config['port']} with model {llm_config['model']}")
        
        session_id = chat_history_manager.start_new_session(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "message": f"Chat session {session_id} started",
            "storage_type": "external" if history_config['enabled'] else "local"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error starting chat session: {str(e)}"
        }

def mcp_add_chat_message(role: str, content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    MCP action to add a message to the current chat session
    
    Args:
        role: Role of the message sender (user, assistant, system)
        content: Content of the message
        context: Optional context information
        
    Returns:
        Information about the added message
    """
    try:
        message_idx = chat_history_manager.add_message(role, content, context)
        
        # Get history database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        return {
            "status": "success",
            "message_idx": message_idx,
            "session_id": chat_history_manager.session_id,
            "message": f"Message added to session {chat_history_manager.session_id}",
            "storage_type": "external" if history_config['enabled'] else "local"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error adding chat message: {str(e)}"
        }

def mcp_get_chat_history(start_idx: int = 0, end_idx: Optional[int] = None) -> Dict[str, Any]:
    """
    MCP action to get messages from the current chat session
    
    Args:
        start_idx: Starting index (inclusive)
        end_idx: Ending index (exclusive)
        
    Returns:
        Messages from the chat history
    """
    try:
        messages = chat_history_manager.get_messages(start_idx, end_idx)
        
        # Get history database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        return {
            "status": "success",
            "session_id": chat_history_manager.session_id,
            "messages": messages,
            "message_count": len(messages),
            "storage_type": "external" if history_config['enabled'] else "local"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting chat history: {str(e)}"
        }

def mcp_load_chat_session(session_id: str) -> Dict[str, Any]:
    """
    MCP action to load a previous chat session
    
    Args:
        session_id: ID of the session to load
        
    Returns:
        Status of the load operation
    """
    try:
        success = chat_history_manager.load_session(session_id)
        
        # Get history database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        if success:
            return {
                "status": "success",
                "session_id": session_id,
                "message": f"Chat session {session_id} loaded",
                "message_count": len(chat_history_manager.current_history),
                "storage_type": "external" if history_config['enabled'] else "local"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to load chat session {session_id}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error loading chat session: {str(e)}"
        }

def mcp_list_chat_sessions() -> Dict[str, Any]:
    """
    MCP action to list all available chat sessions
    
    Returns:
        List of available chat sessions
    """
    try:
        sessions = chat_history_manager.list_sessions()
        
        # Get history database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions),
            "storage_type": "external" if history_config['enabled'] else "local"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing chat sessions: {str(e)}"
        }

def mcp_query_context_for_prompt(prompt: str, max_results: int = 3, min_score: float = 0.6) -> Dict[str, Any]:
    """
    MCP action to retrieve relevant context for a user prompt across all vector databases.
    This provides AI with useful context without exposing the entire database.
    
    Args:
        prompt: The user prompt to find context for
        max_results: Maximum number of context items to return
        min_score: Minimum relevance score (0-1) for included results
        
    Returns:
        Most relevant context data for the prompt
    """
    try:
        # Get vector database configuration
        vector_config = db_config.get_vector_db_config()
        
        # Get all available vector databases
        available_dbs = []
        if vector_config['enabled']:
            # For external DB, we use the mock implementation for now
            db_list_result = _mcp_list_external_vector_databases()
            if db_list_result["status"] == "success":
                available_dbs = [db["name"] for db in db_list_result["databases"]]
        else:
            # For local DB, get the actual list of databases
            vector_db_path = vector_config['local_path']
            if os.path.exists(vector_db_path):
                available_dbs = [
                    d for d in os.listdir(vector_db_path) 
                    if os.path.isdir(os.path.join(vector_db_path, d))
                ]
        
        # No databases found
        if not available_dbs:
            return {
                "status": "no_databases",
                "message": "No vector databases available to search for context"
            }
            
        # Search all databases for relevant content
        all_results = []
        for db_name in available_dbs:
            try:
                # Search this database
                results = search_documents(prompt, db_name, k=max_results)
                if results:
                    # Add database name to each result for tracking
                    for result in results:
                        result["database"] = db_name
                    all_results.extend(results)
            except Exception as e:
                print(f"Error searching database {db_name}: {str(e)}")
                continue
        
        # Filter by minimum score and sort by relevance
        filtered_results = [
            r for r in all_results 
            if r.get("relevance_score", 0) >= min_score
        ]
        sorted_results = sorted(
            filtered_results, 
            key=lambda x: x.get("relevance_score", 0), 
            reverse=True
        )
        
        # Take the top results
        top_results = sorted_results[:max_results]
        
        if not top_results:
            return {
                "status": "no_results",
                "message": f"No relevant context found for prompt: {prompt}"
            }
            
        # Format response with only the needed information
        context_items = []
        for result in top_results:
            context_items.append({
                "content": result["content"],
                "source": result.get("metadata", {}).get("source", "unknown"),
                "relevance": result.get("relevance_score", 0),
                "database": result.get("database", "unknown")
            })
            
        return {
            "status": "success",
            "context_items": context_items,
            "count": len(context_items),
            "prompt": prompt
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving context: {str(e)}"
        }


def mcp_get_recent_conversations(max_sessions: int = 3, max_messages_per_session: int = 10) -> Dict[str, Any]:
    """
    MCP action to retrieve recent conversation history to provide conversational context
    to the AI without giving full database access.
    
    Args:
        max_sessions: Maximum number of recent sessions to retrieve
        max_messages_per_session: Maximum messages to retrieve per session
        
    Returns:
        Recent conversation history
    """
    try:
        # Get available sessions
        all_sessions = chat_history_manager.list_sessions()
        
        # Return if no sessions found
        if not all_sessions:
            return {
                "status": "no_sessions",
                "message": "No chat history sessions available"
            }
            
        # Sort by recency (should already be sorted, but ensure it)
        sorted_sessions = sorted(
            all_sessions, 
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        
        # Take only the most recent sessions
        recent_sessions = sorted_sessions[:max_sessions]
        
        # Get messages for each recent session
        session_data = []
        current_session_data = None
        
        # First add the current session if it exists
        if chat_history_manager.session_id:
            current_messages = chat_history_manager.get_messages()
            # Only include if there are messages
            if current_messages:
                # Take most recent messages if over the limit
                recent_messages = current_messages[-max_messages_per_session:] if len(current_messages) > max_messages_per_session else current_messages
                
                # Format for response
                current_session_data = {
                    "session_id": chat_history_manager.session_id,
                    "is_current": True,
                    "messages": recent_messages,
                    "message_count": len(recent_messages),
                    "total_messages": len(current_messages)
                }
                session_data.append(current_session_data)
        
        # Now add other recent sessions (up to the max)
        remaining_sessions = max_sessions - (1 if current_session_data else 0)
        for session in recent_sessions[:remaining_sessions]:
            session_id = session.get("id")
            
            # Skip current session as we already added it
            if current_session_data and session_id == chat_history_manager.session_id:
                continue
                
            # Load the session temporarily
            temp_manager = ChatHistoryManager()
            if temp_manager.load_session(session_id):
                messages = temp_manager.get_messages()
                
                # Take most recent messages if over the limit
                recent_messages = messages[-max_messages_per_session:] if len(messages) > max_messages_per_session else messages
                
                session_data.append({
                    "session_id": session_id,
                    "is_current": False,
                    "messages": recent_messages,
                    "message_count": len(recent_messages),
                    "total_messages": len(messages),
                    "created_at": session.get("created_at")
                })
        
        return {
            "status": "success",
            "sessions": session_data,
            "count": len(session_data)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving recent conversations: {str(e)}"
        }


def mcp_get_document_metadata(db_name: str = None) -> Dict[str, Any]:
    """
    MCP action to retrieve metadata about available documents without exposing
    their full content, helping the AI understand what knowledge is available.
    
    Args:
        db_name: Optional specific database to query, or None for all databases
        
    Returns:
        Document metadata information
    """
    try:
        # Get vector database configuration
        vector_config = db_config.get_vector_db_config()
        
        # Determine which databases to check
        available_dbs = []
        if db_name:
            available_dbs = [db_name]
        elif vector_config['enabled']:
            # For external DB, we use the mock implementation for now
            db_list_result = _mcp_list_external_vector_databases()
            if db_list_result["status"] == "success":
                available_dbs = [db["name"] for db in db_list_result["databases"]]
        else:
            # For local DB, get the actual list of databases
            vector_db_path = vector_config['local_path']
            if os.path.exists(vector_db_path):
                available_dbs = [
                    d for d in os.listdir(vector_db_path) 
                    if os.path.isdir(os.path.join(vector_db_path, d))
                ]
        
        # No databases found
        if not available_dbs:
            return {
                "status": "no_databases",
                "message": "No vector databases available to retrieve metadata"
            }
            
        # Collect metadata for each database
        database_info = []
        for db in available_dbs:
            db_metadata = {}
            
            if vector_config['enabled']:
                # For external DB, we currently don't have a way to get metadata
                # This is a placeholder for future implementation
                db_metadata = {
                    "name": db,
                    "storage_type": "external",
                    "document_count": "unknown",
                    "source_types": [],
                    "topics": [],
                    "created_at": "unknown"
                }
            else:
                # For local DB, read the metadata file if it exists
                metadata_path = os.path.join(vector_config['local_path'], db, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as f:
                            raw_metadata = json.load(f)
                            
                        # Extract relevant metadata fields
                        db_metadata = {
                            "name": db,
                            "storage_type": "local",
                            "document_count": raw_metadata.get("document_count", "unknown"),
                            "source_directory": raw_metadata.get("source_directory", "unknown"),
                            "model": raw_metadata.get("model", "unknown"),
                            "created_at": raw_metadata.get("created_at", "unknown")
                        }
                    except Exception as e:
                        print(f"Error reading metadata for {db}: {str(e)}")
                        db_metadata = {
                            "name": db,
                            "storage_type": "local",
                            "document_count": "unknown",
                            "error": f"Could not read metadata: {str(e)}"
                        }
                else:
                    db_metadata = {
                        "name": db,
                        "storage_type": "local",
                        "document_count": "unknown",
                        "note": "No metadata file found"
                    }
            
            database_info.append(db_metadata)
            
        return {
            "status": "success",
            "databases": database_info,
            "count": len(database_info)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving document metadata: {str(e)}"
        }