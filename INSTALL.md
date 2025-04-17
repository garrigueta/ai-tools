# Installation Guide for AI-Tools

This guide explains how to install the `ai-tools` package using Poetry.

## Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/docs/#installation) package manager

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

## Environment Configuration

Set these environment variables to customize your AI-Tools experience:

```bash
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MODEL=gemma3:27b
```

## Shell Integration

To enable command-line error handling integration:

```bash
echo 'source /path/to/ai-tools/.bash_ollama_actions' >> ~/.bashrc
source ~/.bashrc
```

## Troubleshooting

If you encounter import errors:
1. Make sure you're using the virtual environment created by Poetry
2. Try reinstalling the package with `poetry install --no-dev`
3. Check Python version with `python --version` (requires 3.10+)