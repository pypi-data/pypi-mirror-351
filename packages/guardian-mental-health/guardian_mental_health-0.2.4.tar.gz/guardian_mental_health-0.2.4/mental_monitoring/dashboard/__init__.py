"""
Dashboard Module for Mental Health Monitoring
===========================================

This module provides the Streamlit-based dashboard for the Guardian mental health
monitoring system. It allows parents and guardians to view mental health risk alerts
and trends, and provides tools for manual message analysis.

Classes:
    MentalHealthDashboard: Dashboard for mental health monitoring

Functions:
    main: Main function to run the dashboard
"""

import logging
import os
import sys

# Create module logger
logger = logging.getLogger(__name__)

# Import main components
from .streamlit_app import MentalHealthDashboard, main

__all__ = ['MentalHealthDashboard', 'main']
