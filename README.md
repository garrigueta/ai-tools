# ai-tools

AI Tools with Ollama LLM integration for OS assistance.

## Overview

ai-tools is an assistant that uses Ollama's local large language models to provide real-time assistance, command generation, and error explanations directly from your terminal. It also includes optional integration with Microsoft Flight Simulator.

## Installation

### Option 1: Install using Poetry (recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/garrigueta/ai-tools.git
   cd ai-tools
   ```

2. Install with Poetry:
   ```bash
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install the package
   poetry install
   
   # Activate the Poetry environment
   poetry shell
   ```

3. Run the command-line tool:
   ```bash
   aitools prompt "Hello, how can you help me today?"
   ```

See [INSTALL.md](INSTALL.md) for more detailed installation options and troubleshooting.

### Option 2: Install as a development package

1. Clone the repository:
   ```bash
   git clone https://github.com/garrigueta/ai-tools.git
   cd ai-tools
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

3. Run the command-line tool:
   ```bash
   aitools prompt "Hello there"
   ```

## Requirements

- Python 3.10+
- Ollama installed locally with a model configured
- Audio playback support for the `speak` command (Linux: ffplay, mpg123, mpg321, or mplayer)

## Environment Setup

Set these environment variables to customize your experience:
```bash
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MODEL=gemma3:27b
```

## Command-Line Integration

ai-tools includes a bash integration that automatically analyzes command errors. When sourced, the bash integration file sets up error handling that will:

1. Capture failed commands
2. Send them to Ollama for analysis
3. Display helpful explanations

### Enable Shell Integration

After installing the package, run the shell integration command:

```bash
aitools install-shell
```

This will install the shell integration script to your home directory and provide instructions on how to enable it in your shell config file.

You can then add the source line to your `.bashrc` or `.zshrc` file:

```bash
# Add to your ~/.bashrc or ~/.zshrc
source ~/.bash_aitools
```

## Usage

The ai-tools package provides several commands:

### Run a Natural Language Command

Generates and executes a command based on natural language input:

```bash
aitools run "list all text files in the current directory"
```

### Send a Direct Prompt to Ollama

Send a direct prompt to the Ollama model and get a response:

```bash
aitools prompt "Explain how regex works in Python"
```

### Speak Response with Text-to-Speech

Send a prompt to Ollama and have the response read aloud using Google's Text-to-Speech:

```bash
aitools speak "Tell me about the benefits of containerization"
```

### Get Error Explanation

Analyze and explain an error message from a command:

```bash
aitools error "npm install" "Error: ENOENT: no such file or directory, open 'package.json'"
```

### Load Documents into Knowledge Base

Load and vectorize documents from a directory to enhance AI knowledge:

```bash
aitools load "/path/to/documents"
```

### Install Shell Integration

Install the shell integration script for terminal capabilities:

```bash
aitools install-shell
```

### View Configuration

Display the current Ollama configuration:

```bash
aitools info
```

### Help

Get help on available commands:

```bash
aitools --help
```

## Shell Integration Features

The shell integration provides several useful features:

1. **Automatic Error Analysis**: When a command fails, the error is automatically analyzed by the AI
2. **Ollama Connection Checking**: Functions to check if Ollama is running and properly configured
3. **Model Availability**: Check if your configured model is available
4. **Alias Support**: Use the `mop` alias as a shorthand for `aitools`
5. **Testing Functions**: Easily test your Ollama setup with the `test_ollama` function

Available shell functions:
- `check_ollama` - Check if Ollama is running
- `check_model` - Check if the configured model is available
- `check_models` - List all available Ollama models
- `test_ollama` - Test Ollama with a simple prompt
- `init_ollama_tools` - Initialize and check Ollama setup

## Speech Capabilities

The speak command uses Google's Text-to-Speech (gTTS) to provide high-quality, natural-sounding voice output. Key features include:

- Natural-sounding human voice using Google's TTS engine
- Automatic text preprocessing to improve speech quality:
  - Removal of emojis and special characters
  - Proper handling of abbreviations and acronyms
  - Sentence splitting for natural pacing
- Speed optimization for more natural delivery
- Multiple audio player support (ffplay, mpg123, mpg321, mplayer)

Note: The speak command requires internet connectivity to access Google's TTS service.

## Project Structure

The project is organized as a Python package:

```
src/                 # Source code directory
  ai_tools/          # Main package
    __init__.py      # Package initialization
    __main__.py      # Entry point for running as a module
    main.py          # Main application logic
    backend/         # Backend services
    chat/            # Chat interface implementations
    config/          # Configuration management
    mcp/             # Model Context Protocol components
      actions.py     # Command execution and LLM interaction
    modules/         # Utility modules
      audio.py       # Audio processing functions
      msfs.py        # Microsoft Flight Simulator integration
      sim.py         # Simulation support functions
      speech.py      # Text-to-speech functionality
    storage/         # Knowledge storage and document loading
      docs.py        # Document vectorization and retrieval
```

## Advanced Configuration

The application uses environment variables for configuration:

- `OLLAMA_HOST`: The hostname where Ollama is running (default: `localhost`)
- `OLLAMA_PORT`: The port Ollama is using (default: `11434`)
- `OLLAMA_MODEL`: The Ollama model to use (default: `gemma3:27b`)

You can set these variables in your shell or modify them in the `.bash_ollama_actions` file.

## License

[Your License Information]
