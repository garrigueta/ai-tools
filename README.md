# ai-tools

Flight Assistant for MSFS2024 with Ollama LLM integration.

## Overview

ai-tools is an assistant that integrates with Microsoft Flight Simulator 2024 and uses Ollama's local large language models to provide real-time assistance, command generation, and error explanations during flight simulation.

## Requirements

- Python 3.10+
- Ollama installed locally with a model configured
- Required Python packages (see `reqs.txt`)
- Audio playback support (for speech functionality)
  - Linux: ffplay (recommended), mpg123, mpg321, or mplayer

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-tools.git
   cd ai-tools
   ```

2. Install the required packages:
   ```bash
   pip install -r reqs.txt
   ```

3. Set up environment variables (optional):
   ```bash
   export OLLAMA_HOST=localhost
   export OLLAMA_PORT=11434
   export OLLAMA_MODEL=gemma3:27b
   ```

4. Enable the command-line error handler (optional):
   ```bash
   # Add this to your ~/.bashrc or ~/.zshrc
   source /path/to/ai-tools/.bash_ollama_actions
   ```

## Usage

The main entry point for ai-tools is `main.py`. This script provides several commands:

### Run a Natural Language Command

Generates and executes a command based on natural language input:

```bash
python main.py run "list all text files in the current directory"
```

### Send a Direct Prompt to Ollama

Send a direct prompt to the Ollama model and get a response:

```bash
python main.py prompt "Explain how autopilot works in an aircraft"
```

### Speak Response with Text-to-Speech

Send a prompt to Ollama and have the response read aloud using Google's Text-to-Speech:

```bash
python main.py speak "Tell me about landing procedures for a Cessna 172"
```

The spoken response uses Google's TTS engine for natural, human-like voice quality.

### Get Error Explanation

Analyze and explain an error message from a command:

```bash
python main.py error "npm install" "Error: ENOENT: no such file or directory, open 'package.json'"
```

### Load Documents into Knowledge Base

Load and vectorize documents from a directory to enhance AI knowledge:

```bash
python main.py load "/path/to/documents"
```

The system will automatically store documents in a unified knowledge base that the AI can access when responding to prompts.

### View Configuration

Display the current Ollama configuration:

```bash
python main.py info
```

### Help

Get help on available commands:

```bash
python main.py --help
```

## Command-Line Integration

ai-tools includes a bash integration that automatically analyzes command errors. When sourced, the `.bash_ollama_actions` file sets up error handling that will:

1. Capture failed commands
2. Send them to Ollama for analysis
3. Display helpful explanations

This feature provides real-time assistance directly in your terminal.

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

```
main.py              # Main entry point script
lib/                 # Core library code
  mcp/               # Model Context Protocol components
    actions.py       # Command execution and LLM interaction
  modules/           # Simulator interface modules
    msfs.py          # Microsoft Flight Simulator integration
    speech.py        # Text-to-speech functionality
  chat/              # Chat interface implementations
  storage/           # Knowledge storage and document loading
    docs.py          # Document vectorization and retrieval
  backend/           # Backend services
data/                # Configuration and data files
```

## Advanced Configuration

The application uses environment variables for configuration:

- `OLLAMA_HOST`: The hostname where Ollama is running (default: `localhost`)
- `OLLAMA_PORT`: The port Ollama is using (default: `11434`)
- `OLLAMA_MODEL`: The Ollama model to use (default: `gemma3:27b`)

You can set these variables in your shell or modify them in the `.bash_ollama_actions` file.

## License

[Your License Information]
