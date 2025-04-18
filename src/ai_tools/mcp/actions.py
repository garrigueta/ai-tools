""" Run a command in the terminal using a local LLM """
import os
import subprocess
import requests
import json
from typing import Dict, Any, Optional

def get_ollama_url():
    """Construct the Ollama API URL from environment variables"""
    host = os.getenv('OLLAMA_HOST', 'localhost')
    port = os.getenv('OLLAMA_PORT', '11434')
    return f"http://{host}:{port}/api/generate"

def get_ollama_model():
    """Get the Ollama model from environment variables"""
    return os.getenv('OLLAMA_MODEL', 'gemma3:27b')

def ask_llm_to_explain_error(command, error):
    """ Ask the local LLM to explain an error """
    system_instruction = "Provide a very brief explanation of the following error message. " \
                         "Limit your response to 3-5 short lines total. " \
                         "Include only the most likely cause and one simple solution. " \
                         "Format your response as console output. " \
                         "Be extremely concise. No extra details or explanations. " \
                         "No markdown formatting."
    full_prompt = f"{system_instruction}\n\nCommand: {command}\n\nError: {error}\nExplanation:"
    try:
        response = requests.post(
            get_ollama_url(),
            json={
                'model': get_ollama_model(),
                'prompt': full_prompt,
                'stream': False
            },
            timeout=30,
        )
        response.raise_for_status()
        response_json = response.json()
        if 'response' not in response_json:
            raise KeyError(f"'response' key not found in API response: {response_json}")
        
        # Clean up any Markdown formatting that might remain
        response_text = response_json['response'].strip()
        response_text = response_text.replace("```", "")
        response_text = response_text.replace("`", "")
        
        return response_text
    except requests.exceptions.ReadTimeout:
        return "Error: The request to the Ollama server timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the Ollama server. {str(e)}"


def ask_llm_for_command(prompt):
    """ Ask the local LLM to generate a safe terminal command """
    system_instruction = "Translate the following user request " \
                         "into a safe Linux terminal command. Only return " \
                         "a command that can be executed directly in the terminal. " \
                         "Do not include shell function syntax like 'return' statements. " \
                         "Do not include any explanations or extra text."
    full_prompt = f"{system_instruction}\n\nUser: {prompt}\nCommand:"

    try:
        response = requests.post(
            get_ollama_url(),
            json={
                'model': get_ollama_model(),
                'prompt': full_prompt,
                'stream': False
            },
            timeout=15,  # Increased timeout
        )
        response.raise_for_status()
        response_json = response.json()
        if 'response' not in response_json:
            raise KeyError(f"'response' key not found in API response: {response_json}")
        return response_json['response'].strip()
    except requests.exceptions.ReadTimeout:
        return "Error: The request to the Ollama server timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the Ollama server. {str(e)}"


def run_command(command):
    """ Run the terminal command safely """
    try:
        # Skip execution for shell function syntax if detected
        if command.strip().startswith("return "):
            return "Error: The command contains shell function syntax that cannot be executed directly."
            
        # Print command for debugging
        print(f"Executing command: {command}")
        result = subprocess.check_output(['/bin/bash', '-c', command],
                                         stderr=subprocess.STDOUT,
                                         text=True, timeout=5)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Command error:\n{e.output.strip()}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def run_ai_command(natural_prompt: str) -> tuple[str, str]:
    """ List the files in the current directory """
    np_command = ask_llm_for_command(natural_prompt)
    print(f"🛠️  LLM Command: {np_command}")

    np_output = run_command(np_command)
    print("📂 Command Output:\n", np_output)
    return np_command, np_output


def prompt_ollama_http(prompt: str, use_streaming: bool = True, verbose: bool = False) -> str:
    """ Send a prompt to the local Ollama server and get the response 
    
    Args:
        prompt: The prompt to send to Ollama
        use_streaming: Whether to use streaming mode (default: True)
        verbose: Whether to print debug information (default: False)
        
    Returns:
        The response string from the Ollama server
    """
    try:
        # Log the request details for debugging
        ollama_url = get_ollama_url()
        ollama_model = get_ollama_model()
        
        if verbose:
            print(f"Connecting to Ollama at: {ollama_url}")
            print(f"Using model: {ollama_model}")
            print(f"Request timeout: 60 seconds")
            print(f"Streaming mode: {'enabled' if use_streaming else 'disabled'}")
        
        # If streaming is enabled, use a different approach that's less likely to timeout
        if use_streaming:
            # Use streaming API
            full_response = ""
            
            # First, check if Ollama is accessible
            try:
                check_url = ollama_url.replace('/api/generate', '/api/tags')
                requests.get(check_url, timeout=5)
            except requests.exceptions.RequestException:
                return "Error: Could not connect to Ollama server. Make sure Ollama is running and accessible."
            
            if verbose:
                print("Connection to Ollama successful. Starting stream...\n")
                print("Response:")
            
            response = requests.post(
                ollama_url,
                json={
                    'model': ollama_model,
                    'prompt': prompt,
                    'stream': True
                },
                timeout=10,  # Just for initial connection
                stream=True
            )
            
            response.raise_for_status()
            
            # Process the streaming response and print it in real-time
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = line.decode('utf-8')
                        # Skip empty chunks
                        if not chunk.strip() or chunk == "data: [DONE]":
                            continue
                        
                        # Remove the "data: " prefix if present
                        if chunk.startswith('data: '):
                            chunk = chunk[6:]
                            
                        # Parse the JSON chunk
                        try:
                            chunk_data = json.loads(chunk)
                            if 'response' in chunk_data:
                                chunk_text = chunk_data['response']
                                # Print the chunk text directly as it arrives
                                print(chunk_text, end="", flush=True)
                                full_response += chunk_text
                        except json.JSONDecodeError:
                            # Skip malformed chunks
                            continue
                    except Exception as e:
                        print(f"\nError processing chunk: {str(e)}")
            
            if verbose:
                print("\n\nResponse complete.")
            else:
                print("\n")  # Just add a newline for better formatting
                
            return "" # Return empty since we already printed the response
        else:
            # Non-streaming approach (original method)
            response = requests.post(
                ollama_url,
                json={
                    'model': ollama_model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=60,  # 60 second timeout
            )
            response.raise_for_status()
            response_json = response.json()
            if 'response' not in response_json:
                raise KeyError(f"'response' key not found in API response: {response_json}")
            return response_json['response'].strip()
    except requests.exceptions.ReadTimeout:
        return "Error: The request to the Ollama server timed out. Try a simpler query or check your Ollama server configuration.\n\nTroubleshooting tips:\n1. Check if Ollama is running (curl {})\n2. Try a smaller model\n3. Check server resources\n4. Consider using the 'error' command which uses a different prompt format".format(get_ollama_url().replace('/api/generate', '/api/tags'))
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to connect to the Ollama server. {str(e)}"


# Import database connector functions
db_functions_available = False
try:
    from ai_tools.mcp.db_connector import (
        mcp_vectorize_documents,
        mcp_query_documents,
        mcp_list_vector_databases,
        mcp_start_chat_session,
        mcp_add_chat_message,
        mcp_get_chat_history,
        mcp_load_chat_session,
        mcp_list_chat_sessions,
        mcp_query_context_for_prompt,
        mcp_get_recent_conversations,
        mcp_get_document_metadata
    )
    db_functions_available = True
except ImportError as e:
    print(f"Warning: Could not import database connector functions: {str(e)}")
    # Define placeholder functions to avoid NameError
    def db_function_unavailable(*args, **kwargs):
        return {
            "status": "error", 
            "message": "Database functions are unavailable. Please ensure langchain and other required packages are installed."
        }
    
    # Create placeholder functions for all expected DB connector functions
    mcp_vectorize_documents = db_function_unavailable
    mcp_query_documents = db_function_unavailable
    mcp_list_vector_databases = db_function_unavailable
    mcp_start_chat_session = db_function_unavailable
    mcp_add_chat_message = db_function_unavailable
    mcp_get_chat_history = db_function_unavailable
    mcp_load_chat_session = db_function_unavailable
    mcp_list_chat_sessions = db_function_unavailable
    mcp_query_context_for_prompt = db_function_unavailable
    mcp_get_recent_conversations = db_function_unavailable
    mcp_get_document_metadata = db_function_unavailable


# MCP action registry
MCP_ACTIONS = {
    # Terminal and command actions
    "run_command": run_command,
    "ask_llm_for_command": ask_llm_for_command,
    "run_ai_command": run_ai_command,
    "ask_llm_to_explain_error": ask_llm_to_explain_error,
    "prompt_ollama": prompt_ollama_http,
    
    # Database connector actions - Vector database operations
    "vectorize_documents": mcp_vectorize_documents,
    "query_documents": mcp_query_documents,
    "list_vector_databases": mcp_list_vector_databases,
    
    # Database connector actions - Chat history operations
    "start_chat_session": mcp_start_chat_session,
    "add_chat_message": mcp_add_chat_message,
    "get_chat_history": mcp_get_chat_history,
    "load_chat_session": mcp_load_chat_session,
    "list_chat_sessions": mcp_list_chat_sessions,
    
    # AI-specific context and information retrieval functions
    "query_context_for_prompt": mcp_query_context_for_prompt,
    "get_recent_conversations": mcp_get_recent_conversations,
    "get_document_metadata": mcp_get_document_metadata,
}


def handle_mcp_action(action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle an MCP action request
    
    Args:
        action_name: Name of the action to perform
        params: Parameters for the action
        
    Returns:
        Action result
    """
    if action_name not in MCP_ACTIONS:
        return {
            "status": "error",
            "message": f"Unknown action: {action_name}",
            "available_actions": list(MCP_ACTIONS.keys())
        }
    
    try:
        action_function = MCP_ACTIONS[action_name]
        result = action_function(**params)
        
        # If the result is not a dictionary, wrap it
        if not isinstance(result, dict):
            result = {
                "status": "success",
                "result": result
            }
        
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error executing action {action_name}: {str(e)}"
        }
