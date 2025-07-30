"""
Shell detection and utilities.
"""

import os
import subprocess
from typing import Optional

def detect_shell() -> str:
    """
    Detect the current shell being used.
    
    Returns:
        Shell name (bash, zsh, cmd, powershell, etc.)
    """
    if os.name == "nt":  # Windows
        # Try to detect PowerShell
        try:
            subprocess.run(["powershell", "-Command", "echo $PSVersionTable"], 
                         capture_output=True, check=True)
            return "powershell"
        except (subprocess.SubprocessError, FileNotFoundError):
            return "cmd"
    
    # Unix-like systems
    shell = os.environ.get("SHELL", "")
    if not shell:
        return "bash"  # Default to bash if SHELL is not set
    
    # Extract shell name from path
    return os.path.basename(shell)

def get_shell_activation_command(shell: str) -> str:
    """
    Get the appropriate activation command for the given shell.
    
    Args:
        shell: Shell name (bash, zsh, cmd, powershell)
    
    Returns:
        Shell-specific activation command
    """
    if shell == "powershell":
        return "& .\\Scripts\\Activate.ps1"
    elif shell == "cmd":
        return "Scripts\\activate.bat"
    else:  # bash, zsh, etc.
        return "source bin/activate" 