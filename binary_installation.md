# AI-Tools Binary Installation Guide

This guide explains how to build, install, and use the binary version of the `ai-tools` package.

## Overview

The binary version of AI-Tools provides a standalone executable that doesn't require Python or any dependencies to be installed on the target system. This makes it ideal for:

- Users without Python knowledge
- Deployment on systems where installing Python packages is complicated
- Creating distributable packages for end-users
- Systems with restricted permissions

## Building the Binary

### Prerequisites for Building

- Python 3.10 or higher
- PyInstaller (will be automatically installed if missing)
- Git repository clone of ai-tools

### Building Steps

1. Clone the repository if you haven't already:
   ```bash
   git clone https://github.com/garrigueta/ai-tools.git
   cd ai-tools
   ```

2. Run the binary build script:
   ```bash
   python build_binary.py
   ```

3. The script will:
   - Install PyInstaller if it's not already available
   - Clean previous builds if they exist
   - Package the application into a single executable
   - Create an installer script
   - Place all files in the `dist` directory

4. When complete, you'll find these files in the `dist` directory:
   - `aitools`: The standalone executable
   - `install.sh`: An installer script for easy deployment
   - `bash_aitools`: Shell integration script for command-line features

5. (Optional) Create a distributable package:
   ```bash
   cd dist
   tar -czvf aitools-binary.tar.gz aitools install.sh bash_aitools
   ```

## Installing the Binary

### Method 1: Using the Installer Script

1. Navigate to the directory containing the binary files:
   ```bash
   cd /path/to/ai-tools/dist
   ```

2. Run the installer script:
   ```bash
   # For user installation (recommended)
   ./install.sh
   
   # For system-wide installation (requires root)
   sudo ./install.sh
   ```

3. The installer will:
   - Copy the `aitools` executable to the appropriate bin directory (`~/.local/bin` for user install or `/usr/local/bin` for system-wide)
   - Install the shell integration script
   - Configure your `.bashrc` to load the shell integration (user install only)
   - Provide instructions on activating the integration in your current shell

### Method 2: Manual Installation

1. Copy the binary to a directory in your PATH:
   ```bash
   # For user installation
   mkdir -p ~/.local/bin
   cp /path/to/ai-tools/dist/aitools ~/.local/bin/
   chmod +x ~/.local/bin/aitools
   
   # For system-wide installation
   sudo cp /path/to/ai-tools/dist/aitools /usr/local/bin/
   sudo chmod +x /usr/local/bin/aitools
   ```

2. Copy the shell integration script:
   ```bash
   # For user installation
   cp /path/to/ai-tools/dist/bash_aitools ~/.bash_aitools
   
   # For system-wide installation
   sudo cp /path/to/ai-tools/dist/bash_aitools /etc/profile.d/bash_aitools.sh
   ```

3. Add the shell integration to your `.bashrc` (user installation only):
   ```bash
   echo '# AI-Tools Shell Integration' >> ~/.bashrc
   echo 'if [ -f "$HOME/.bash_aitools" ]; then' >> ~/.bashrc
   echo '    source "$HOME/.bash_aitools"' >> ~/.bashrc
   echo 'fi' >> ~/.bashrc
   ```

4. Activate the shell integration in your current terminal:
   ```bash
   source ~/.bash_aitools  # For user installation
   # OR
   source /etc/profile.d/bash_aitools.sh  # For system-wide installation
   ```

## Using the Binary Version

The binary version of AI-Tools provides the same functionality as the source version, but without requiring Python or any dependencies to be installed.

### Basic Commands

```bash
# Send a direct prompt to Ollama
aitools prompt "Explain how regex works in Python"

# Generate and execute a command from natural language
aitools run "list all text files in the current directory"

# Get spoken output (requires internet connection for Google TTS)
aitools speak "Tell me about the benefits of containerization"

# Analyze an error message
aitools error "npm install" "Error: ENOENT: no such file or directory, open 'package.json'"

# Get help on available commands
aitools --help

# Show configuration information
aitools info
```

### Required Environment Setup

Just like the source version, the binary version requires Ollama to be installed and running. Set up these environment variables to configure your AI-Tools experience:

```bash
# Basic configuration
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MODEL=gemma3:27b
```

For a complete list of all available environment variables, see the [Advanced Configuration](README.md#advanced-configuration) section in the README.

### Shell Integration Features

The binary installation includes the shell integration that provides:

1. **Automatic Error Analysis**: When a command fails, the error is automatically analyzed by the AI
2. **Ollama Connection Checking**: Functions to check if Ollama is running
3. **Model Availability**: Check if your configured model is available

Available shell functions:
- `check_ollama` - Check if Ollama is running
- `check_model` - Check if the configured model is available
- `check_models` - List all available Ollama models
- `test_ollama` - Test Ollama with a simple prompt
- `init_ollama_tools` - Initialize and check Ollama setup

### Using the Shell Integration Alias

The shell integration includes an alias for convenience:

```bash
# 'mop' is a shorthand for 'aitools'
mop prompt "What's the weather like today?"
```

## Advanced Features for Binary Usage

### Database Configuration

The binary version supports all the same database features as the source version. To enable them:

```bash
# Set database environment variables
export OLLAMA_DB_ENABLED=true
export OLLAMA_DB_HOST=localhost
export OLLAMA_DB_PORT=5432
export OLLAMA_DB_USER=aitools
export OLLAMA_DB_PASSWORD=your_password
export OLLAMA_DB_NAME=ai_tools_db
```

### Verifying Binary Installation

To verify that your binary installation is working correctly:

1. Check basic functionality:
   ```bash
   aitools prompt "Hello, are you working correctly?"
   ```

2. Test Ollama connection:
   ```bash
   # Source the shell integration if not already done
   source ~/.bash_aitools
   # Run the test function
   test_ollama
   ```

3. Check environment configuration:
   ```bash
   aitools info
   ```

### Uninstalling the Binary

To uninstall the binary version:

1. Delete the executable:
   ```bash
   # User installation
   rm ~/.local/bin/aitools
   
   # System-wide installation
   sudo rm /usr/local/bin/aitools
   ```

2. Delete the shell integration script:
   ```bash
   # User installation
   rm ~/.bash_aitools
   
   # System-wide installation
   sudo rm /etc/profile.d/bash_aitools.sh
   ```

3. Remove the source line from your `.bashrc` (user installation only):
   ```bash
   # Edit .bashrc and remove these lines:
   # # AI-Tools Shell Integration
   # if [ -f "$HOME/.bash_aitools" ]; then
   #     source "$HOME/.bash_aitools"
   # fi
   ```

## Troubleshooting Binary Installation

### Common Issues and Solutions

1. **Binary not found after installation**
   - Check if the installation directory is in your PATH:
     ```bash
     echo $PATH | grep -E '(\.local/bin|/usr/local/bin)'
     ```
   - If not, add it to your PATH:
     ```bash
     echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
     source ~/.bashrc
     ```

2. **Permission denied when running the binary**
   - Ensure the binary is executable:
     ```bash
     chmod +x ~/.local/bin/aitools   # For user installation
     sudo chmod +x /usr/local/bin/aitools  # For system-wide installation
     ```

3. **Shell integration not working**
   - Make sure you've sourced the shell integration file:
     ```bash
     source ~/.bash_aitools   # For user installation
     source /etc/profile.d/bash_aitools.sh  # For system-wide installation
     ```
   - Verify the shell integration is in your .bashrc (user installation only):
     ```bash
     grep -A 3 "AI-Tools Shell Integration" ~/.bashrc
     ```

4. **Missing shared libraries**
   - If you see "error while loading shared libraries" messages, you may need to install the missing libraries:
     ```bash
     # Example for common dependencies on Ubuntu/Debian
     sudo apt-get update
     sudo apt-get install libffi7 libbz2-1.0
     ```

5. **Ollama connection issues**
   - The binary requires a running Ollama server just like the source version:
     ```bash
     # Check if Ollama is running
     curl http://localhost:11434/api/tags
     
     # Start Ollama if it's not running
     ollama serve
     ```

For more detailed troubleshooting, refer to the [Troubleshooting](INSTALL.md#troubleshooting) section in INSTALL.md.

## Differences Between Binary and Source Installation

The binary version has a few differences from the source installation:

1. **Fixed Dependencies**: The binary includes all necessary dependencies, which means:
   - You don't need to worry about Python version compatibility
   - No need to install or manage Python packages
   - Dependencies can't be updated without rebuilding the binary

2. **Size**: The binary is significantly larger than the source code because it includes:
   - A complete Python interpreter
   - All required libraries
   - Pre-trained embedding models

3. **Updates**: To update the binary:
   - You must rebuild the binary from the latest source
   - There's no "update" command like with pip or Poetry

4. **Platform Specificity**: Binaries are platform-specific:
   - A binary built on Linux will only work on Linux (and similar enough distributions)
   - A binary built on macOS will only work on macOS
   - Different binaries are needed for different platforms

## Conclusion

The binary version of AI-Tools provides a convenient way to distribute and use the package without requiring Python knowledge or setting up a development environment. It includes all the functionality of the source version in a single, self-contained executable.