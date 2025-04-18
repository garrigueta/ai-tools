#!/usr/bin/env python3
"""
Build script to create a standalone executable for the ai-tools package.
This script uses PyInstaller to package the application into a single binary.

Usage:
    python build_binary.py

Dependencies:
    PyInstaller must be installed: pip install pyinstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_binary():
    """Build the aitools binary package."""
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
    shell_script = root_dir / "src" / "ai_tools" / "shell" / "bash_aitools"
    
    # Build the PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=aitools",
        "--onefile",  # Create a single executable file
        "--add-data", f"{shell_script}:ai_tools/shell/",  # Include shell script
        "--hidden-import=gtts",  # Add hidden dependencies
        "--hidden-import=sentence_transformers",
        str(main_script),
    ]
    
    # Add platform-specific options
    if sys.platform.startswith('win'):
        pyinstaller_cmd.append("--console")  # Windows: console mode
    
    print(f"Building binary with command: {' '.join(pyinstaller_cmd)}")
    subprocess.check_call(pyinstaller_cmd)
    
    # Create installation script
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
    else
        echo "Shell integration already in .bashrc"
    fi
fi

echo ""
echo "Installation complete! You can now use 'aitools' command."
echo "To activate shell integration in current terminal, run: source ~/.bash_aitools"
""")
    
    # Make the installer executable
    installer_script.chmod(0o755)
    
    # Also copy shell script to dist directory for the installer
    shutil.copy(shell_script, dist_dir / "bash_aitools")
    
    print(f"\nBuild complete! Binary and installer available in {dist_dir}")
    print("To create a distributable package:")
    print(f"cd {dist_dir} && tar -czvf aitools-binary.tar.gz aitools install.sh bash_aitools")

if __name__ == "__main__":
    build_binary()