#!/usr/bin/env python3
"""
Shell integration tools for ai-tools package.
This module provides functionality to install bash scripts for enhanced terminal integration.
"""

import os
import shutil
import subprocess
from pathlib import Path
import platform

def get_package_root():
    """Get the root directory of the installed package"""
    # The bash file will be inside the package directory
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_bash_script_path():
    """Get the path to the .bash_aitools script inside the package"""
    return os.path.join(get_package_root(), "ai_tools", "shell", "bash_aitools")

def get_user_home():
    """Get the user's home directory"""
    return str(Path.home())

def get_shell_config_file():
    """Determine which shell config file to modify"""
    home = get_user_home()
    shell = os.environ.get("SHELL", "")
    
    # Check if user has a .bashrc file
    if os.path.exists(os.path.join(home, ".bashrc")):
        return os.path.join(home, ".bashrc")
    # Check for zsh
    elif "zsh" in shell and os.path.exists(os.path.join(home, ".zshrc")):
        return os.path.join(home, ".zshrc")
    # Default to .bash_profile if exists
    elif os.path.exists(os.path.join(home, ".bash_profile")):
        return os.path.join(home, ".bash_profile")
    # If nothing suitable is found, default to .bashrc
    else:
        return os.path.join(home, ".bashrc")

def is_shell_integration_installed():
    """Check if the shell integration is already installed"""
    config_file = get_shell_config_file()
    bash_script_path = get_bash_script_path()
    
    # Check if the config file exists and contains a reference to our script
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            return f"source {bash_script_path}" in content or "source ~/.bash_aitools" in content
    
    return False

def install_shell_integration(auto_source=False):
    """
    Install the shell integration by copying the bash script to the user's home
    and adding a source command to their shell config file.
    
    Args:
        auto_source: If True, add source command to shell config automatically
    
    Returns:
        dict: Status information about the installation
    """
    try:
        # Get paths
        home = get_user_home()
        bash_script_path = get_bash_script_path()
        config_file = get_shell_config_file()
        
        # Create the destination directory in the package
        os.makedirs(os.path.dirname(bash_script_path), exist_ok=True)
        
        # Check if we have permission to write to the user's home directory
        if not os.access(home, os.W_OK):
            return {
                "status": "error",
                "message": f"No write permission to user's home directory: {home}"
            }
        
        # Copy the .bash_aitools file to the user's home directory
        user_script_path = os.path.join(home, ".bash_aitools")
        shutil.copy(bash_script_path, user_script_path)
        os.chmod(user_script_path, 0o755)  # Make it executable
        
        # Add source command to shell config if requested
        if auto_source and not is_shell_integration_installed():
            with open(config_file, 'a') as f:
                f.write(f"\n# AI-Tools shell integration\nsource {user_script_path}\n")
            
            return {
                "status": "success",
                "message": f"Shell integration installed to {user_script_path}",
                "config_file": config_file,
                "auto_source": True
            }
        else:
            # Just return the information without modifying shell config
            return {
                "status": "success",
                "message": f"Shell integration installed to {user_script_path}",
                "manual_source_cmd": f"source {user_script_path}",
                "config_file": config_file,
                "auto_source": False
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error installing shell integration: {str(e)}"
        }

def install_shell_integration_command():
    """Command-line function for installing the shell integration"""
    print("Installing AI-Tools shell integration...")
    result = install_shell_integration(auto_source=False)
    
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        print(f"\nTo enable shell integration, add this line to your {result['config_file']}:")
        print(f"  source {result['manual_source_cmd']}")
        print("\nOr run this command:")
        print(f"  echo 'source {result['manual_source_cmd']}' >> {result['config_file']}")
    else:
        print(f"❌ {result['message']}")
        
    return 0 if result["status"] == "success" else 1