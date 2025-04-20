import os
import json
import datetime
from typing import List, Dict, Tuple, Optional, Any, Union, Collection, cast
from pathlib import Path

# Import the unified database configuration
from ai_tools.config.database import db_config

# Use unified database configuration
CHAT_HISTORY_PATH = db_config.history_db_path
EXTERNAL_HISTORY_DB_ENABLED = db_config.history_db_enabled

# Determine if we're using the external DB
def using_external_db():
    return EXTERNAL_HISTORY_DB_ENABLED


class ChatHistoryManager:
    """
    Manages storage and retrieval of chat history
    """
    
    def __init__(self, history_dir: Optional[str] = None):
        """
        Initialize the chat history manager
        
        Args:
            history_dir: Directory to store chat histories. Defaults to data/chat_history
        """
        self.history_dir = history_dir or CHAT_HISTORY_PATH
        
        # Use local file storage if not using external DB
        if not using_external_db():
            os.makedirs(self.history_dir, exist_ok=True)
            
        # Fix the type annotation to handle complex message structures
        self.current_history: List[Dict[str, Union[str, Dict[str, Any]]]] = []
        self.session_id: Optional[str] = None
        
        # Set up external DB connection if enabled
        if using_external_db():
            # Get database configuration from the unified config
            history_config = db_config.get_history_db_config()
            print(f"Using external chat history database at {history_config['host']}:{history_config['port']}")
            # In a real implementation, you would establish a database connection here
    
    def start_new_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new chat session
        
        Args:
            session_id: Optional custom session ID
            
        Returns:
            The session ID
        """
        self.current_history = []
        self.session_id = session_id or f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save initial session metadata
        metadata = {
            "id": self.session_id,
            "created_at": datetime.datetime.now().isoformat(),
            "message_count": 0
        }
        
        # External DB handling
        if using_external_db():
            self._save_session_metadata_external(metadata)
        else:
            # Local file handling
            session_dir = os.path.join(self.history_dir, self.session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            with open(os.path.join(session_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)
        
        return self.session_id
    
    def add_message(self, role: str, content: str, context: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a message to the current chat history
        
        Args:
            role: The role of the sender (user, assistant, system)
            content: The message content
            context: Optional context information
            
        Returns:
            The index of the added message
        """
        if not self.session_id:
            self.start_new_session()
        
        message = {
            "id": f"msg_{len(self.current_history)}",
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content,
            "context": context or {}
        }
        
        self.current_history.append(message)
        
        # Save the message to storage
        self._save_current_history()
        
        return len(self.current_history) - 1
    
    def get_messages(self, start_idx: int = 0, end_idx: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get messages from the current history
        
        Args:
            start_idx: Starting index (inclusive)
            end_idx: Ending index (exclusive)
            
        Returns:
            List of messages
        """
        if end_idx is None:
            return self.current_history[start_idx:]
        return self.current_history[start_idx:end_idx]
    
    def get_formatted_history(self) -> List[Tuple[Union[str, Dict[str, Any]], Union[str, Dict[str, Any]]]]:
        """
        Get the history in a format suitable for LangChain
        
        Returns:
            List of (human_message, ai_message) tuples
        """
        formatted_history = []
        current_pair = []
        
        for message in self.current_history:
            if message["role"] == "user":
                # Cast content to the expected type to satisfy mypy
                current_pair = [cast(Union[str, Dict[str, Any]], message["content"])]
            elif message["role"] == "assistant" and current_pair:
                # Cast content to the expected type to satisfy mypy
                current_pair.append(cast(Union[str, Dict[str, Any]], message["content"]))
                if len(current_pair) == 2:
                    formatted_history.append((current_pair[0], current_pair[1]))
                    current_pair = []
        
        return formatted_history
    
    def load_session(self, session_id: str) -> bool:
        """
        Load a previous chat session
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            True if session was loaded successfully, False otherwise
        """
        # Check if using external DB
        if using_external_db():
            return self._load_session_external(session_id)
        
        # Using local file storage
        session_dir = os.path.join(self.history_dir, session_id)
        
        if not os.path.exists(session_dir):
            print(f"Session {session_id} not found")
            return False
        
        try:
            history_file = os.path.join(session_dir, "history.json")
            if os.path.exists(history_file):
                with open(history_file, "r") as f:
                    self.current_history = json.load(f)
                self.session_id = session_id
                return True
            else:
                print(f"History file not found for session {session_id}")
                return False
        except Exception as e:
            print(f"Error loading session {session_id}: {str(e)}")
            return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available chat sessions
        
        Returns:
            List of session metadata
        """
        # Check if using external DB
        if using_external_db():
            return self._list_sessions_external()
        
        # Using local file storage
        sessions = []
        
        for session_id in os.listdir(self.history_dir):
            session_dir = os.path.join(self.history_dir, session_id)
            if os.path.isdir(session_dir):
                metadata_file = os.path.join(session_dir, "metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        sessions.append(metadata)
                    except Exception as e:
                        print(f"Error loading metadata for session {session_id}: {str(e)}")
        
        # Sort by creation date, newest first
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return sessions
    
    def _save_current_history(self) -> None:
        """
        Save the current history to storage
        """
        if not self.session_id:
            return
            
        # Check if using external DB
        if using_external_db():
            self._save_history_external()
            return
        
        # Using local file storage
        session_dir = os.path.join(self.history_dir, self.session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save history
        with open(os.path.join(session_dir, "history.json"), "w") as f:
            json.dump(self.current_history, f, indent=2)
        
        # Update metadata
        metadata_file = os.path.join(session_dir, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                
                metadata["message_count"] = len(self.current_history)
                metadata["last_updated"] = datetime.datetime.now().isoformat()
                
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                print(f"Error updating metadata: {str(e)}")
    
    def _save_session_metadata_external(self, metadata: Dict[str, Any]) -> None:
        """
        Save session metadata to external database
        
        This is a placeholder for external DB integration. In a production
        environment, you would implement the specific database connector here.
        """
        # Get database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        # Get the table name with prefix to ensure it's separate from vector data
        sessions_table = db_config.get_history_table_name("sessions")
        
        print(f"Would save session metadata to external DB: {history_config['host']}")
        print(f"Target table: {sessions_table}")
        print(f"Session ID: {metadata['id']}")
        # In a real implementation, you would:
        # 1. Connect to your external database
        # 2. Insert/update the session metadata in the sessions table with the proper prefix
    
    def _save_history_external(self) -> None:
        """
        Save chat history to external database
        
        This is a placeholder for external DB integration. In a production
        environment, you would implement the specific database connector here.
        """
        # Get database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        # Get the table name with prefix to ensure it's separate from vector data
        messages_table = db_config.get_history_table_name("messages")
        
        print(f"Would save chat history to external DB: {history_config['host']}")
        print(f"Target table: {messages_table}")
        print(f"Session ID: {self.session_id}, Message count: {len(self.current_history)}")
        # In a real implementation, you would:
        # 1. Connect to your external database
        # 2. Insert/update the chat history records in the messages table with the proper prefix
    
    def _load_session_external(self, session_id: str) -> bool:
        """
        Load a session from external database
        
        This is a placeholder for external DB integration. In a production
        environment, you would implement the specific database connector here.
        """
        # Get database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        print(f"Would load session {session_id} from external DB: {history_config['host']}")
        # In a real implementation, you would:
        # 1. Connect to your external database
        # 2. Query for the session and its messages
        
        # For this demo, create some mock data
        self.session_id = session_id
        self.current_history = [
            {
                "id": "msg_0",
                "timestamp": datetime.datetime.now().isoformat(),
                "role": "system",
                "content": "This is a mock message from the external database",
                "context": {"source": "external_db"}
            }
        ]
        return True
    
    def _list_sessions_external(self) -> List[Dict[str, Any]]:
        """
        List sessions from external database
        
        This is a placeholder for external DB integration. In a production
        environment, you would implement the specific database connector here.
        """
        # Get database configuration from the unified config
        history_config = db_config.get_history_db_config()
        
        print(f"Would list sessions from external DB: {history_config['host']}")
        # In a real implementation, you would:
        # 1. Connect to your external database
        # 2. Query for available sessions
        
        # For this demo, return mock data
        return [
            {
                "id": "mock_session_1",
                "created_at": datetime.datetime.now().isoformat(),
                "message_count": 10,
                "source": "external_db"
            }
        ]