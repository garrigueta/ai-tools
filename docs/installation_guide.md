# Installation Guide for AI-Tools

This guide explains how to install the `ai-tools` package and set up all required components.

## Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager
- [Ollama](https://ollama.com/) installed and running locally
- PostgreSQL (optional, for advanced features)
- Audio playback utilities (for speech functionality)

## Installation Methods

### Method 1: Install from source using Poetry (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/garrigueta/ai-tools.git
   cd ai-tools
   ```

2. Install with Poetry:
   ```bash
   poetry install
   ```

3. Activate the Poetry virtual environment:
   ```bash
   poetry shell
   ```

4. Run the command-line tool:
   ```bash
   aitools prompt "Hello, how can you help me today?"
   ```

### Method 2: Install as a development package

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
   aitools prompt "Hello, how can you help me today?"
   ```

### Method 3: Binary Installation

For using the pre-built binary packages without needing to install Python or other dependencies, see the [Binary Installation Guide](binary_installation.md).

## Ollama Setup

The AI-Tools package requires a running Ollama server with a compatible model:

1. Install Ollama:
   ```bash
   # On Linux
   curl -fsSL https://ollama.com/install.sh | sh

   # On macOS
   brew install ollama
   
   # On Windows
   # Download and install from https://ollama.com/download/windows
   ```

2. Pull a recommended model:
   ```bash
   # The recommended model - good balance of speed and capabilities
   ollama pull gemma3:27b

   # Alternative smaller model for less powerful systems
   ollama pull phi3:mini
   
   # Alternative model with very powerful reasoning
   ollama pull llama3:70b
   ```

3. Start the Ollama server:
   ```bash
   ollama serve
   ```

## Audio Support

For the `speak` command which uses Google Text-to-Speech, you'll need at least one of these audio players installed:

### On Linux:
```bash
# FFplay (recommended)
sudo apt-get install ffmpeg

# Or mpg123
sudo apt-get install mpg123

# Or mpg321
sudo apt-get install mpg321

# Or mplayer
sudo apt-get install mplayer
```

### On macOS:
```bash
# Using Homebrew
brew install ffmpeg
# or
brew install mpg123
```

### On Windows:
For Windows users, it's recommended to use Windows Subsystem for Linux (WSL) and follow the Linux installation steps, or use the binary package with PowerShell integration.

## PostgreSQL Database Setup (Optional)

For advanced features like document vector storage and chat history, you'll need PostgreSQL:

1. Install PostgreSQL:
   ```bash
   # On Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib

   # On macOS
   brew install postgresql
   
   # On Windows
   # Download and install from https://www.postgresql.org/download/windows/
   ```

2. Create a database for AI-Tools:
   ```bash
   # Start PostgreSQL service if not already running
   sudo service postgresql start   # Linux
   brew services start postgresql  # macOS
   # On Windows, PostgreSQL should run as a service after installation

   # Create the database
   sudo -u postgres psql -c "CREATE DATABASE ai_tools_db;"
   sudo -u postgres psql -c "CREATE USER aitools WITH PASSWORD 'your_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_tools_db TO aitools;"
   ```

3. Configure AI-Tools to use your database by setting environment variables:
   ```bash
   # Linux/macOS
   export OLLAMA_DB_ENABLED=true
   export OLLAMA_DB_HOST=localhost
   export OLLAMA_DB_PORT=5432
   export OLLAMA_DB_USER=aitools
   export OLLAMA_DB_PASSWORD=your_password
   export OLLAMA_DB_NAME=ai_tools_db
   
   # Windows (PowerShell)
   $env:OLLAMA_DB_ENABLED="true"
   $env:OLLAMA_DB_HOST="localhost"
   $env:OLLAMA_DB_PORT="5432"
   $env:OLLAMA_DB_USER="aitools"
   $env:OLLAMA_DB_PASSWORD="your_password"
   $env:OLLAMA_DB_NAME="ai_tools_db"
   ```

## Microsoft Flight Simulator Integration (Optional)

To use the MSFS integration features:

1. Ensure Microsoft Flight Simulator is installed
2. Install SimConnect SDK (should be included with MSFS)
3. Set up Python-SimConnect:
   ```bash
   poetry add python-simconnect
   # or with pip
   pip install python-simconnect
   ```

4. Configure simulation settings:
   ```bash
   # Set MSFS as the default simulation
   export SIMULATION_TYPE=msfs
   # Set the SimConnect server address if not on the same machine
   export SIMCONNECT_HOST=localhost
   ```

## Environment Configuration

Set these environment variables to customize your AI-Tools experience:

```bash
# Basic configuration
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MODEL=gemma3:27b

# For database features (if using PostgreSQL)
export OLLAMA_DB_ENABLED=true
export OLLAMA_DB_HOST=localhost
export OLLAMA_DB_PORT=5432
export OLLAMA_DB_USER=postgres
export OLLAMA_DB_PASSWORD=your_password
export OLLAMA_DB_NAME=ai_tools_db

# For simulation features
export SIMULATION_TYPE=msfs  # or 'dummy' for testing
```

For a complete list of all configuration options, see the [Advanced Configuration](user_guide.md#advanced-configuration) section in the User Guide.

## Shell Integration

To enable command-line error handling integration, use the built-in installation command:

```bash
aitools install-shell
```

This will:
1. Install the shell integration script to your home directory as `~/.bash_aitools`
2. Automatically add the required source line to your shell configuration file (`~/.bashrc` or `~/.zshrc`)
3. Inform you when the integration is complete

You'll need to restart your terminal or run `source ~/.bashrc` (or equivalent) to activate the integration.

On Windows, when using the binary package, follow the [Windows installation instructions](binary_installation.md#windows-installation) for PowerShell integration.

## Troubleshooting

### General Issues

If you encounter import errors:
1. Make sure you're using the virtual environment created by Poetry
2. Try reinstalling the package with `poetry install --no-dev`
3. Check Python version with `python --version` (requires 3.10+)

### Ollama Connection Issues

If AI-Tools can't connect to Ollama:
1. Verify that Ollama is running with `curl http://localhost:11434/`
2. Check if your model is properly downloaded with `ollama list`
3. Try pulling the model again with `ollama pull gemma3:27b`
4. If connecting to a remote Ollama instance, check network settings

### Database Connection Issues

If database features aren't working:
1. Verify PostgreSQL is running with `pg_isready`
2. Check connection parameters in environment variables
3. Try connecting manually with `psql -U [username] -d ai_tools_db -h localhost`
4. Ensure the database and user exist with proper permissions

### Microsoft Flight Simulator Issues

If MSFS integration isn't working:
1. Make sure MSFS is running before starting the simulation assistant
2. Check that SimConnect is properly installed (should be in your MSFS SDK folder)
3. Verify the python-simconnect package is installed
4. Try using the dummy simulation first to test basic functionality: `aitools sim dummy start`

### Speech Recognition Issues

If voice commands aren't being recognized:
1. Check that your microphone is properly connected and set as default
2. Try speaking more slowly and clearly
3. Ensure you have a good internet connection for Google's speech services
4. Test your microphone with another application

### Advanced Debugging

For advanced troubleshooting:
1. Enable verbose logging:
   ```bash
   export VERBOSE_CONFIG=true
   ```
2. Check logs for specific components:
   ```bash
   # Run with debug output
   PYTHONPATH=/path/to/ai-tools python -m ai_tools.modules.sim --debug
   ```

## Updating AI-Tools

To update to the latest version:

```bash
cd /path/to/ai-tools
git pull
poetry install  # If using Poetry
# or
pip install -e .  # If using pip
```

If you're using the binary package, download the latest binary release or rebuild it following the [binary building instructions](binary_installation.md#building-the-binary).