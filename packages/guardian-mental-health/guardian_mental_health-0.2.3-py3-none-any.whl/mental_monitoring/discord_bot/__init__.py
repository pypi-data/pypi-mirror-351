"""
Discord Bot Module for Mental Health Monitoring
==============================================

This module provides Discord integration for the Guardian mental health monitoring system.
It includes a bot that can monitor Discord messages for mental health risk indicators
and alert parents or guardians when concerning content is detected.

Classes:
    MentalHealthBot: Bot for monitoring mental health indicators in Discord messages

Functions:
    run_bot: Run the Discord bot with specified configuration
"""

import logging
import os
from pathlib import Path

# Create module logger
logger = logging.getLogger(__name__)

# Import main components
from .monitor import MentalHealthBot, run_bot

__all__ = ['MentalHealthBot', 'run_bot']
