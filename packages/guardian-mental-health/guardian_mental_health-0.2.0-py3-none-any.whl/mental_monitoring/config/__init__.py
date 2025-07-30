"""
Configuration file initialization.

This ensures that the config module is properly imported.
"""

# Import the configuration from the main file
from .config import *

# Export all configuration variables
__all__ = [
    'MODEL_CONFIG', 
    'DISCORD_CONFIG', 
    'DASHBOARD_CONFIG', 
    'TRAINING_CONFIG',
    'DATASET_PATHS',
    'RISK_LEVELS',
    'RESOURCES'
]
