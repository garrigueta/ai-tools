#!/usr/bin/env python3
"""
Build script to create a standalone executable for the ai-tools package.
This script uses PyInstaller to package the application into a single binary.

Usage:
    python build_binary.py [--platform=<platform>]
    
    --platform: Optional argument to specify target platform (linux, win, macos)
                If not specified, builds for the current platform

Dependencies:
    PyInstaller must be installed: pip install pyinstaller
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build standalone binary for ai-tools.")
    parser.add_argument('--platform', choices=['linux', 'win', 'macos'],
                      help='Target platform (linux, win, macos). Defaults to current platform.')
    return parser.parse_args()

def build_binary():
    """Build the aitools binary package."""
    # Parse command-line arguments
    args = parse_args()
    target_platform = args.platform
    
    # If platform not specified, use current platform
    if not target_platform:
        if sys.platform.startswith('linux'):
            target_platform = 'linux'
        elif sys.platform.startswith('win'):
            target_platform = 'win'
        elif sys.platform.startswith('darwin'):
            target_platform = 'macos'
        else:
            print(f"Unknown platform: {sys.platform}")
            print("Please specify target platform with --platform=<linux|win|macos>")
            sys.exit(1)
    
    print(f"Building binary for {target_platform} platform")
    
    print("Checking for PyInstaller...")
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} found.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")
    
    # Directory setup
    root_dir = Path(__file__).parent.absolute()
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    
    # Clean previous builds if they exist
    if dist_dir.exists():
        print(f"Cleaning previous distribution in {dist_dir}")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print(f"Cleaning previous build in {build_dir}")
        shutil.rmtree(build_dir)
    
    # Define the PyInstaller command
    main_script = root_dir / "src" / "ai_tools" / "__main__.py"
    
    # Collect data files to include
    bash_script = root_dir / "src" / "ai_tools" / "shell" / "bash_aitools"
    powershell_script = root_dir / "src" / "ai_tools" / "shell" / "powershell_aitools.ps1"
    
    # Determine path separator based on target platform
    path_sep = ";" if target_platform == 'win' else ":"
    
    # Build the PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=aitools",
        "--onefile",  # Create a single executable file
        "--hidden-import=gtts",  # Add hidden dependencies
        "--hidden-import=sentence_transformers",
    ]
    
    # Add data files with correct path separator for target platform
    if target_platform == 'win':
        # Add PowerShell script for Windows builds
        pyinstaller_cmd.extend([
            "--add-data", f"{bash_script}{path_sep}ai_tools/shell/",
            "--add-data", f"{powershell_script}{path_sep}ai_tools/shell/",
        ])
    else:
        # Add only bash script for Linux/macOS builds
        pyinstaller_cmd.extend([
            "--add-data", f"{bash_script}{path_sep}ai_tools/shell/",
        ])
    
    # Add main script and platform-specific options
    pyinstaller_cmd.append(str(main_script))
    
    if target_platform == 'win':
        pyinstaller_cmd.append("--console")  # Windows: console mode
    
    print(f"Building binary with command: {' '.join(pyinstaller_cmd)}")
    subprocess.check_call(pyinstaller_cmd)
    
    # Create platform-specific installer and prepare files
    if target_platform == 'win':
        # Create Windows installer script (PowerShell)
        create_windows_installer(dist_dir, powershell_script, bash_script)
    else:
        # Create Unix installer script (Bash)
        create_unix_installer(dist_dir, bash_script)
    
    print(f"\nBuild complete! Binary and installer available in {dist_dir}")
    
    if target_platform == 'win':
        print("To create a distributable package:")
        print(f"cd {dist_dir} && Compress-Archive -Path aitools.exe,install.ps1,powershell_aitools.ps1,bash_aitools -DestinationPath aitools-windows.zip")
    else:
        print("To create a distributable package:")
        print(f"cd {dist_dir} && tar -czvf aitools-binary.tar.gz aitools install.sh bash_aitools")

def create_unix_installer(dist_dir, bash_script):
    """Create installer script for Unix-like systems (Linux/macOS)."""
    installer_script = dist_dir / "install.sh"
    with open(installer_script, 'w') as f:
        f.write("""#!/bin/bash
# Installer script for ai-tools binary

# Exit on error
set -e

# Determine installation directory
if [ "$EUID" -eq 0 ]; then
    # Running as root, install for all users
    INSTALL_DIR="/usr/local/bin"
    SHELL_DIR="/etc/profile.d"
else
    # Running as user, install for current user only
    INSTALL_DIR="$HOME/.local/bin"
    SHELL_DIR="$HOME"
    # Create bin directory if it doesn't exist
    mkdir -p "$INSTALL_DIR"
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        echo "Adding $INSTALL_DIR to your PATH..."
        echo 'export PATH="$PATH:$HOME/.local/bin"' >> "$HOME/.bashrc"
        echo "Please run 'source ~/.bashrc' after installation or restart your terminal."
    fi
fi

# Copy executable to installation directory
echo "Installing aitools binary to $INSTALL_DIR..."
cp aitools "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/aitools"

# Install shell integration
echo "Installing shell integration..."
if [ "$EUID" -eq 0 ]; then
    # System-wide installation
    cp bash_aitools "$SHELL_DIR/bash_aitools.sh"
    echo "Adding shell integration to /etc/profile.d..."
    echo 'You will need to run "source /etc/profile.d/bash_aitools.sh" or log out and back in.'
else
    # User-specific installation
    cp bash_aitools "$SHELL_DIR/.bash_aitools"
    
    # Check if already in bashrc
    if ! grep -q "source ~/.bash_aitools" "$HOME/.bashrc"; then
        echo "# AI-Tools Shell Integration" >> "$HOME/.bashrc"
        echo 'if [ -f "$HOME/.bash_aitools" ]; then' >> "$HOME/.bashrc"
        echo '    source "$HOME/.bash_aitools"' >> "$HOME/.bashrc"
        echo 'fi' >> "$HOME/.bashrc"
        echo "Shell integration added to .bashrc"
    else:
        echo "Shell integration already in .bashrc"
    fi
fi

echo ""
echo "Installation complete! You can now use 'aitools' command."
echo "To activate shell integration in current terminal, run: source ~/.bash_aitools"
""")
    
    # Make the installer executable
    installer_script.chmod(0o755)
    
    # Copy shell script to dist directory for the installer
    shutil.copy(bash_script, dist_dir / "bash_aitools")

def create_windows_installer(dist_dir, powershell_script, bash_script):
    """Create installer script for Windows systems."""
    installer_script = dist_dir / "install.ps1"
    with open(installer_script, 'w') as f:
        f.write("""# PowerShell installer script for AI-Tools binary

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Determine installation directory
if ($isAdmin) {
    # System-wide installation
    $installDir = "$env:ProgramFiles\\AI-Tools"
    $modulesDir = "$env:ProgramFiles\\WindowsPowerShell\\Modules\\AI-Tools"
} else {
    # User-specific installation
    $installDir = "$env:LOCALAPPDATA\\AI-Tools"
    $modulesDir = "$env:USERPROFILE\\Documents\\WindowsPowerShell\\Modules\\AI-Tools"
}

# Create installation directories if they don't exist
Write-Host "Creating installation directories..." -ForegroundColor Cyan
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}
if (-not (Test-Path $modulesDir)) {
    New-Item -ItemType Directory -Path $modulesDir -Force | Out-Null
}

# Copy executable to installation directory
Write-Host "Installing aitools binary to $installDir..." -ForegroundColor Cyan
Copy-Item -Path "aitools.exe" -Destination "$installDir" -Force

# Copy PowerShell integration script to modules directory
Write-Host "Installing PowerShell integration..." -ForegroundColor Cyan
Copy-Item -Path "powershell_aitools.ps1" -Destination "$modulesDir" -Force
Copy-Item -Path "bash_aitools" -Destination "$installDir" -Force

# Create module manifest
$manifestPath = "$modulesDir\\AI-Tools.psd1"
Write-Host "Creating PowerShell module manifest..." -ForegroundColor Cyan
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
"@ | Out-File -FilePath $manifestPath -Force -Encoding utf8

# Add to PATH if not already there
$envPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::User)
if (-not $envPath.Contains($installDir)) {
    Write-Host "Adding $installDir to your PATH..." -ForegroundColor Cyan
    [Environment]::SetEnvironmentVariable("PATH", "$envPath;$installDir", [EnvironmentVariableTarget]::User)
    $env:PATH = "$env:PATH;$installDir"
}

# Create profile if it doesn't exist
$profileDir = Split-Path -Parent $PROFILE
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Add import to PowerShell profile
if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}

# Check if module import already exists in profile
$profileContent = Get-Content $PROFILE -ErrorAction SilentlyContinue
if (-not ($profileContent -match "Import-Module AI-Tools")) {
    Write-Host "Adding module import to your PowerShell profile..." -ForegroundColor Cyan
    @"

# AI-Tools Integration
if (Get-Module -ListAvailable -Name AI-Tools) {
    Import-Module AI-Tools
    Write-Host 'AI-Tools module loaded.' -ForegroundColor Green
} else {
    Write-Host 'AI-Tools module not found.' -ForegroundColor Yellow
}
"@ | Out-File -FilePath $PROFILE -Append -Encoding utf8
}

Write-Host ""
Write-Host "Installation complete! You can now use the 'aitools' command." -ForegroundColor Green
Write-Host "To activate the PowerShell integration in the current session, run:" -ForegroundColor Green
Write-Host "Import-Module AI-Tools" -ForegroundColor Yellow
Write-Host ""
Write-Host "The module will be loaded automatically in new PowerShell sessions." -ForegroundColor Green
Write-Host "Available commands: mop, Check-Ollama, Check-Model, Check-Models, Test-Ollama" -ForegroundColor Cyan
Write-Host "Use 'iweh { command }' to run commands with error handling" -ForegroundColor Cyan
""")

    # Copy shell scripts to dist directory for the installer
    shutil.copy(powershell_script, dist_dir / "powershell_aitools.ps1")
    shutil.copy(bash_script, dist_dir / "bash_aitools")

if __name__ == "__main__":
    build_binary()