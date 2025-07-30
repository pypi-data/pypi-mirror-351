# Contributing to Guardian

Thank you for your interest in contributing to Guardian! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

## How to Contribute

### Reporting Issues

- Check if the issue has already been reported
- Use the issue template to provide all necessary information
- Include clear steps to reproduce the issue
- Add screenshots if applicable

### Submitting Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Add or update tests as necessary
5. Run the test suite to ensure all tests pass
6. Submit a pull request

### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the documentation
3. The PR should work on all supported Python versions
4. The PR will be merged once it receives approval from maintainers

## Development Setup

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/guardian.git
cd guardian

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest
```

### Code Style

We use PEP 8 and Black for code formatting. Make sure your code follows these guidelines.

```bash
# Format your code
black mental_monitoring/

# Check for lint errors
flake8 mental_monitoring/
```

## Project Structure

```
mental_monitoring/
├── models/               # ML models
├── data/                 # Dataset files
├── discord_bot/          # Discord integration
├── dashboard/            # Streamlit dashboard
├── utils/                # Helper utilities
├── config.py             # Configuration
└── main.py               # Main entry point
```

## Feature Requests

If you have ideas for new features, please open an issue with the tag "enhancement".

## Documentation

All code should be properly documented with docstrings. Follow the Google Python Style Guide for docstrings.

## License

By contributing to Guardian, you agree that your contributions will be licensed under the project's MIT license.
