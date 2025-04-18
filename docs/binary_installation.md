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
   # Build for the current platform
   python build_binary.py
   
   # Or specify a target platform
   python build_binary.py --platform=linux
   python build_binary.py --platform=win
   python build_binary.py --platform=macos
   ```

3. The script will:
   - Install PyInstaller if it's not already available
   - Clean previous builds if they exist
   - Package the application into a single executable
   - Create platform-specific installer scripts
   - Place all files in the `dist` directory

4. When complete, you'll find these files in the `dist` directory:
   
   **For Linux/macOS:**
   - `aitools`: The standalone executable
   - `install.sh`: A Bash installer script for easy deployment
   - `bash_aitools`: Shell integration script for Bash

   **For Windows:**
   - `aitools.exe`: The standalone executable
   - `install.ps1`: A PowerShell installer script for easy deployment
   - `powershell_aitools.ps1`: Shell integration script for PowerShell
   - `bash_aitools`: Shell integration script for WSL/Git Bash

5. (Optional) Create a distributable package:
   ```bash
   # For Linux/macOS
   cd dist
   tar -czvf aitools-binary.tar.gz aitools install.sh bash_aitools
   
   # For Windows (in PowerShell)
   cd dist
   Compress-Archive -Path aitools.exe,install.ps1,powershell_aitools.ps1,bash_aitools -DestinationPath aitools-windows.zip
   ```

## Installing the Binary

### Linux/macOS Installation

#### Method 1: Using the Installer Script

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

#### Method 2: Manual Installation

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

### Windows Installation

#### Method 1: Using the PowerShell Installer Script

1. Navigate to the directory containing the binary files:
   ```powershell
   cd \path\to\ai-tools\dist
   ```

2. Run the installer script in PowerShell:
   ```powershell
   # For user installation (recommended)
   .\install.ps1
   
   # For system-wide installation (run PowerShell as Administrator first)
   # Right-click on PowerShell -> Run as Administrator, then run:
   .\install.ps1
   ```

3. The installer will:
   - Copy the `aitools.exe` executable to the appropriate directory
   - Install the PowerShell integration script as a proper PowerShell module
   - Add the installation directory to your PATH
   - Configure your PowerShell profile to load the module automatically
   - Provide instructions on activating the integration in your current session

#### Method 2: Manual Installation

1. Create installation directories:
   ```powershell
   # For user installation
   New-Item -ItemType Directory -Path "$env:LOCALAPPDATA\AI-Tools" -Force
   New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\WindowsPowerShell\Modules\AI-Tools" -Force
   
   # For system-wide installation (in admin PowerShell)
   New-Item -ItemType Directory -Path "$env:ProgramFiles\AI-Tools" -Force
   New-Item -ItemType Directory -Path "$env:ProgramFiles\WindowsPowerShell\Modules\AI-Tools" -Force
   ```

2. Copy files to the appropriate locations:
   ```powershell
   # For user installation
   Copy-Item -Path "aitools.exe" -Destination "$env:LOCALAPPDATA\AI-Tools\" -Force
   Copy-Item -Path "powershell_aitools.ps1" -Destination "$env:USERPROFILE\Documents\WindowsPowerShell\Modules\AI-Tools\" -Force
   
   # For system-wide installation (in admin PowerShell)
   Copy-Item -Path "aitools.exe" -Destination "$env:ProgramFiles\AI-Tools\" -Force
   Copy-Item -Path "powershell_aitools.ps1" -Destination "$env:ProgramFiles\WindowsPowerShell\Modules\AI-Tools\" -Force
   ```

3. Create a PowerShell module manifest:
   ```powershell
   # Create a module manifest (adjust path based on your installation type)
   $modulesDir = "$env:USERPROFILE\Documents\WindowsPowerShell\Modules\AI-Tools"  # Or use $env:ProgramFiles if admin
   
   # Manifest content
   @"
@{
    RootModule = 'powershell_aitools.ps1'
    ModuleVersion = '1.0.0'
    GUID = '$(New-Guid)'
    Author = 'AI-Tools'
    Description = 'AI Tools with Ollama LLM integration for OS assistance'
    PowerShellVersion = '5.1'
    FunctionsToExport = @('mop', 'Check-Ollama', 'Check-Model', 'Check-Models', 'Test-Ollama', 'Initialize-OllamaTools', 'Invoke-WithErrorHandling', 'iweh', 'Handle-CommandError')
    VariablesToExport = '*'
    AliasesToExport = @('mop')
}
"@ | Out-File -FilePath "$modulesDir\AI-Tools.psd1" -Force -Encoding utf8
   ```

4. Add the executable directory to your PATH:
   ```powershell
   # For user installation
   $installDir = "$env:LOCALAPPDATA\AI-Tools"
   $envPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
   [Environment]::SetEnvironmentVariable("PATH", "$envPath;$installDir", [EnvironmentVariableTarget]::User)
   $env:PATH = "$env:PATH;$installDir"
   ```

5. Modify your PowerShell profile to load the module:
   ```powershell
   # Create profile if it doesn't exist
   if (-not (Test-Path $PROFILE)) {
       New-Item -ItemType File -Path $PROFILE -Force | Out-Null
   }
   
   # Add module import to profile
   @"

# AI-Tools Integration
if (Get-Module -ListAvailable -Name AI-Tools) {
    Import-Module AI-Tools
    Write-Host 'AI-Tools module loaded.' -ForegroundColor Green
}
"@ | Out-File -FilePath $PROFILE -Append -Encoding utf8
   ```

6. Load the module in your current session:
   ```powershell
   Import-Module AI-Tools
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

**Linux/macOS (Bash):**
```bash
# Basic configuration
export OLLAMA_HOST=localhost
export OLLAMA_PORT=11434
export OLLAMA_MODEL=gemma3:27b
```

**Windows (PowerShell):**
```powershell
# Basic configuration
$env:OLLAMA_HOST = "localhost"
$env:OLLAMA_PORT = "11434"
$env:OLLAMA_MODEL = "gemma3:27b"

# To make these settings persistent (user-specific)
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "localhost", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("OLLAMA_PORT", "11434", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("OLLAMA_MODEL", "gemma3:27b", [EnvironmentVariableTarget]::User)
```

For a complete list of all available environment variables, see the [Advanced Configuration](README.md#advanced-configuration) section in the README.

### Shell Integration Features

#### Bash Integration (Linux/macOS/WSL)

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

#### PowerShell Integration (Windows)

The Windows binary comes with a comprehensive PowerShell module that provides:

1. **Interactive Error Analysis**: Use the `iweh` wrapper to run commands with error handling
2. **Ollama Connection Verification**: Functions to check Ollama status
3. **Model Management**: Check and list available models
4. **Colorful Terminal Output**: Informative color-coded messages

Available PowerShell functions:
- `Check-Ollama` - Check if Ollama is running
- `Check-Model` - Check if your model is available
- `Check-Models` - List all available models
- `Test-Ollama` - Test Ollama with a simple prompt
- `Initialize-OllamaTools` - Initialize and check Ollama setup
- `iweh` - Run a command with error handling (e.g., `iweh { npm install }`)
- `Invoke-WithErrorHandling` - Same as iweh but with a more PowerShell-standard name

### Using the Shell Integration Alias

Both Bash and PowerShell integrations include an alias for convenience:

```bash
# In Bash/Zsh (Linux/macOS)
mop prompt "What's the weather like today?"
```

```powershell
# In PowerShell (Windows)
mop prompt "What's the weather like today?"
```

## Advanced Features for Binary Usage

### Database Configuration

The binary version supports all the same database features as the source version. To enable them:

**Linux/macOS:**
```bash
# Set database environment variables
export OLLAMA_DB_ENABLED=true
export OLLAMA_DB_HOST=localhost
export OLLAMA_DB_PORT=5432
export OLLAMA_DB_USER=aitools
export OLLAMA_DB_PASSWORD=your_password
export OLLAMA_DB_NAME=ai_tools_db
```

**Windows:**
```powershell
# Set database environment variables
$env:OLLAMA_DB_ENABLED="true"
$env:OLLAMA_DB_HOST="localhost"
$env:OLLAMA_DB_PORT="5432"
$env:OLLAMA_DB_USER="aitools"
$env:OLLAMA_DB_PASSWORD="your_password"
$env:OLLAMA_DB_NAME="ai_tools_db"
```

### Verifying Binary Installation

To verify that your binary installation is working correctly:

**Linux/macOS:**
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

**Windows:**
1. Check basic functionality:
   ```powershell
   aitools prompt "Hello, are you working correctly?"
   ```

2. Test Ollama connection:
   ```powershell
   # Make sure the module is imported
   Import-Module AI-Tools
   # Run the test function
   Test-Ollama
   ```

### Uninstalling the Binary

**Linux/macOS:**
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

**Windows:**
1. Delete the executable and integration files:
   ```powershell
   # User installation
   Remove-Item -Path "$env:LOCALAPPDATA\AI-Tools" -Recurse -Force
   Remove-Item -Path "$env:USERPROFILE\Documents\WindowsPowerShell\Modules\AI-Tools" -Recurse -Force
   
   # System-wide installation (in admin PowerShell)
   Remove-Item -Path "$env:ProgramFiles\AI-Tools" -Recurse -Force
   Remove-Item -Path "$env:ProgramFiles\WindowsPowerShell\Modules\AI-Tools" -Recurse -Force
   ```

2. Remove the module import from your PowerShell profile:
   ```powershell
   # Edit your PowerShell profile and remove the AI-Tools Integration section
   notepad $PROFILE
   ```

3. Remove from PATH (only if added manually):
   ```powershell
   # Get current path
   $path = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
   
   # Remove AI-Tools directory from path
   $newPath = ($path -split ';' | Where-Object { $_ -notmatch 'AI-Tools' }) -join ';'
   
   # Set the new PATH
   [Environment]::SetEnvironmentVariable("PATH", $newPath, [EnvironmentVariableTarget]::User)
   ```

## Troubleshooting Binary Installation

### Common Issues and Solutions

#### Linux/macOS Issues

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

#### Windows Issues

1. **Cannot find aitools.exe after installation**
   - Check if the installation directory is in your PATH:
     ```powershell
     $env:PATH -split ';' | Where-Object { $_ -match 'AI-Tools' }
     ```
   - If not, add it to your PATH:
     ```powershell
     $installDir = "$env:LOCALAPPDATA\AI-Tools"
     [Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$installDir", [EnvironmentVariableTarget]::User)
     $env:PATH = "$env:PATH;$installDir"
     ```

2. **PowerShell module not loading automatically**
   - Check if the module is installed correctly:
     ```powershell
     Get-Module -ListAvailable -Name AI-Tools
     ```
   - Verify your PowerShell profile:
     ```powershell
     Test-Path $PROFILE
     Get-Content $PROFILE | Select-String -Pattern "AI-Tools"
     ```
   - Manually import the module:
     ```powershell
     Import-Module AI-Tools -Force
     ```

3. **PowerShell execution policy preventing script execution**
   - You might need to adjust your PowerShell execution policy:
     ```powershell
     # Check current policy
     Get-ExecutionPolicy
     
     # Set to a more permissive policy (run as administrator)
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

#### General Issues for All Platforms

1. **Ollama connection issues**
   - The binary requires a running Ollama server just like the source version:
     ```bash
     # Check if Ollama is running (Linux/macOS)
     curl http://localhost:11434/api/tags
     
     # Check if Ollama is running (Windows PowerShell)
     Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing
     
     # Start Ollama if it's not running
     ollama serve
     ```

2. **Missing shared libraries**
   - If you see "error while loading shared libraries" messages on Linux, install the missing libraries:
     ```bash
     # Example for common dependencies on Ubuntu/Debian
     sudo apt-get update
     sudo apt-get install libffi7 libbz2-1.0
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
   - A binary built on Windows will only work on Windows
   - Different binaries are needed for different platforms

## Conclusion

The binary version of AI-Tools provides a convenient way to distribute and use the package without requiring Python knowledge or setting up a development environment. It includes all the functionality of the source version in a single, self-contained executable with platform-specific integration for both Linux/macOS (Bash) and Windows (PowerShell).