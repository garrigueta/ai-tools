[![CI](https://github.com/garrigueta/ai-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/garrigueta/ai-tools/actions/workflows/ci.yml)

# AI-Tools

AI Tools with Ollama LLM integration for OS assistance. This project is in active development and not finished.

## Overview

ai-tools is an assistant that uses Ollama's local large language models to provide real-time assistance, command generation, and error explanations directly from your terminal. It also includes optional integration with Microsoft Flight Simulator.

## Key Features

- ✨ **Natural Language Commands**: Generate and execute shell commands using natural language
- 🤖 **AI-Powered Error Analysis**: Automatic explanations for command errors
- 🔊 **Text-to-Speech**: Have AI responses read aloud with natural voice
- ✈️ **Game Simulation Integration**: Voice assistant for Microsoft Flight Simulator
- 📚 **Knowledge Base**: Load documents to enhance AI's context awareness
- 🐚 **Shell Integration**: Seamless terminal integration for Bash and PowerShell

## Quick Start

```bash
# Clone the repository
git clone https://github.com/garrigueta/ai-tools.git
cd ai-tools

# Install with Poetry (recommended)
poetry install
poetry shell

# Run the command-line tool
aitools prompt "Hello, how can you help me today?"
```

## Requirements

- Python 3.10+
- Ollama installed locally with a model configured
- Audio playback support for the `speak` command

## Documentation

Comprehensive documentation is available in the `docs` folder:

- [Installation Guide](docs/installation_guide.md) - Detailed installation instructions
- [User Guide](docs/user_guide.md) - How to use AI-Tools
- [Binary Installation](docs/binary_installation.md) - Using pre-built binaries (no Python required)
- [Shell Integration Guide](docs/shell_integration_guide.md) - Using the terminal error handler and shell features
- [Game Module Development](docs/game_module_development.md) - Guide for developing game integration modules
- [Development Guide](docs/development_guide.md) - Guide for contributors

## Basic Usage Examples

```bash
# Generate and execute a command
aitools run "list all text files in the current directory"

# Get an explanation from the AI
aitools prompt "Explain how regex works in Python"

# Spoken response
aitools speak "Tell me about containerization"

# Analyze an error
aitools error "npm install" "Error: ENOENT: no such file or directory, open 'package.json'"

# Install shell integration
aitools install-shell

# Start flight simulator assistant
aitools sim msfs start
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
