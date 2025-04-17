#!/usr/bin/env python3
"""
ai-tools - Ollama Prompt Entry Point
This script serves as the main entry point for the ai-tools application.
"""
import os
import sys
import argparse
import logging
from ai_tools.mcp.actions import (
    get_ollama_url,
    get_ollama_model,
    ask_llm_to_explain_error,
    run_ai_command,
    prompt_ollama_http,
    MCP_ACTIONS
)
from ai_tools.config.database import db_config
from ai_tools.modules.speech import SpeechToText
from ai_tools.modules.shell_tools import install_shell_integration_command

# Special handling for error analysis mode to completely suppress help output
if len(sys.argv) > 1 and sys.argv[1] == "error":
    # Direct error handling path that bypasses argparse completely
    if len(sys.argv) > 2:
        command = sys.argv[2]
        error = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "Command failed with no output"
        print(f"Analyzing error for command: '{command}'")
        output = ask_llm_to_explain_error(command, error)
        print(f"\nExplanation:\n{output}")
    else:
        print("Error: Missing command to analyze")
    sys.exit(0)

def print_environment_info():
    """Print current Ollama configuration from environment variables"""
    print("\nOllama Configuration:")
    print(f"  Host: {os.getenv('OLLAMA_HOST', 'localhost')}")
    print(f"  Port: {os.getenv('OLLAMA_PORT', '11434')}")
    print(f"  Model: {get_ollama_model()}")
    print(f"  API URL: {get_ollama_url()}\n")

def handle_run_command(args):
    """Handle the 'run' command"""
    prompt = " ".join(args.prompt)
    print(f"Generating command for: '{prompt}'")
    command, output = run_ai_command(prompt)
    print(f"\nCommand: {command}")
    print(f"Output: {output}")

def handle_prompt_command(args):
    """Handle the 'prompt' command"""
    # Set database configuration verbosity
    db_config.set_verbose(args.verbose)
    
    prompt = " ".join(args.prompt)
    print(f"Sending prompt to Ollama: '{prompt}'")
    output = prompt_ollama_http(prompt, use_streaming=True, verbose=args.verbose)
    # Don't print the response if using streaming mode because it's already printed directly
    if output:  # Only print if there's actual output (non-streaming mode)
        print(f"\nResponse:\n{output}")

def handle_error_command(args):
    """Handle the 'error' command"""
    if not args.error:
        print("Error: You must provide both a command and an error message.")
        return
    
    command = args.command
    error = " ".join(args.error)
    print(f"Analyzing error for command: '{command}'")
    output = ask_llm_to_explain_error(command, error)
    print(f"\nExplanation:\n{output}")

def handle_load_command(args):
    """Handle the 'load' command for loading documents into the knowledge base"""
    # Always use the consistent database name "knowledge"
    KNOWLEDGE_DB_NAME = "knowledge"
    
    directory_path = args.directory
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print(f"Error: '{directory_path}' is not a valid directory")
        return
    
    print(f"Loading documents from '{directory_path}' into knowledge base...")
    
    # Set database configuration verbosity
    db_config.set_verbose(args.verbose)
    
    # Access the MCP action for vectorizing documents
    vectorize_action = MCP_ACTIONS.get("vectorize_documents")
    if not vectorize_action:
        print("Error: Document loading functionality is not available")
        return
    
    result = vectorize_action(directory_path, db_name=KNOWLEDGE_DB_NAME)
    
    if result.get("status") == "success":
        print(f"Successfully loaded documents from '{directory_path}'")
        print(f"Storage type: {result.get('storage_type', 'local')}")
        print(f"Documents are now available to the AI as reference knowledge")
    else:
        print(f"Error: {result.get('message', 'Failed to load documents')}")

def handle_speak_command(args):
    """Handle the 'speak' command that sends a prompt to Ollama and speaks the response with a natural voice"""
    # Set database configuration verbosity
    db_config.set_verbose(args.verbose)
    
    # Initialize the speech engine with natural voice settings
    speech_engine = SpeechToText()
    
    prompt = " ".join(args.prompt)
    print(f"Sending prompt to Ollama: '{prompt}'")
    print("Please wait while getting response...")
    
    # Using non-streaming mode to get the full response at once for speech synthesis
    output = prompt_ollama_http(prompt, use_streaming=False, verbose=args.verbose)
    
    print(f"\nResponse:\n{output}")
    
    print("\nSpeaking response...")
    speech_engine.speech(output)
    print("Done speaking.")

def parse_args(argv=None):
    """Parse and return command line arguments"""
    # Create parser with add_help=False to suppress automatic help/usage messages
    parser = argparse.ArgumentParser(
        description="ai-tools Ollama interface for AI-powered flight assistance and command generation.",
        add_help=False  # Suppress automatic help message on error
    )
    
    # Add help option manually so it still shows up with -h/--help
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                      help='show this help message and exit')
    
    # Global arguments
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--mode', choices=['shell', 'api', 'web'], default='shell',
                      help='Runtime mode: shell, api, or web (not implemented)')
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Run command parser
    run_parser = subparsers.add_parser("run", help="Generate and run a command based on natural language")
    run_parser.add_argument("prompt", nargs="+", help="Natural language description of the command to generate")
    
    # Prompt command parser
    prompt_parser = subparsers.add_parser("prompt", help="Send a direct prompt to Ollama")
    prompt_parser.add_argument("prompt", nargs="+", help="Prompt to send to Ollama")
    prompt_parser.add_argument("-v", "--verbose", action="store_true", help="Show additional connection information")
    
    # Error command parser
    error_parser = subparsers.add_parser("error", help="Get an explanation for a command error")
    error_parser.add_argument("command", help="The command that generated the error")
    error_parser.add_argument("error", nargs="+", help="The error message to analyze")
    
    # Document loading parser
    load_parser = subparsers.add_parser("load", help="Load documents into the knowledge base")
    load_parser.add_argument("directory", help="Directory containing documents to load")
    load_parser.add_argument("-v", "--verbose", action="store_true", help="Show additional processing information")
    
    # Info command parser
    info_parser = subparsers.add_parser("info", help="Display configuration information")
    
    # Speak command parser
    speak_parser = subparsers.add_parser("speak", help="Send a prompt to Ollama and speak the response")
    speak_parser.add_argument("prompt", nargs="+", help="Prompt to send to Ollama")
    speak_parser.add_argument("-v", "--verbose", action="store_true", help="Show additional connection information")
    
    # Shell integration parser
    shell_parser = subparsers.add_parser("install-shell", help="Install shell integration for terminal capabilities")
    shell_parser.add_argument("--auto", action="store_true", help="Automatically add source command to shell config")
    
    # Parse arguments
    return parser.parse_args(argv)

def main(argv=None):
    """Main entry point for the application"""
    # Use the parse_args function to get command line arguments
    args = parse_args(argv)
    
    if args.verbose:
        # Configure logging with reasonable defaults
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        print("Starting AI Tools in verbose mode")
    else:
        # Setup minimal logging
        logging.basicConfig(level=logging.INFO)
    
    if args.config:
        print(f"Note: Config file '{args.config}' specified but config loading is not implemented")
    
    if not args.command:
        if args.mode != 'shell':
            print(f"Note: Mode '{args.mode}' is not implemented")
        # Create parser object for print_help()
        parser = argparse.ArgumentParser(
            description="ai-tools Ollama interface for AI-powered flight assistance and command generation.",
            add_help=False
        )
        parser.print_help()
        return
    
    if args.command == "run":
        handle_run_command(args)
    elif args.command == "prompt":
        handle_prompt_command(args)
    elif args.command == "error":
        handle_error_command(args)
    elif args.command == "load":
        handle_load_command(args)
    elif args.command == "info":
        print_environment_info()
    elif args.command == "speak":
        handle_speak_command(args)
    elif args.command == "install-shell":
        install_shell_integration_command()
    else:
        # Create parser object for print_help()
        parser = argparse.ArgumentParser(
            description="ai-tools Ollama interface for AI-powered flight assistance and command generation.",
            add_help=False
        )
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)