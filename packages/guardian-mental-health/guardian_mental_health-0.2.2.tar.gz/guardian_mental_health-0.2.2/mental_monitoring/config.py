"""
Configuration file for mental health monitoring system
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Model configuration
MODEL_CONFIG = {
    "pretrained_model": "bert-base-uncased",
    "max_length": 128,
    "num_classes": 3,  # 0: No risk, 1: Low risk, 2: High risk (suicidal ideation)
    "saved_model_path": os.path.join(MODEL_DIR, "saved_model.pt")
}

# Discord bot configuration
DISCORD_CONFIG = {
    "token": "YOUR_DISCORD_BOT_TOKEN",  # Replace with token from Discord Developer Portal 
    "command_prefix": "!",
    "parent_channel_id": None,  # Channel ID for parent alerts
    "risk_thresholds": {
        "medium": 0.5,  # Medium risk threshold
        "high": 0.7     # High risk threshold
    }
}

# Dashboard configuration
DASHBOARD_CONFIG = {
    "port": 8501,
    "theme": "light",
    "data_path": os.path.join(DATA_DIR, "message_history.json"),
    "model_path": MODEL_CONFIG["saved_model_path"],
    "refresh_interval": 60  # Refresh interval in seconds
}

# Training configuration
TRAINING_CONFIG = {
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_epochs": 5,
    "train_test_split": 0.2,
    "random_seed": 42,
    "early_stopping_patience": 3
}

# Dataset paths
DATASET_PATHS = {
    "suicide_watch": os.path.join(DATA_DIR, "suicide_watch.csv"),
    "depression": os.path.join(DATA_DIR, "depression.csv"),
    "combined": os.path.join(DATA_DIR, "combined_dataset.csv")
}

# Risk level definitions
RISK_LEVELS = {
    0: {"label": "No Risk", "color": "green", "description": "No significant risk indicators detected."},
    1: {"label": "Low Risk", "color": "yellow", "description": "Some minor risk indicators detected, monitor situation."},
    2: {"label": "High Risk", "color": "red", "description": "Significant risk indicators detected, immediate attention required."}
}

# Mental health resources
RESOURCES = [
    {
        "name": "National Suicide Prevention Lifeline",
        "phone": "1-800-273-8255",
        "url": "https://suicidepreventionlifeline.org/",
        "description": "24/7 support for people in distress"
    },
    {
        "name": "Crisis Text Line",
        "phone": "Text HOME to 741741",
        "url": "https://www.crisistextline.org/",
        "description": "Text-based crisis support"
    },
    {
        "name": "Teen Line",
        "phone": "310-855-HOPE or Text TEEN to 839863",
        "url": "https://teenlineonline.org/",
        "description": "Support specifically for teenagers"
    }
]
