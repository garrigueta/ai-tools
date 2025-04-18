import os
import logging
from openai import OpenAI
from ai_tools.mcp.db_connector import get_vector_db

logger = logging.getLogger(__name__)

class AiWrapper:
    """Wrapper for AI model interactions with support for multiple models and knowledge retrieval"""
    def __init__(self):
        self.client = None
        self.system_base_data = ""
        self.system_content = ""
        self.user_content = ""
        self.ai_response = ""
        self.model = os.getenv("AI_MODEL", "gpt-4o")  # Default to GPT-4o if not specified
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma3:27b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        self.ollama_port = os.getenv("OLLAMA_PORT", "11434")
        self.temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        self.use_rag = os.getenv("USE_RAG", "true").lower() == "true"
        
    def set_system_content(self, system_content):
        """Set the system content for the next AI request"""
        self.system_content = system_content

    def set_user_content(self, user_content):
        """Set the user content for the next AI request"""
        self.user_content = user_content

    def set_system_base_data(self, system_base_data):
        """Set the base system prompt that will be used for all requests"""
        self.system_base_data = system_base_data

    def initi_ai(self):
        """Initialize the AI client based on configuration"""
        if self.use_ollama:
            # For Ollama, we don't need to create a client here
            # We'll use the appropriate method in ai_request
            logger.info(f"Using Ollama with model {self.ollama_model}")
            pass
        else:
            # Initialize OpenAI client
            self.client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                organization=os.getenv("OPENAI_ORG", None),
            )
            logger.info(f"Initialized OpenAI client with model {self.model}")

    def _get_relevant_context(self, query):
        """Retrieve relevant context from vector database if available"""
        if not self.use_rag:
            return ""
            
        try:
            vector_db = get_vector_db()
            if vector_db and vector_db.initialized:
                results = vector_db.search(query, limit=3)
                if results:
                    context = "\nRelevant information from knowledge base:\n"
                    for i, result in enumerate(results):
                        context += f"[{i+1}] {result.content}\n"
                    return context
        except Exception as e:
            logger.warning(f"Failed to retrieve context from vector DB: {e}")
            
        return ""

    def ai_request(self):
        """Send the request to the appropriate AI model and return the response"""
        messages = [
            {"role": "system", "content": self.system_base_data + self.system_content},
            {"role": "user", "content": self.user_content}
        ]
        
        try:
            if self.use_ollama:
                return self._ollama_request(messages)
            else:
                return self._openai_request(messages)
        except Exception as e:
            logger.error(f"Error in AI request: {e}")
            self.ai_response = f"Error communicating with AI service: {str(e)}"
    
    def _openai_request(self, messages):
        """Make a request to the OpenAI API"""
        if not self.client:
            self.initi_ai()
            
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        self.ai_response = str(response.choices[0].message.content)
        return self.ai_response
        
    def _ollama_request(self, messages):
        """Make a request to the Ollama API"""
        import requests
        import json
        
        ollama_url = f"http://{self.ollama_host}:{self.ollama_port}/api/chat"
        
        try:
            response = requests.post(
                ollama_url,
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            self.ai_response = response.json()["message"]["content"]
            return self.ai_response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama: {e}")
            raise Exception(f"Failed to communicate with Ollama: {e}")

    def get_ai_response(self, message, system_content=None):
        """Get a response from the AI for the given message and optional system content"""
        if system_content is not None:
            self.set_system_content(system_content)
            
        # Retrieve relevant knowledge if RAG is enabled
        context = self._get_relevant_context(message)
        if context:
            message = f"{message}\n{context}"
            
        self.set_user_content(message)
        self.ai_request()
        return self.ai_response
