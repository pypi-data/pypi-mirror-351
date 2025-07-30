"""
Requirements management utilities.
"""

import os
import sys
import subprocess
from pathlib import Path
import google.generativeai as genai
from rich.console import Console
import questionary

console = Console()

def handle_requirements() -> None:
    """
    Handle project requirements:
    1. Check for existing requirements.txt
    2. If not found, ask user if they want to create one
    3. If yes, use Gemini to generate requirements.txt
    4. Install dependencies if requirements.txt exists
    """
    if os.path.exists("requirements.txt"):
        console.print("📦 Found requirements.txt, installing dependencies...", style="bold blue")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        return

    # Check if there are any Python files
    python_files = list(Path(".").rglob("*.py"))
    if not python_files:
        console.print("\n✨ [bold green]No Python files found in the project[/bold green]")
        console.print("🚀 [bold blue]Your environment is ready! Start coding your Python project.[/bold blue]\n")
        return

    # Ask user if they want to create requirements.txt
    create_reqs = questionary.confirm(
        "Would you like to create a requirements.txt file?",
        default=False
    ).ask()

    if create_reqs:
        console.print("\n🔍 [bold blue]Analyzing your Python files...[/bold blue]")
        
        # Ask for Gemini API key
        use_ai = questionary.confirm(
            "Would you like to use AI to analyze your Python files? (Requires Google Gemini API key)",
            default=False
        ).ask()
        
        if use_ai:
            api_key = questionary.password(
                "Please enter your Google Gemini API key:",
                validate=lambda text: len(text) > 0 or "API key cannot be empty"
            ).ask()
            
            if not api_key:
                console.print("⚠️ [bold yellow]No API key provided. Skipping AI analysis.[/bold yellow]")
                console.print("🚀 [bold blue]Your environment is ready! Start coding your Python project.[/bold blue]\n")
                return
                
            try:
                generate_requirements_with_ai(api_key)
            except Exception as e:
                console.print(f"⚠️ [bold red]Error during AI analysis: {str(e)}[/bold red]")
                console.print("🚀 [bold blue]Your environment is ready! Start coding your Python project.[/bold blue]\n")
                return
        else:
            console.print("\n✨ [bold green]Skipping AI analysis[/bold green]")
            console.print("🚀 [bold blue]Your environment is ready! Start coding your Python project.[/bold blue]\n")
            return
        
        if os.path.exists("requirements.txt"):
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
                console.print("✅ [bold green]Dependencies installed successfully[/bold green]")
            except subprocess.SubprocessError as e:
                console.print(f"⚠️ [bold red]Error installing dependencies: {str(e)}[/bold red]")
                console.print("Please check your requirements.txt file and try installing manually.")
    else:
        console.print("\n✨ [bold green]No requirements.txt will be created[/bold green]")
        console.print("🚀 [bold blue]Your environment is ready! Start coding your Python project.[/bold blue]\n")

def generate_requirements_with_ai(api_key: str) -> None:
    """
    Use Google's Gemini AI to analyze Python files and generate requirements.txt.
    
    Args:
        api_key: Google Gemini API key
    """
    try:
        # Initialize Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Collect all Python files
        python_files = list(Path(".").rglob("*.py"))
        if not python_files:
            console.print("⚠️ [bold yellow]No Python files found in the project[/bold yellow]")
            return

        # Read and analyze Python files
        imports = set()
        for file in python_files:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # Use Gemini to analyze imports
                response = model.generate_content(
                    f"Analyze this Python code and list all external package imports (excluding standard library):\n\n{content}"
                )
                if response.text:
                    imports.update(response.text.strip().split("\n"))

        # Write requirements.txt
        with open("requirements.txt", "w", encoding="utf-8") as f:
            for imp in sorted(imports):
                f.write(f"{imp}\n")

        console.print("✨ [bold green]Generated requirements.txt using AI analysis[/bold green]")
        
    except Exception as e:
        console.print(f"⚠️ [bold red]Error during AI analysis: {str(e)}[/bold red]")
        raise

def suggest_dev_tools() -> None:
    """
    Suggest and optionally install common development tools.
    """
    dev_tools = {
        "black": "Code formatter",
        "flake8": "Linter",
        "pytest": "Testing framework",
        "mypy": "Static type checker",
        "isort": "Import sorter"
    }

    choices = questionary.checkbox(
        "Would you like to install any of these development tools?",
        choices=[f"{tool} - {desc}" for tool, desc in dev_tools.items()]
    ).ask()

    if choices:
        tools = [choice.split(" - ")[0] for choice in choices]
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + tools, check=True)
            console.print("✅ [bold green]Development tools installed successfully[/bold green]")
        except subprocess.SubprocessError as e:
            console.print(f"⚠️ [bold red]Error installing development tools: {str(e)}[/bold red]")
            console.print("Please try installing the tools manually.") 