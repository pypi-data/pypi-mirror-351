"""
Virtual environment management utilities.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

def list_available_python_versions() -> List[Tuple[str, str]]:
    """
    List all available Python versions on the system.
    
    Returns:
        List of tuples containing (version string, python path)
    """
    versions = []
    
    # Check common Python installation paths
    if os.name == "nt":  # Windows
        # Check Python in Program Files
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        python_dirs = [
            program_files,
            os.path.join(program_files, "Python*"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python")
        ]
        
        for base_dir in python_dirs:
            try:
                for path in Path(base_dir).glob("Python*"):
                    if path.is_dir():
                        python_exe = path / "python.exe"
                        if python_exe.exists():
                            try:
                                result = subprocess.run(
                                    [str(python_exe), "--version"],
                                    capture_output=True,
                                    text=True,
                                    check=True
                                )
                                versions.append((result.stdout.strip(), str(python_exe)))
                            except subprocess.SubprocessError:
                                continue
            except Exception:
                continue
    else:  # Unix-like
        # Check common Python paths
        python_paths = [
            "/usr/bin/python*",
            "/usr/local/bin/python*",
            os.path.expanduser("~/.local/bin/python*")
        ]
        
        for pattern in python_paths:
            try:
                for path in Path("/").glob(pattern.lstrip("/")):
                    if path.is_file() and os.access(path, os.X_OK):
                        try:
                            result = subprocess.run(
                                [str(path), "--version"],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            versions.append((result.stdout.strip(), str(path)))
                        except subprocess.SubprocessError:
                            continue
            except Exception:
                continue
    
    return sorted(list(set(versions)))

def get_existing_venvs() -> List[str]:
    """
    Find existing virtual environments in the current directory.
    
    Returns:
        List of virtual environment directory names
    """
    venv_dirs = []
    
    # Common virtual environment directory names
    venv_names = [".venv", "venv", "env", ".env"]
    
    for name in venv_names:
        venv_path = Path(name)
        if venv_path.exists() and venv_path.is_dir():
            # Verify it's a virtual environment by checking for activation script
            if os.name == "nt":  # Windows
                activate_script = venv_path / "Scripts" / "activate.bat"
            else:  # Unix-like
                activate_script = venv_path / "bin" / "activate"
            
            if activate_script.exists():
                venv_dirs.append(name)
    
    return venv_dirs

def create_venv(venv_name: str, python: Optional[str] = None) -> Path:
    """
    Create a new virtual environment.
    
    Args:
        venv_name: Name of the virtual environment directory
        python: Python interpreter to use (optional)
    
    Returns:
        Path to the created virtual environment
    """
    venv_path = Path(venv_name)
    
    if venv_path.exists():
        raise FileExistsError(f"Virtual environment directory {venv_name} already exists")
    
    # Extract Python path if it's in the format "version (path)"
    if python and "(" in python and ")" in python:
        python = python.split("(")[1].rstrip(")")
    
    cmd = [python if python else sys.executable, "-m", "venv", str(venv_path)]
    
    try:
        subprocess.run(cmd, check=True)
        return venv_path
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to create virtual environment: {str(e)}")

def activate_venv(venv_path: Path, shell: str) -> None:
    """
    Activate the virtual environment in the current shell.
    
    Args:
        venv_path: Path to the virtual environment
        shell: Shell type (bash, zsh, etc.)
    """
    if os.name == "nt":  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        if not activate_script.exists():
            raise FileNotFoundError(f"Activation script not found at {activate_script}")
        
        # On Windows, we need to modify the current process environment
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        os.environ["PATH"] = f"{venv_path}\\Scripts;{os.environ['PATH']}"
        
        # Set the prompt to show the virtual environment name
        venv_name = venv_path.name
        os.environ["PROMPT"] = f"({venv_name}) $P$G"
        
    else:  # Unix-like
        activate_script = venv_path / "bin" / "activate"
        if not activate_script.exists():
            raise FileNotFoundError(f"Activation script not found at {activate_script}")
        
        # Source the activation script
        subprocess.run(f"source {activate_script}", shell=True, check=True)
        
        # Set the prompt to show the virtual environment name
        venv_name = venv_path.name
        os.environ["PS1"] = f"({venv_name}) $PS1" 