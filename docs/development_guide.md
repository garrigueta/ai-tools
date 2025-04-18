# AI-Tools Development Guide

This guide is intended for developers who want to contribute to the ai-tools project.

## Project Structure

The project is organized as a Python package:

```
src/                 # Source code directory
  ai_tools/          # Main package
    __init__.py      # Package initialization
    __main__.py      # Entry point for running as a module
    main.py          # Main application logic
    backend/         # Backend services
    chat/            # Chat interface implementations
    config/          # Configuration management
    mcp/             # Model Context Protocol components
      actions.py     # Command execution and LLM interaction
    modules/         # Utility modules
      audio.py       # Audio processing functions
      msfs.py        # Microsoft Flight Simulator integration
      sim.py         # Simulation support functions
      speech.py      # Text-to-speech functionality
    storage/         # Knowledge storage and document loading
      docs.py        # Document vectorization and retrieval
```

## Development Setup

### Option 1: Install using Poetry (recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/garrigueta/ai-tools.git
   cd ai-tools
   ```

2. Install with Poetry:
   ```bash
   # Install Poetry if you don't have it
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install the package
   poetry install
   
   # Activate the Poetry environment
   poetry shell
   ```

### Option 2: Install as a development package

1. Clone the repository:
   ```bash
   git clone https://github.com/garrigueta/ai-tools.git
   cd ai-tools
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

## Testing

To run the test suite and verify that everything is working correctly:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=ai_tools

# Run a specific test file
pytest tests/unit/modules/test_sim.py
```

The project includes comprehensive unit tests for all major components. If you're contributing new features, please add appropriate tests to maintain code quality.

## Building Binary Packages

To build standalone binary packages (which don't require Python to be installed):

```bash
# Build for the current platform
python build_binary.py

# Or specify a target platform 
python build_binary.py --platform=linux
python build_binary.py --platform=win
python build_binary.py --platform=macos
```

For more details about binary packages, see the [Binary Installation](binary_installation.md) guide.

## Contributing Guidelines

Contributions are welcome! To contribute to ai-tools:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests to ensure everything works (`pytest`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure your code follows the project's coding style and includes appropriate tests.

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for all public functions and classes
- Keep functions focused on a single responsibility
- Add type hints where appropriate

### Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate
2. Update the version number in relevant files
3. The pull request will be merged once it has been reviewed and approved
4. Make sure all tests pass before submitting your pull request

## Adding New Features

When adding new features to ai-tools:

1. Consider how the feature fits into the existing architecture
2. Add appropriate tests for your feature
3. Update documentation to reflect new capabilities
4. Ensure the feature works across all supported platforms (Linux, macOS, WSL)

### Adding New Shell Commands

To add a new command to the ai-tools CLI:

1. Add a new method to handle your command in `main.py`
2. Register the command with appropriate arguments in the argument parser
3. Implement the core functionality in the appropriate module
4. Add tests for the new command
5. Update documentation with examples of using your command

### Adding New Game Support

To add support for a new game to the simulation assistant:

1. Create a new module for your game in `modules/`
2. Implement the required interfaces for data collection and state tracking
3. Add appropriate tests for your game module
4. Update documentation to include your new game in the supported list

## Release Process

The release process for ai-tools involves:

1. Ensuring all tests pass
2. Updating the version number
3. Creating a new release in GitHub with appropriate tags
4. Building binary distributions for all platforms
5. Updating documentation

## Troubleshooting Development Issues

If you encounter issues during development:

1. Check that you're using the right Python version (3.10+)
2. Ensure all dependencies are correctly installed
3. Look at the test output for clues
4. Check the issue tracker to see if your problem has already been reported

For more specific troubleshooting information, see the [Installation Guide](installation_guide.md).