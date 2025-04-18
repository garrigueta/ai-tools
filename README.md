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

This will:
1. Install the shell integration script to your home directory as `~/.bash_aitools`
2. Automatically add the required source line to your shell configuration file (`~/.bashrc` or `~/.zshrc`)
3. Inform you when the integration is complete

You'll need to restart your terminal or run `source ~/.bashrc` (or equivalent) to activate the integration.

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

### Game Simulation Assistant

Start an interactive voice assistant for game simulators:

```bash
# Start the Microsoft Flight Simulator assistant
aitools sim msfs start

# Start a test simulation with dummy data (default)
aitools sim dummy start
# or simply
aitools sim start

# Stop a running simulator assistant
aitools sim msfs stop
```

The game simulation assistant:
- Connects to game data (from MSFS, or dummy data for testing)
- Listens for voice commands through your microphone
- Processes your requests with AI using the real-time game data
- Responds with spoken answers about the game state

#### Advanced Simulation Features

The game assistant includes several advanced features:

- **Real-time Data Monitoring**: Continuously collects game data every second, even when you're not speaking
- **Automatic Warning Alerts**: Proactively announces critical warnings through voice alerts (e.g., stall warnings, low fuel)
- **Historical Data Analysis**: Tracks trends and changes in important metrics (altitude, airspeed)
- **Knowledge Integration**: Stores game data in vector database for AI context enhancement
- **Game-specific Expertise**: Each game module provides specialized knowledge and terminology to the AI
- **Prioritized Warnings**: Critical warnings have shorter cooldowns and higher priorities

For Microsoft Flight Simulator, specific warnings include:
- Stall warnings (dangerous low airspeed)
- Overspeed warnings (excessive airspeed)
- Engine and fuel alerts
- System failures (electrical, hydraulic, avionics)

To exit the simulation assistant, simply say "exit" or press Ctrl+C.

Currently supported games:
- Microsoft Flight Simulator (msfs)
- Dummy simulator for testing (dummy)

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

The application uses environment variables for configuration. Here's a comprehensive list of all available environment variables:

### LLM Configuration
- `OLLAMA_HOST`: The hostname where Ollama is running (default: `localhost`)
- `OLLAMA_PORT`: The port Ollama is using (default: `11434`)
- `OLLAMA_MODEL`: The Ollama model to use (default: `gemma3:27b`)
- `LLM_API_KEY`: API key for authentication with external LLM services (default: empty)

### Database Configuration
- `OLLAMA_DB_ENABLED`: Enable external database storage (default: `false`)
- `OLLAMA_DB_HOST`: Database host (default: `localhost`)
- `OLLAMA_DB_PORT`: Database port (default: `5432`)
- `OLLAMA_DB_USER`: Database username (default: `postgres`)
- `OLLAMA_DB_PASSWORD`: Database password (default: empty)
- `OLLAMA_DB_NAME`: Database name (default: `ai_tools_db`)

### Vector Database Configuration
- `VECTOR_DB_ENABLED`: Enable vector database (default: same as `OLLAMA_DB_ENABLED`)
- `VECTOR_DB_HOST`: Vector database host (default: same as `OLLAMA_DB_HOST`)
- `VECTOR_DB_PORT`: Vector database port (default: same as `OLLAMA_DB_PORT`)
- `VECTOR_DB_USER`: Vector database username (default: same as `OLLAMA_DB_USER`)
- `VECTOR_DB_PASSWORD`: Vector database password (default: same as `OLLAMA_DB_PASSWORD`)
- `VECTOR_DB_NAME`: Vector database name (default: same as `OLLAMA_DB_NAME`)
- `VECTOR_TABLE_PREFIX`: Prefix for vector database tables (default: `vector_`)
- `VECTOR_DB_PATH`: Local path for vector database if using local storage (default: `data/vector_db` in project directory)

### History Database Configuration
- `HISTORY_DB_ENABLED`: Enable history database (default: same as `OLLAMA_DB_ENABLED`)
- `HISTORY_DB_HOST`: History database host (default: same as `OLLAMA_DB_HOST`)
- `HISTORY_DB_PORT`: History database port (default: same as `OLLAMA_DB_PORT`)
- `HISTORY_DB_USER`: History database username (default: same as `OLLAMA_DB_USER`)
- `HISTORY_DB_PASSWORD`: History database password (default: same as `OLLAMA_DB_PASSWORD`)
- `HISTORY_DB_NAME`: History database name (default: same as `OLLAMA_DB_NAME`)
- `HISTORY_TABLE_PREFIX`: Prefix for history database tables (default: `chat_`)
- `HISTORY_DB_PATH`: Local path for history database if using local storage (default: `data/chat_history` in project directory)

### Embedding Model Configuration
- `DEFAULT_EMBEDDING_MODEL`: Model used for vector embeddings (default: `sentence-transformers/all-MiniLM-L6-v2`)

### Debugging and Logging
- `VERBOSE_CONFIG`: Print detailed configuration on startup (default: `false`)

You can set these variables in your shell or create a `.env` file in your project directory.

## License

[Your License Information]
