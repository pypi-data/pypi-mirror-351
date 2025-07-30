"""
Data Module for Mental Health Monitoring
======================================

This module contains sample data and data handling utilities for the Guardian
mental health monitoring system. It includes sample messages with risk levels
for demonstration and testing purposes.

Files:
    samples.json: Sample messages with risk assessments
"""

import logging
import os
import json
from pathlib import Path

# Create module logger
logger = logging.getLogger(__name__)

# Define data directory
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def get_sample_data():
    """
    Load the sample data from samples.json.
    
    Returns:
        dict: Sample messages with risk assessments
    """
    try:
        with open(os.path.join(DATA_DIR, 'samples.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        return []

__all__ = ['get_sample_data', 'DATA_DIR']
