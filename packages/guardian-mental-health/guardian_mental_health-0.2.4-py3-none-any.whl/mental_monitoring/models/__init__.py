"""
Models Module for Mental Health Monitoring
=========================================

This module contains the machine learning models used for detecting mental health
risk indicators in text. It provides transformer-based classifiers built on BERT
and tools for training and evaluating these models.

Classes:
    MentalHealthClassifier: BERT-based model for mental health risk classification

Functions:
    train_model: Train a mental health classifier on a dataset
    evaluate_model: Evaluate a trained model on test data
    load_model: Load a saved model from disk
"""

import logging
import os
import torch

# Create module logger
logger = logging.getLogger(__name__)

# Check for CUDA availability
if torch.cuda.is_available():
    logger.info(f"CUDA is available: {torch.cuda.get_device_name(0)}")
    logger.info(f"Using CUDA version: {torch.version.cuda}")
else:
    logger.warning("CUDA is not available. Training/inference will run on CPU.")

# Import main components
from .transformer_classifier import MentalHealthClassifier
from .training import train_model, evaluate_model, load_model, TextDataset

__all__ = [
    'MentalHealthClassifier', 
    'train_model', 
    'evaluate_model', 
    'load_model',
    'TextDataset'
]
