"""
Unified database configuration for both vector storage and chat history
"""
import os
from typing import Dict, Any, Optional


class DatabaseConfig:
    """
    Centralized database configuration class that provides consistent
    connection settings for all database-related functionality.
    """
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the database configuration from environment variables"""
        # Database connection settings (shared unless overridden)
        self.db_enabled = os.getenv('OLLAMA_DB_ENABLED', 'false').lower() == 'true'
        self.db_host = os.getenv('OLLAMA_DB_HOST', 'localhost')
        self.db_port = int(os.getenv('OLLAMA_DB_PORT', '5432'))
        self.db_user = os.getenv('OLLAMA_DB_USER', 'postgres')
        self.db_password = os.getenv('OLLAMA_DB_PASSWORD', '')
        self.db_name = os.getenv('OLLAMA_DB_NAME', 'ai_tools_db')
        
        # Vector database specific settings - use OLLAMA_DB variables if specific ones aren't set
        self.vector_db_enabled = os.getenv('VECTOR_DB_ENABLED', str(self.db_enabled)).lower() == 'true'
        self.vector_db_host = os.getenv('VECTOR_DB_HOST', self.db_host)
        self.vector_db_port = int(os.getenv('VECTOR_DB_PORT', str(self.db_port)))
        self.vector_db_user = os.getenv('VECTOR_DB_USER', self.db_user)
        self.vector_db_password = os.getenv('VECTOR_DB_PASSWORD', self.db_password)
        self.vector_db_name = os.getenv('VECTOR_DB_NAME', self.db_name)
        
        # Vector database table/collection prefixes
        self.vector_table_prefix = os.getenv('VECTOR_TABLE_PREFIX', 'vector_')
        
        # Local vector DB path
        self.vector_db_path = os.getenv(
            'VECTOR_DB_PATH', 
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/vector_db")
        )
        
        # Chat history settings - use OLLAMA_DB variables if specific ones aren't set
        self.history_db_enabled = os.getenv('HISTORY_DB_ENABLED', str(self.db_enabled)).lower() == 'true'
        self.history_db_host = os.getenv('HISTORY_DB_HOST', self.db_host)
        self.history_db_port = int(os.getenv('HISTORY_DB_PORT', str(self.db_port)))
        self.history_db_user = os.getenv('HISTORY_DB_USER', self.db_user)
        self.history_db_password = os.getenv('HISTORY_DB_PASSWORD', self.db_password)
        self.history_db_name = os.getenv('HISTORY_DB_NAME', self.db_name)
        
        # Chat history table/collection prefixes
        self.history_table_prefix = os.getenv('HISTORY_TABLE_PREFIX', 'chat_')
        
        # Local history DB path
        self.history_db_path = os.getenv(
            'HISTORY_DB_PATH', 
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/chat_history")
        )
        
        # LLM settings
        self.llm_host = os.getenv('OLLAMA_HOST', 'localhost')
        self.llm_port = int(os.getenv('OLLAMA_PORT', '11434'))
        self.llm_model = os.getenv('OLLAMA_MODEL', 'gemma3:27b')
        self.llm_api_key = os.getenv('LLM_API_KEY', '')
        
        # Default embedding model
        self.default_embedding_model = os.getenv(
            'DEFAULT_EMBEDDING_MODEL',
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Don't automatically print config on initialization
        # The log_config method can be called explicitly when needed
        self.verbose = os.getenv('VERBOSE_CONFIG', 'false').lower() == 'true'
        if self.verbose:
            self._log_config()
    
    def _log_config(self):
        """Log the current configuration"""
        print("===== Database Configuration =====")
        
        # Overall database settings
        print(f"Database configuration: {'Enabled' if self.db_enabled else 'Disabled (using local files)'}")
        if self.db_enabled:
            print(f"Default DB Connection: {self.db_host}:{self.db_port}/{self.db_name}")
        
        # Vector database specific settings
        print(f"Vector DB: {'Enabled' if self.vector_db_enabled else 'Disabled (using local files)'}")
        if self.vector_db_enabled:
            print(f"Vector DB Connection: {self.vector_db_host}:{self.vector_db_port}/{self.vector_db_name}")
            print(f"Vector table prefix: {self.vector_table_prefix}")
        else:
            print(f"Vector DB Path: {self.vector_db_path}")
            
        # Chat history specific settings
        print(f"History DB: {'Enabled' if self.history_db_enabled else 'Disabled (using local files)'}")
        if self.history_db_enabled:
            print(f"History DB Connection: {self.history_db_host}:{self.history_db_port}/{self.history_db_name}")
            print(f"History table prefix: {self.history_table_prefix}")
        else:
            print(f"History DB Path: {self.history_db_path}")
            
        # LLM settings
        print(f"LLM: {self.llm_host}:{self.llm_port} (Model: {self.llm_model})")
        print(f"Embedding Model: {self.default_embedding_model}")
        print("=================================")
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get vector database configuration as a dictionary"""
        return {
            "enabled": self.vector_db_enabled,
            "host": self.vector_db_host,
            "port": self.vector_db_port,
            "user": self.vector_db_user,
            "password": self.vector_db_password,
            "dbname": self.vector_db_name,
            "table_prefix": self.vector_table_prefix,
            "local_path": self.vector_db_path
        }
    
    def get_history_db_config(self) -> Dict[str, Any]:
        """Get history database configuration as a dictionary"""
        return {
            "enabled": self.history_db_enabled,
            "host": self.history_db_host,
            "port": self.history_db_port,
            "user": self.history_db_user,
            "password": self.history_db_password,
            "dbname": self.history_db_name,
            "table_prefix": self.history_table_prefix,
            "local_path": self.history_db_path
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration as a dictionary"""
        return {
            "host": self.llm_host,
            "port": self.llm_port,
            "model": self.llm_model,
            "api_key": self.llm_api_key
        }
    
    def get_vector_table_name(self, db_name: str = "default") -> str:
        """
        Get the table/collection name for a vector database
        
        Args:
            db_name: The base name of the database
            
        Returns:
            The full table/collection name with prefix
        """
        return f"{self.vector_table_prefix}{db_name}"
    
    def get_history_table_name(self, session_id: str = "default") -> str:
        """
        Get the table/collection name for chat history
        
        Args:
            session_id: The session ID
            
        Returns:
            The full table/collection name with prefix
        """
        return f"{self.history_table_prefix}{session_id}"
    
    def get_connection_string(self, db_type: str = "vector") -> str:
        """
        Get database connection string
        
        Args:
            db_type: Type of database ("vector" or "history")
            
        Returns:
            Connection string for the database
        """
        if db_type == "vector":
            if not self.vector_db_enabled:
                return f"local://{self.vector_db_path}"
            
            password_part = f":{self.vector_db_password}" if self.vector_db_password else ""
            return f"postgresql://{self.vector_db_user}{password_part}@{self.vector_db_host}:{self.vector_db_port}/{self.vector_db_name}"
        
        elif db_type == "history":
            if not self.history_db_enabled:
                return f"local://{self.history_db_path}"
            
            password_part = f":{self.history_db_password}" if self.history_db_password else ""
            return f"postgresql://{self.history_db_user}{password_part}@{self.history_db_host}:{self.history_db_port}/{self.history_db_name}"
        
        else:
            raise ValueError(f"Unknown database type: {db_type}")
    
    def set_verbose(self, verbose: bool = True):
        """
        Set the verbose flag and optionally log configuration
        
        Args:
            verbose: Whether to enable verbose logging (default: True)
        """
        self.verbose = verbose
        if verbose:
            self._log_config()


# Singleton instance for easy access
db_config = DatabaseConfig()