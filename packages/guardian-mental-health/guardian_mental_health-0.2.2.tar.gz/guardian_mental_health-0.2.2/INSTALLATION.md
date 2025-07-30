# Guardian Installation Guide

This guide explains how to install the Guardian mental health monitoring system for both development and production use.

## Prerequisites

Before installation, ensure you have:

- Python 3.8 or higher
- pip (package installer for Python)
- Git (optional, for cloning the repository)
- A CUDA-capable GPU (recommended for training, optional for inference)

## Installation Methods

### Method 1: Development Installation

For contributors and developers who want to modify the code, install in development mode:

1. **Clone the repository** (if using Git):
   ```bash
   git clone https://github.com/yourusername/guardian.git
   cd guardian
   ```

   Or **download and extract** the source code.

2. **Create a virtual environment** (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

   This installs the package in "editable" mode, meaning changes to the source code will immediately affect the installed package without needing to reinstall.

### Method 2: Direct Installation

For users who just want to use the package without modifying it:

1. **Install directly from the source directory**:
   ```bash
   pip install .
   ```

   This installs the package in standard mode.

### Method 3: Install from PyPI

Once the package is published to PyPI, you can install it with:

```bash
pip install guardian-mental-health
```

## Verifying the Installation

After installation, verify that Guardian is correctly installed:

```bash
python -c "import mental_monitoring; print(mental_monitoring.__version__)"
```

This should print the version number without errors.

## Installing Optional Dependencies

### CUDA Support (for GPU acceleration)

To enable GPU support for faster model training and inference:

```bash
pip install torch --extra-index-url https://download.pytorch.org/whl/cu118
```

Replace `cu118` with the appropriate CUDA version for your system.

### Development Tools

If you're contributing to Guardian, install development dependencies:

```bash
pip install -r requirements-dev.txt
```

## What Happens During Installation

When you run `pip install -e .` or `pip install .`, the following occurs:

1. **setuptools** reads the `setup.py` file to determine metadata and dependencies
2. The required dependencies listed in `setup.py` are installed
3. The package is either:
   - Linked to your source directory (with `-e`)
   - Copied to your Python's site-packages directory (without `-e`)
4. Entry points are created (the `guardian` command)

## Troubleshooting

### Common Issues

#### Missing Dependencies
```
ImportError: No module named 'some_module'
```

Solution: Install the missing dependency:
```bash
pip install some_module
```

#### CUDA Issues
```
RuntimeError: CUDA error: no CUDA-capable device is detected
```

Solution: Ensure your CUDA drivers are installed and up to date, or use CPU mode.

#### Permission Errors
```
PermissionError: [Errno 13] Permission denied
```

Solution: Use `--user` flag (non-development install) or fix directory permissions.

## Uninstalling

To uninstall Guardian:

```bash
pip uninstall guardian-mental-health
```

## Updating

For a development installation, pull the latest changes and the package will automatically update:

```bash
git pull
```

For standard installations, reinstall the package:

```bash
pip install . --upgrade
```

Or from PyPI:

```bash
pip install guardian-mental-health --upgrade
```
