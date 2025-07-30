"""
Project structure and template utilities.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
import google.generativeai as genai
from rich.console import Console

console = Console()

def get_project_templates() -> Dict[str, Dict]:
    """
    Get available project templates.
    
    Returns:
        Dictionary of template configurations
    """
    return {
        "web-app": {
            "name": "Web Application",
            "description": "A modern web application using FastAPI/Flask",
            "dependencies": [
                "fastapi",
                "uvicorn",
                "sqlalchemy",
                "pydantic",
                "python-dotenv"
            ],
            "dev_dependencies": [
                "pytest",
                "black",
                "flake8",
                "mypy"
            ]
        },
        "cli-tool": {
            "name": "CLI Tool",
            "description": "A command-line interface tool",
            "dependencies": [
                "click",
                "rich",
                "typer",
                "python-dotenv"
            ],
            "dev_dependencies": [
                "pytest",
                "black",
                "flake8",
                "mypy"
            ]
        },
        "data-science": {
            "name": "Data Science Project",
            "description": "A data science project with Jupyter notebooks",
            "dependencies": [
                "numpy",
                "pandas",
                "matplotlib",
                "scikit-learn",
                "jupyter"
            ],
            "dev_dependencies": [
                "pytest",
                "black",
                "flake8",
                "mypy"
            ]
        },
        "api-service": {
            "name": "REST API Service",
            "description": "A RESTful API service with authentication",
            "dependencies": [
                "fastapi",
                "uvicorn",
                "sqlalchemy",
                "pydantic",
                "python-jose",
                "passlib",
                "python-multipart"
            ],
            "dev_dependencies": [
                "pytest",
                "black",
                "flake8",
                "mypy"
            ]
        },
        "bot": {
            "name": "Discord/Telegram Bot",
            "description": "A Discord or Telegram bot",
            "dependencies": [
                "discord.py",
                "python-telegram-bot",
                "python-dotenv"
            ],
            "dev_dependencies": [
                "pytest",
                "black",
                "flake8",
                "mypy"
            ]
        },
        "game": {
            "name": "Simple Game",
            "description": "A simple game using Pygame",
            "dependencies": [
                "pygame",
                "numpy"
            ],
            "dev_dependencies": [
                "pytest",
                "black",
                "flake8"
            ]
        }
    }

def generate_demo_code(template: str, api_key: str) -> Dict[str, str]:
    """
    Generate demo code for the selected template using Gemini.
    
    Args:
        template: Template identifier
        api_key: Gemini API key
    
    Returns:
        Dictionary of file paths and their contents
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        templates = get_project_templates()
        if template not in templates:
            raise ValueError(f"Unknown template: {template}")
        
        template_info = templates[template]
        prompt = f"""Generate a complete demo project for a {template_info['name']} using Python.
        The project should demonstrate best practices and include:
        1. Main application code
        2. Configuration files
        3. README with setup instructions
        4. Example usage
        
        Template details:
        - Name: {template_info['name']}
        - Description: {template_info['description']}
        - Dependencies: {', '.join(template_info['dependencies'])}
        
        Please provide the code in a structured format with file paths and contents.
        """
        
        response = model.generate_content(prompt)
        return parse_gemini_response(response.text)
    except Exception as e:
        console.print(f"Error generating demo code: {str(e)}", style="bold red")
        return {}

def parse_gemini_response(response: str) -> Dict[str, str]:
    """
    Parse Gemini response into file contents.
    
    Args:
        response: Raw response from Gemini
    
    Returns:
        Dictionary of file paths and their contents
    """
    files = {}
    current_file = None
    current_content = []
    
    for line in response.split('\n'):
        if line.startswith('```') and ':' in line:
            if current_file:
                files[current_file] = '\n'.join(current_content)
            current_file = line.split(':')[1].strip()
            current_content = []
        elif current_file and not line.startswith('```'):
            current_content.append(line)
    
    if current_file:
        files[current_file] = '\n'.join(current_content)
    
    return files

def setup_project_structure(template: Optional[str] = None) -> None:
    """
    Set up project structure based on template.
    
    Args:
        template: Template identifier (optional)
    """
    # Create basic directory structure
    directories = [
        "src",
        "tests",
        "docs",
        ".github/workflows"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Create basic files
    with open("README.md", "w") as f:
        f.write("# Python Project\n\nA Python project created with pykickstart.\n")
    
    with open(".gitignore", "w") as f:
        f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/

# Logs
*.log

# Jupyter Notebook
.ipynb_checkpoints
""")
    
    # Create template-specific structure
    if template:
        templates = get_project_templates()
        if template in templates:
            template_info = templates[template]
            
            # Create requirements.txt
            with open("requirements.txt", "w") as f:
                f.write("\n".join(template_info["dependencies"]))
            
            # Create dev-requirements.txt
            with open("dev-requirements.txt", "w") as f:
                f.write("\n".join(template_info["dev_dependencies"]))
            
            # Create basic source files
            src_dir = Path("src")
            src_dir.mkdir(exist_ok=True)
            
            with open(src_dir / "__init__.py", "w") as f:
                f.write('"""Project package."""\n')
            
            # Create template-specific files
            if template == "web-app":
                with open(src_dir / "main.py", "w") as f:
                    f.write('"""Main application module."""\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\ndef read_root():\n    return {"Hello": "World"}\n')
            elif template == "cli-tool":
                with open(src_dir / "cli.py", "w") as f:
                    f.write('"""Command-line interface module."""\n\nimport click\n\n@click.group()\ndef cli():\n    """CLI tool."""\n    pass\n\n@cli.command()\ndef hello():\n    """Say hello."""\n    click.echo("Hello, World!")\n\nif __name__ == "__main__":\n    cli()\n')
            elif template == "data-science":
                with open("notebooks/example.ipynb", "w") as f:
                    f.write('{"cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Example Notebook"]}], "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 4}')
            
            # Create GitHub Actions workflow
            workflow_dir = Path(".github/workflows")
            workflow_dir.mkdir(parents=True, exist_ok=True)
            
            with open(workflow_dir / "ci.yml", "w") as f:
                f.write("""name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r dev-requirements.txt
    - name: Run tests
      run: |
        pytest
""") 