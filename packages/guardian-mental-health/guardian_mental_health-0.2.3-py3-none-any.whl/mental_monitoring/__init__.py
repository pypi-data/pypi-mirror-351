"""
Guardian - Mental Health Monitoring System
=========================================

A mental health monitoring system using transformer models with PyTorch and CUDA acceleration.
This package provides tools for monitoring and analyzing text for mental health
risk indicators, with capabilities for Discord message monitoring and
a Streamlit dashboard for visualization.

Modules:
    models: Transformer-based classification models
    dashboard: Streamlit dashboard interface
    discord_bot: Discord message monitoring
    utils: Helper utilities for text processing and optimized inference
    data: Sample datasets and data handling
    config: Configuration management
"""

import os
import sys
import logging
from datetime import datetime
import platform

# Package metadata
__version__ = '0.2.3'  # Semantic versioning: MAJOR.MINOR.PATCH
__author__ = 'Carlos Hernandez'
__email__ = 'scorpioon1008@ai-withcarlos.com'
__url__ = 'https://github.com/scoorpion1008/guardian'
__license__ = 'MIT'
__copyright__ = f'Copyright 2023-2025 {__author__}'
__build_date__ = '20250528'

# Platform information
__platform__ = {
    'python': platform.python_version(),
    'os': platform.platform(),
    'system': platform.system(),
    'machine': platform.machine(),
}

# Ensure submodules can be imported directly
from .models import transformer_classifier
from .utils import tokenizer
from . import config

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"guardian_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Guardian {__version__} initialized")
