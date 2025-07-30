from setuptools import setup, find_packages
import os
import re
from datetime import datetime

# Read version from __init__.py
with open(os.path.join("mental_monitoring", "__init__.py"), "r", encoding="utf-8") as f:
    version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if version_match:
        version = version_match.group(1)
    else:
        version = "0.1.0"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get today's date for build tag
build_date = datetime.now().strftime("%Y%m%d")

setup(
    name="guardian-mental-health",
    version=version,  # Remove build date for PyPI
    author="Carlos Hernandez",
    author_email="scorpioon1008@ai-withcarlos.com",
    description="Mental health monitoring system using transformer models with PyTorch and CUDA acceleration",
    long_description=long_description,
    long_description_content_type="text/markdown",    url="https://github.com/scoorpion1008/Guardian",
    project_urls={
        "Bug Tracker": "https://github.com/scoorpion1008/Guardian/issues",
        "Documentation": "https://github.com/scoorpion1008/Guardian/wiki", 
        "Source Code": "https://github.com/scoorpion1008/Guardian",
        "PyPI": "https://pypi.org/project/guardian-mental-health/",
    },classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
        "Topic :: Text Processing :: Linguistic",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
    ],
    keywords="mental health, nlp, transformers, pytorch, discord, machine learning, bert",
    packages=find_packages(exclude=["tests", "examples", "*.log"]),
    include_package_data=False,
    python_requires=">=3.8",    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "torchaudio>=2.0.0",
        "transformers>=4.30.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "streamlit>=1.25.0",
        "plotly>=5.15.0",
        "matplotlib>=3.7.0",
        "discord.py>=2.3.0",
        "tqdm>=4.65.0",
        "requests>=2.30.0",
        "python-dotenv>=1.0.0",
        "ninja",  # For faster custom CUDA kernel compilation
        "accelerate>=0.20.0",  # For HuggingFace model acceleration
    ],    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "pylint>=2.17.0",
            "mypy>=1.4.0",
            "twine>=4.0.0",
            "build>=1.0.0",
            "wheel>=0.42.0",
        ],
        "optimize": [
            "onnx>=1.14.0",
            "onnxruntime-gpu>=1.16.0; platform_system!='Darwin'",
            "onnxruntime>=1.16.0; platform_system=='Darwin'",
        ],
        "rtx": [
            "onnx>=1.14.0",
            "onnxruntime-gpu>=1.16.0",
            "ninja>=1.10.0",
            "accelerate>=0.20.0",
        ],
        "deploy": [
            "gunicorn>=21.0.0",
            "uvicorn>=0.23.0",
            "fastapi>=0.100.0",
        ],
        "all": [
            "onnx>=1.14.0",
            "onnxruntime-gpu>=1.16.0; platform_system!='Darwin'",
            "onnxruntime>=1.16.0; platform_system=='Darwin'",
            "ninja>=1.10.0",
            "accelerate>=0.20.0",
            "gunicorn>=21.0.0",
            "uvicorn>=0.23.0",
            "fastapi>=0.100.0",
        ],
    },    entry_points={
        "console_scripts": [
            "guardian=mental_monitoring.main:main",
            "guardian-bot=mental_monitoring.main:run_discord_bot",
            "guardian-dash=mental_monitoring.main:run_dashboard",
            "guardian-optimize=mental_monitoring.utils.optimized_inference:main",
            "guardian-rtx=optimize_discord_bot:main",
            "guardian-benchmark=examples.batch_message_processing:main",
        ],
    },    package_data={
        "mental_monitoring": [
            "data/*.json",
            "config/*.py",
        ],
    },
    zip_safe=False,
)
