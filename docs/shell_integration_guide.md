# AI-Tools Shell Integration Guide

This guide explains how to effectively use the AI-Tools shell integration features after installation, with a focus on automatic error handling and AI-powered terminal enhancements.

## Overview

The AI-Tools shell integration (`bash_aitools`) provides several powerful features:

- **Automatic Error Analysis**: When a command fails, errors are automatically analyzed by the AI
- **Ollama Connection Utilities**: Built-in functions to check if Ollama is running and properly configured
- **Model Management**: Easy verification of your configured model's availability
- **Terminal Productivity Enhancements**: Handy aliases and shortcuts for common AI operations

## Prerequisites

- AI-Tools installed (via binary or source)
- Shell integration installed and activated
- Ollama running locally or remotely (as configured)

## Getting Started with Shell Integration

### Verifying Installation

First, verify that your shell integration is properly installed:

```bash
# Check if bash_aitools is sourced in your current session
type check_ollama

# Expected output should show that check_ollama is a function
# If not found, you may need to source the file manually:
source ~/.bash_aitools
```

### Basic Shell Integration Features

Once installed, you have access to several helpful functions:

- `check_ollama` - Verify if Ollama is running
- `check_model` - Check if your configured AI model is available
- `check_models` - List all available Ollama models
- `test_ollama` - Test Ollama with a simple prompt
- `init_ollama_tools` - Initialize and check the entire Ollama setup

Example usage:

```bash
# Check if Ollama is running
check_ollama

# See if your configured model is available
check_model

# List all available models
check_models

# Test Ollama with a simple prompt
test_ollama
```

## Automatic Error Handling

The most powerful feature of the shell integration is automatic error analysis. When commands fail in your terminal, AI-Tools will:

1. Capture the failed command and its error output
2. Send the information to Ollama for analysis
3. Display a helpful explanation and suggested solutions

### How Error Handling Works

The error handling is completely automatic once the shell integration is active:

```bash
# Example of running a command that will fail
npm install   # When no package.json exists

# The shell integration will automatically:
# 1. Detect the error
# 2. Send it to Ollama for analysis
# 3. Display an explanation like:
#    "💡 The error suggests you're trying to run npm install without a package.json file..."
```

### Platform-Specific Considerations

#### Linux/macOS

On Linux and macOS, the shell integration is automatically loaded if you've added the source line to your `.bashrc` or `.zshrc`:

```bash
# This line should be in your ~/.bashrc file
if [ -f "$HOME/.bash_aitools" ]; then
    source "$HOME/.bash_aitools"
fi
```

#### Windows

On Windows, different approaches are available:

1. **WSL/Git Bash**: Use the same approach as Linux with `bash_aitools`

2. **PowerShell**: Use the PowerShell module that's installed with the Windows version:
   ```powershell
   # This should be in your PowerShell profile
   Import-Module AI-Tools
   ```

## Manual Error Analysis

If you prefer to manually analyze errors rather than using the automatic integration, you can use the `aitools error` command directly:

```bash
# Syntax: aitools error "command" "error message"
aitools error "npm install" "Error: ENOENT: no such file or directory, open 'package.json'"
```

## Customization

### Disabling Automatic Error Analysis

If you want to temporarily disable automatic error analysis:

```bash
# Set this environment variable to disable automatic error analysis
export AITOOLS_DISABLE_AUTO_ERROR=1

# To re-enable:
unset AITOOLS_DISABLE_AUTO_ERROR
```

### Adjusting Model Settings

You can view and update your AI-Tools configuration:

```bash
# View current configuration
aitools info

# Update configuration (refer to configuration documentation for more details)
aitools config set model llama3:8b
```

## Troubleshooting

### Common Issues

1. **Error analysis not working automatically**:
   - Verify the shell integration is properly sourced
   - Check that Ollama is running with `check_ollama`
   - Ensure your model is available with `check_model`

2. **Slow response times**:
   - Consider using a smaller model for faster responses
   - Check network connection if using a remote Ollama instance

3. **Shell integration not found**:
   - Verify the installation path with `ls -la ~/.bash_aitools`
   - Reinstall shell integration with `aitools install-shell`

## Advanced Usage

### Combining with Other AI-Tools Features

The shell integration works seamlessly with other AI-Tools features:

```bash
# Generate and execute a command
aitools run "list all text files in the current directory"

# Get an explanation from the AI
aitools prompt "Explain how regex works in Python"

# Spoken response (requires TTS setup)
aitools speak "Tell me about containerization"
```

## Conclusion

The AI-Tools shell integration transforms your terminal experience by providing intelligent error handling and AI assistance directly in your workflow. With automatic error analysis, you'll spend less time troubleshooting and more time being productive.

For more information on other AI-Tools features, refer to the [User Guide](user_guide.md).