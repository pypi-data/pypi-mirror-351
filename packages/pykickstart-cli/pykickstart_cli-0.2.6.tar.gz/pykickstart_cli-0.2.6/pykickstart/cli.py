"""
Main CLI module for pykickstart.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, List
import json
import random

import click
import questionary
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns

from .venv_utils import create_venv, activate_venv, list_available_python_versions, get_existing_venvs
from .reqs_handler import handle_requirements, suggest_dev_tools
from .shell_utils import detect_shell
from .project_utils import setup_project_structure, get_project_templates, generate_demo_code
from .gemini_utils import generate_template_code

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler(".pykickstart.log")
    ]
)

logger = logging.getLogger("pykickstart")
console = Console()

# ASCII Art for different states
ASCII_ART = {
    "welcome": """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ██╗   ██╗██╗  ██╗██╗ ██████╗██╗  ██╗███████╗     ║
    ║  ██╔═══██╗╚██╗ ██╔╝██║ ██╔╝██║██╔════╝██║ ██╔╝██╔════╝     ║
    ║  ██║   ██║ ╚████╔╝ █████╔╝ ██║██║     █████╔╝ ███████╗     ║
    ║  ██║   ██║  ╚██╔╝  ██╔═██╗ ██║██║     ██╔═██╗ ╚════██║     ║
    ║  ╚██████╔╝   ██║   ██║  ██╗██║╚██████╗██║  ██╗███████║     ║
    ║   ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """,
    "success": """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗  ║
    ║   ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝  ║
    ║   ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗  ║
    ║   ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║  ║
    ║   ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║  ║
    ║   ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """,
    "error": """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ███████╗██████╗ ██████╗  ██████╗ ██████╗ ███████╗         ║
    ║   ██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝         ║
    ║   █████╗  ██████╔╝██████╔╝██║   ██║██████╔╝███████╗         ║
    ║   ██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗╚════██║         ║
    ║   ███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║███████║         ║
    ║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
}

def print_ascii_art(art_type: str):
    """Print ASCII art with color."""
    if art_type in ASCII_ART:
        style = {
            "welcome": "bold cyan",
            "success": "bold green",
            "error": "bold red"
        }.get(art_type, "bold white")
        console.print(ASCII_ART[art_type], style=style)

def print_header(title: str):
    """Print a beautiful header."""
    console.print("\n")
    print_ascii_art("welcome")
    title_text = Text(f"✨ {title} ✨", style="bold cyan")
    console.print(Panel(title_text, box=box.ROUNDED, border_style="cyan"))
    console.print("\n")

def print_success(message: str):
    """Print a success message."""
    console.print(f"✅ {message}", style="bold green")

def print_error(message: str):
    """Print an error message."""
    console.print(f"❌ {message}", style="bold red")

def print_info(message: str):
    """Print an info message."""
    console.print(f"ℹ️ {message}", style="bold blue")

def print_warning(message: str):
    """Print a warning message."""
    console.print(f"⚠️ {message}", style="bold yellow")

def print_completion():
    """Print completion message with ASCII art."""
    console.print("\n")
    print_ascii_art("success")
    console.print("\n")

def print_error_completion():
    """Print error completion message with ASCII art."""
    console.print("\n")
    print_ascii_art("error")
    console.print("\n")

def create_progress():
    """Create a beautiful progress bar."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        expand=True
    )

def print_table(title: str, columns: List[str], rows: List[List[str]], styles: Optional[List[str]] = None):
    """Print a beautiful table."""
    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style="cyan",
        title_style="bold cyan",
        header_style="bold green",
        expand=True
    )
    
    for i, col in enumerate(columns):
        style = styles[i] if styles and i < len(styles) else "white"
        table.add_column(col, style=style, justify="left")
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)
    console.print("\n")

def print_columns(items: List[str], title: str = None):
    """Print items in columns."""
    if title:
        console.print(Panel(title, style="bold cyan", box=box.ROUNDED))
    console.print(Columns(items, equal=True, expand=True))
    console.print("\n")

@click.group()
@click.version_option()
def cli():
    """Pykickstart - Python project environment setup automation tool."""
    pass

@cli.command()
def help_commands():
    """Display beautiful command reference and examples."""
    console.print("\n")
    
    # Title
    title = Text("✨ Pykickstart Command Reference ✨", style="bold cyan")
    console.print(Panel(title, box=box.ROUNDED, border_style="cyan"))
    console.print("\n")
    
    # Basic Commands
    console.print(Panel("📚 Basic Commands", style="bold green", box=box.ROUNDED))
    console.print("\n")
    
    # Initialize Project
    init_cmd = Syntax("""# Initialize a new project with web-app template
pykickstart init --template web-app

# Initialize with custom virtual environment name
pykickstart init --venv-name myenv --template cli-tool

# Initialize without Git
pykickstart init --no-git --template data-science

# Initialize with specific Python version
pykickstart init --python "Python 3.11.0" --template web-app""", "bash")
    console.print(Panel(init_cmd, title="🚀 Initialize Project", border_style="blue"))
    console.print("\n")
    
    # List Templates
    list_cmd = Syntax("""# List all available project templates
pykickstart list-templates""", "bash")
    console.print(Panel(list_cmd, title="📋 List Templates", border_style="blue"))
    console.print("\n")
    
    # Project Management
    console.print(Panel("🛠️ Project Management", style="bold green", box=box.ROUNDED))
    console.print("\n")
    
    # Requirements
    reqs_cmd = Syntax("""# Manage project requirements
pykickstart requirements""", "bash")
    console.print(Panel(reqs_cmd, title="📦 Requirements", border_style="blue"))
    console.print("\n")
    
    # Development Tools
    dev_cmd = Syntax("""# Install development tools
pykickstart dev-tools""", "bash")
    console.print(Panel(dev_cmd, title="🔧 Development Tools", border_style="blue"))
    console.print("\n")
    
    # Project Setup
    setup_cmd = Syntax("""# Set up project structure
pykickstart setup""", "bash")
    console.print(Panel(setup_cmd, title="🏗️ Project Setup", border_style="blue"))
    console.print("\n")
    
    # Documentation
    docs_cmd = Syntax("""# Set up project documentation
pykickstart docs""", "bash")
    console.print(Panel(docs_cmd, title="📚 Documentation", border_style="blue"))
    console.print("\n")
    
    # Code Quality
    quality_cmd = Syntax("""# Set up code quality tools
pykickstart code-quality""", "bash")
    console.print(Panel(quality_cmd, title="✨ Code Quality", border_style="blue"))
    console.print("\n")
    
    # Git Setup
    git_cmd = Syntax("""# Set up Git configuration and templates
pykickstart git-setup""", "bash")
    console.print(Panel(git_cmd, title="📝 Git Setup", border_style="blue"))
    console.print("\n")
    
    # VS Code Setup
    vscode_cmd = Syntax("""# Set up VS Code configuration
pykickstart vscode-setup""", "bash")
    console.print(Panel(vscode_cmd, title="💻 VS Code Setup", border_style="blue"))
    console.print("\n")
    
    # Footer
    footer = Text("For more information, visit: https://github.com/yourusername/pykickstart", style="dim")
    console.print(Panel(footer, box=box.ROUNDED, border_style="cyan"))
    console.print("\n")

@cli.command()
def list_templates():
    """List available project templates with their details."""
    print_header("Available Project Templates")
    
    templates = get_project_templates()
    
    columns = ["Template", "Name", "Description", "Dependencies"]
    styles = ["cyan", "green", "yellow", "blue"]
    rows = []
    
    for template_id, template in templates.items():
        deps = ", ".join(template["dependencies"])
        rows.append([
            f"📦 {template_id}",
            template["name"],
            template["description"],
            deps
        ])
    
    print_table("Project Templates", columns, rows, styles)

@cli.command()
@click.option("--venv-name", default=".venv", help="Name of the virtual environment directory")
@click.option("--python", default=None, help="Python interpreter to use")
@click.option("--no-git", is_flag=True, help="Skip Git initialization")
@click.option("--template", help="Project template to use")
@click.option("--gemini-key", envvar="GEMINI_API_KEY", help="Gemini API key for template generation")
def init(venv_name: str, python: Optional[str], no_git: bool, template: Optional[str], gemini_key: Optional[str]):
    """Initialize a new Python project environment."""
    try:
        print_header("Project Initialization")
        
        # If template is specified but no Gemini key is provided, ask for it
        if template and not gemini_key:
            gemini_key = questionary.text(
                "Please enter your Gemini API key for template generation:",
                password=True
            ).ask()
            
            if not gemini_key:
                print_error("Gemini API key is required for template generation.")
                return

        # Detect shell
        shell = detect_shell()
        print_info(f"Detected shell: {shell}")

        # Check for existing virtual environments
        existing_venvs = get_existing_venvs()
        if existing_venvs:
            venv_choice = questionary.select(
                "Found existing virtual environments. What would you like to do?",
                choices=[
                    "Use an existing virtual environment",
                    "Create a new virtual environment",
                    "Exit"
                ]
            ).ask()

            if venv_choice == "Exit":
                return
            elif venv_choice == "Use an existing virtual environment":
                venv_name = questionary.select(
                    "Select a virtual environment to use:",
                    choices=existing_venvs
                ).ask()
                venv_path = Path(venv_name)
                print_success(f"Using existing virtual environment: {venv_name}")
            else:
                # Get Python version
                python_versions = list_available_python_versions()
                if not python_versions:
                    print_error("No Python versions found. Please install Python first.")
                    return

                # Format versions for display
                version_choices = [
                    questionary.Choice(
                        f"{version} ({path})",
                        value=path
                    )
                    for version, path in python_versions
                ]

                python = questionary.select(
                    "Select Python version to use:",
                    choices=version_choices
                ).ask()

                # Create new virtual environment
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Creating virtual environment...", total=None)
                    try:
                        venv_path = create_venv(venv_name, python)
                        progress.update(task, completed=True)
                        print_success(f"Created virtual environment at {venv_path}")
                    except Exception as e:
                        print_error(f"Failed to create virtual environment: {str(e)}")
                        return
        else:
            # Get Python version
            python_versions = list_available_python_versions()
            if not python_versions:
                print_error("No Python versions found. Please install Python first.")
                return

            # Format versions for display
            version_choices = [
                questionary.Choice(
                    f"{version} ({path})",
                    value=path
                )
                for version, path in python_versions
            ]

            python = questionary.select(
                "Select Python version to use:",
                choices=version_choices
            ).ask()

            # Create new virtual environment
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating virtual environment...", total=None)
                try:
                    venv_path = create_venv(venv_name, python)
                    progress.update(task, completed=True)
                    print_success(f"Created virtual environment at {venv_path}")
                except Exception as e:
                    print_error(f"Failed to create virtual environment: {str(e)}")
                    return

        # Activate virtual environment
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Activating virtual environment...", total=None)
            try:
                activate_venv(venv_path, shell)
                progress.update(task, completed=True)
                print_success("Virtual environment activated")
            except Exception as e:
                print_error(f"Failed to activate virtual environment: {str(e)}")
                return

        # Select project template if not provided
        if not template:
            templates = get_project_templates()
            template_choice = questionary.select(
                "Select a project template:",
                choices=[
                    questionary.Choice(
                        f"{t['name']} - {t['description']}",
                        value=name
                    )
                    for name, t in templates.items()
                ] + ["Custom (no template)"]
            ).ask()
            
            if template_choice != "Custom (no template)":
                template = template_choice

        # Setup project structure with template
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up project structure...", total=None)
            setup_project_structure(template)
            progress.update(task, completed=True)
            print_success("Project structure created")

        # Generate template code if template is selected and Gemini key is provided
        if template and gemini_key:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Generating template code...", total=None)
                try:
                    logger.info(f"Generating template for type: {template}")
                    logger.info("Using Gemini API key: %s", "*" * len(gemini_key))
                    
                    template_files = generate_template_code(template, gemini_key)
                    logger.info(f"Generated {len(template_files)} files")
                    
                    for file_path, content in template_files.items():
                        file_path = Path(file_path)
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        logger.info(f"Created file: {file_path}")
                    
                    progress.update(task, completed=True)
                    print_success("Template code generated")
                except Exception as e:
                    logger.error(f"Template generation failed: {str(e)}", exc_info=True)
                    print_error(f"Failed to generate template code: {str(e)}")
                    return

        # Install requirements if requirements.txt exists
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Installing project dependencies...", total=None)
                try:
                    # Use the Python from the virtual environment
                    if os.name == "nt":  # Windows
                        pip_path = venv_path / "Scripts" / "pip.exe"
                    else:  # Unix-like
                        pip_path = venv_path / "bin" / "pip"
                    
                    subprocess.run(
                        [str(pip_path), "install", "-r", "requirements.txt"],
                        check=True
                    )
                    progress.update(task, completed=True)
                    print_success("Project dependencies installed")
                except subprocess.SubprocessError as e:
                    print_error(f"Failed to install dependencies: {str(e)}")
                    return

        # Initialize Git repository
        if not no_git and questionary.confirm("Would you like to initialize a Git repository?").ask():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Initializing Git repository...", total=None)
                subprocess.run(["git", "init"], check=True)
                progress.update(task, completed=True)
                print_success("Git repository initialized")

        print_completion()
        print_success("Your project is ready to code!")
        print_info("Next steps:")
        print_info("1. Your virtual environment is already activated")
        print_info("2. Dependencies are already installed")
        print_info("3. Start coding!")

    except Exception as e:
        print_error_completion()
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def requirements():
    """Manage project requirements."""
    try:
        print_header("Project Requirements")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Managing project requirements...", total=None)
            handle_requirements()
            progress.update(task, completed=True)
            print_success("Project requirements updated")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def dev_tools():
    """Install development tools."""
    try:
        print_header("Development Tools")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Installing development tools...", total=None)
            suggest_dev_tools()
            progress.update(task, completed=True)
            print_success("Development tools installed")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def setup():
    """Set up project structure."""
    try:
        print_header("Project Setup")
        
        templates = get_project_templates()
        template_choice = questionary.select(
            "Select a project template:",
            choices=[
                questionary.Choice(
                    f"{t['name']} - {t['description']}",
                    value=name
                )
                for name, t in templates.items()
            ] + ["Custom (no template)"]
        ).ask()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up project structure...", total=None)
            if template_choice != "Custom (no template)":
                setup_project_structure(template_choice)
            else:
                setup_project_structure()
            progress.update(task, completed=True)
            print_success("Project structure created")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def docs():
    """Set up project documentation."""
    try:
        print_header("Project Documentation")
        
        templates = get_project_templates()
        template_choice = questionary.select(
            "Select a project template for documentation:",
            choices=[
                questionary.Choice(
                    f"{t['name']} - {t['description']}",
                    value=name
                )
                for name, t in templates.items()
            ] + ["Custom (no template)"]
        ).ask()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up documentation...", total=None)
            if template_choice != "Custom (no template)":
                setup_project_structure(template_choice)
            progress.update(task, completed=True)
            print_success("Documentation structure created")
            print_info("To build the documentation, run:")
            print_info("cd docs && make html")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def code_quality():
    """Set up code quality tools and configurations."""
    try:
        print_header("Code Quality Setup")
        
        # Install code quality tools
        tools = {
            "black": "Code formatter",
            "flake8": "Linter",
            "mypy": "Static type checker",
            "isort": "Import sorter",
            "pre-commit": "Git hooks manager"
        }
        
        choices = questionary.checkbox(
            "Select code quality tools to install:",
            choices=[f"{tool} - {desc}" for tool, desc in tools.items()]
        ).ask()
        
        if choices:
            tools_to_install = [choice.split(" - ")[0] for choice in choices]
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Installing code quality tools...", total=None)
                subprocess.run([sys.executable, "-m", "pip", "install"] + tools_to_install, check=True)
                progress.update(task, completed=True)
                print_success("Code quality tools installed")
            
            # Create configuration files
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating configuration files...", total=None)
                
                if "black" in tools_to_install:
                    with open("pyproject.toml", "w") as f:
                        f.write("""[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
""")
                
                if "flake8" in tools_to_install:
                    with open(".flake8", "w") as f:
                        f.write("""[flake8]
max-line-length = 88
extend-ignore = E203
""")
                
                if "mypy" in tools_to_install:
                    with open("mypy.ini", "w") as f:
                        f.write("""[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
""")
                
                if "isort" in tools_to_install:
                    with open(".isort.cfg", "w") as f:
                        f.write("""[settings]
profile = black
multi_line_output = 3
""")
                
                if "pre-commit" in tools_to_install:
                    with open(".pre-commit-config.yaml", "w") as f:
                        f.write("""repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
""")
                    
                    # Initialize pre-commit
                    subprocess.run(["pre-commit", "install"], check=True)
                
                progress.update(task, completed=True)
                print_success("Configuration files created")
            
            print_success("Code quality setup complete")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def git_setup():
    """Set up Git configuration and templates."""
    try:
        print_header("Git Setup")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up Git configuration...", total=None)
            
            # Create Git templates
            templates_dir = Path(".git-templates")
            templates_dir.mkdir(exist_ok=True)
            
            # Create issue template
            issue_template = """---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10]
 - Python version: [e.g. 3.8.0]
 - Package version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
"""
            with open(templates_dir / "ISSUE_TEMPLATE.md", "w") as f:
                f.write(issue_template)
            
            # Create PR template
            pr_template = """## Description
Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context.

Fixes # (issue)

## Type of change
Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How Has This Been Tested?
Please describe the tests that you ran to verify your changes.

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
"""
            with open(templates_dir / "PULL_REQUEST_TEMPLATE.md", "w") as f:
                f.write(pr_template)
            
            # Create .gitignore
            gitignore_content = """# Python
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
"""
            with open(".gitignore", "w") as f:
                f.write(gitignore_content)
            
            # Initialize Git if not already initialized
            if not Path(".git").exists():
                subprocess.run(["git", "init"], check=True)
            
            # Configure Git
            subprocess.run(["git", "config", "--local", "init.templateDir", str(templates_dir)], check=True)
            
            progress.update(task, completed=True)
            print_success("Git configuration complete")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def vscode_setup():
    """Set up VS Code configuration."""
    try:
        print_header("VS Code Setup")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up VS Code configuration...", total=None)
            
            # Create .vscode directory
            vscode_dir = Path(".vscode")
            vscode_dir.mkdir(exist_ok=True)
            
            # Create settings.json
            settings = {
                "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe" if os.name == "nt" else "${workspaceFolder}/.venv/bin/python",
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True,
                "python.formatting.provider": "black",
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True
                },
                "python.testing.pytestEnabled": True,
                "python.testing.unittestEnabled": False,
                "python.testing.nosetestsEnabled": False,
                "python.testing.pytestArgs": [
                    "tests"
                ]
            }
            
            with open(vscode_dir / "settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            
            # Create launch.json
            launch = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Python: Current File",
                        "type": "python",
                        "request": "launch",
                        "program": "${file}",
                        "console": "integratedTerminal",
                        "justMyCode": True
                    },
                    {
                        "name": "Python: Debug Tests",
                        "type": "python",
                        "request": "launch",
                        "program": "${file}",
                        "purpose": ["debug-test"],
                        "console": "integratedTerminal",
                        "justMyCode": False
                    }
                ]
            }
            
            with open(vscode_dir / "launch.json", "w") as f:
                json.dump(launch, f, indent=4)
            
            progress.update(task, completed=True)
            print_success("VS Code configuration complete")
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def activate():
    """Activate a virtual environment."""
    try:
        # Get list of existing virtual environments
        venvs = get_existing_venvs()
        if not venvs:
            print_error("No virtual environments found in the current directory.")
            return

        # Let user select which virtual environment to activate
        venv_name = questionary.select(
            "Select a virtual environment to activate:",
            choices=venvs
        ).ask()

        # Activate the selected virtual environment
        venv_path = Path(venv_name)
        shell = detect_shell()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Activating virtual environment...", total=None)
            try:
                activate_venv(venv_path, shell)
                progress.update(task, completed=True)
                print_success(f"Virtual environment '{venv_name}' activated")
                
                # Print instructions for the user
                print_info("\nTo see the virtual environment indicator in your prompt, you need to:")
                if os.name == "nt":  # Windows
                    print_info("1. Close and reopen your terminal")
                    print_info("2. Or run: $env:PROMPT = \"(.venv) $P$G\"")
                else:  # Unix-like
                    print_info("1. Close and reopen your terminal")
                    print_info("2. Or run: export PS1=\"(.venv) $PS1\"")
                
            except Exception as e:
                print_error(f"Failed to activate virtual environment: {str(e)}")
                return

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

@cli.command()
def deactivate():
    """Deactivate the current virtual environment."""
    try:
        if "VIRTUAL_ENV" not in os.environ:
            print_error("No virtual environment is currently active.")
            return

        # Get the current virtual environment path
        venv_path = Path(os.environ["VIRTUAL_ENV"])
        
        # Remove virtual environment from PATH
        if os.name == "nt":  # Windows
            os.environ["PATH"] = os.environ["PATH"].replace(f"{venv_path}\\Scripts;", "")
        else:  # Unix-like
            os.environ["PATH"] = os.environ["PATH"].replace(f"{venv_path}/bin:", "")
        
        # Remove VIRTUAL_ENV from environment
        del os.environ["VIRTUAL_ENV"]
        
        print_success(f"Virtual environment '{venv_path.name}' deactivated")

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

def main():
    """Entry point for the CLI."""
    cli() 