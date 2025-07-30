# PyKickstart 🚀

A powerful CLI tool that automates Python project environment setup for developers.

## Features

- 🔧 Automatic virtual environment creation and activation
- 📦 Smart dependency management
- 🤖 AI-powered package inference
- 🎨 Beautiful CLI interface
- 🛠️ Optional project structure generation
- 🔍 Unused dependency detection
- 💡 Developer tool suggestions

## Installation

```bash
pip install pykickstart
```

## Configuration

### Google Gemini API Key

For AI-powered package inference, you'll need a Google Gemini API key:

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the API key in one of these ways:
   ```bash
   # Option 1: Environment variable
   export GOOGLE_API_KEY="your-api-key-here"  # Unix/Linux/macOS
   set GOOGLE_API_KEY=your-api-key-here       # Windows CMD
   $env:GOOGLE_API_KEY="your-api-key-here"    # Windows PowerShell

   # Option 2: Create a .env file in your project root
   echo "GOOGLE_API_KEY=your-api-key-here" > .env
   ```

## Usage

```bash
# Run as a module
python -m pykickstart

# Or use the CLI command
pykickstart
```

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Publishing

To publish this package to PyPI:

1. Install build tools:
   ```bash
   pip install build twine
   ```

2. Build the package:
   ```bash
   python -m build
   ```

3. Upload to PyPI:
   ```bash
   # Test upload to TestPyPI first
   python -m twine upload --repository testpypi dist/*

   # Upload to real PyPI
   python -m twine upload dist/*
   ```

## License

MIT License - feel free to use this project for any purpose. 