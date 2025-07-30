"""
Main entry point for mental health monitoring system
"""

import os
import argparse
import logging
import torch
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"guardian_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_parser():
    """Set up command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Guardian - Mental Health Monitoring System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start the Streamlit dashboard")
    dashboard_parser.add_argument("--port", type=int, default=8501, help="Port for Streamlit dashboard")
    
    # Discord bot command
    bot_parser = subparsers.add_parser("bot", help="Start the Discord monitoring bot")
    bot_parser.add_argument("--token", type=str, help="Discord bot token")
    bot_parser.add_argument("--parent-channel", type=str, help="Channel ID for parent notifications")
    bot_parser.add_argument("--batch-size", type=int, default=8, help="Maximum messages to process in a batch")
    bot_parser.add_argument("--batch-interval", type=float, default=5.0, 
                           help="Time interval (in seconds) between batch processing")
    bot_parser.add_argument("--optimize", action="store_true", 
                           help="Force use of optimized inference engine (will fail if not available)")
    
    # Training command
    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument("--dataset", type=str, required=True, help="Path to training dataset")
    train_parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    train_parser.add_argument("--batch-size", type=int, default=16, help="Training batch size")
    
    # Evaluation command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate the model")
    eval_parser.add_argument("--dataset", type=str, required=True, help="Path to evaluation dataset")
    eval_parser.add_argument("--model", type=str, help="Path to trained model")
    
    return parser

def run_dashboard(args):
    """Run the Streamlit dashboard"""
    import subprocess
    from config import DASHBOARD_CONFIG
    
    # Get the directory containing the Streamlit app
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "streamlit_app.py")
    
    # Run Streamlit
    port = args.port or DASHBOARD_CONFIG["port"]
    logger.info(f"Starting Streamlit dashboard on port {port}")
    
    cmd = ["streamlit", "run", dashboard_path, "--server.port", str(port)]
    subprocess.run(cmd)

def run_discord_bot(args):
    """Run the Discord monitoring bot"""
    from discord_bot.monitor import run_bot
    from config import DISCORD_CONFIG, MODEL_CONFIG
    
    token = args.token or DISCORD_CONFIG["token"]
    if not token:
        logger.error("Discord bot token not set. For security reasons, please set it using one of these methods:")
        logger.error("1. Set the DISCORD_BOT_TOKEN environment variable")
        logger.error("2. Create a .env file with DISCORD_BOT_TOKEN=your_token")
        logger.error("3. Provide it via command line: --token YOUR_TOKEN")
        logger.error("\nNEVER commit tokens to version control!")
        return
    
    parent_channel_id = args.parent_channel or DISCORD_CONFIG["parent_channel_id"]
    logger.info(f"Starting Discord bot with parent channel ID: {parent_channel_id}")
    
    # Use batch processing configurations if provided
    batch_size = args.batch_size
    batch_interval = args.batch_interval
    
    # Auto-configure for RTX GPUs if no specific batch size is provided
    if torch.cuda.is_available() and "RTX" in torch.cuda.get_device_name(0):
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"RTX GPU detected: {gpu_name}")
        
        # Optimal batch size for RTX 4080 based on benchmark
        if "4080" in gpu_name and batch_size == 8:
            logger.info("Using optimized batch settings for RTX 4080 Laptop GPU")
            batch_size = 8
            batch_interval = 3.0 if batch_interval == 5.0 else batch_interval  # Only change if default
    
    logger.info(f"Batch processing settings: size={batch_size}, interval={batch_interval}s")
    
    # Create configuration dictionary for the bot
    bot_config = {
        "model_path": MODEL_CONFIG["saved_model_path"],
        "parent_channel_id": parent_channel_id,
        "batch_size": batch_size,
        "batch_interval": batch_interval
    }
    
    # If optimization is explicitly requested, check for availability
    if args.optimize:
        try:
            from utils.optimized_inference import OptimizedInference
            # Just create an instance to test availability
            _ = OptimizedInference(model_path=MODEL_CONFIG["saved_model_path"])
            logger.info("Optimized inference engine successfully initialized")
        except ImportError:
            logger.error("Optimized inference requested but required packages not installed")
            logger.error("Try: pip install onnx onnxruntime-gpu")
            return
        except Exception as e:
            logger.error(f"Error initializing optimized inference: {str(e)}")
            return
    
    # Run the bot
    run_bot(token=token, **bot_config)

def train_model(args):
    """Train the model"""
    import pandas as pd
    from models.training import train_model
    from config import MODEL_CONFIG, TRAINING_CONFIG
    
    logger.info(f"Loading training dataset from {args.dataset}")
    try:
        data = pd.read_csv(args.dataset)
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        return
    
    logger.info(f"Training model with {len(data)} examples")
    
    # Get training parameters
    epochs = args.epochs or TRAINING_CONFIG["num_epochs"]
    batch_size = args.batch_size or TRAINING_CONFIG["batch_size"]
    
    # Split the data into train and validation
    from sklearn.model_selection import train_test_split
    train_data, val_data = train_test_split(
        data, 
        test_size=TRAINING_CONFIG["train_test_split"],
        random_state=TRAINING_CONFIG["random_seed"]
    )
    
    logger.info(f"Training on {len(train_data)} examples, validating on {len(val_data)} examples")
    
    # Train the model
    train_model(
        train_data=train_data,
        val_data=val_data,
        model_save_path=MODEL_CONFIG["saved_model_path"],
        num_epochs=epochs,
        batch_size=batch_size,
        learning_rate=TRAINING_CONFIG["learning_rate"]
    )
    
    logger.info(f"Model saved to {MODEL_CONFIG['saved_model_path']}")

def evaluate_model(args):
    """Evaluate the model"""
    import pandas as pd
    from models.training import evaluate_model, load_model
    from config import MODEL_CONFIG
    
    # Load dataset
    logger.info(f"Loading evaluation dataset from {args.dataset}")
    try:
        data = pd.read_csv(args.dataset)
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        return
    
    # Load model
    model_path = args.model or MODEL_CONFIG["saved_model_path"]
    logger.info(f"Loading model from {model_path}")
    try:
        model = load_model(model_path)
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return
    
    # Evaluate model
    logger.info(f"Evaluating model on {len(data)} examples")
    report, cm = evaluate_model(model, data)
    
    # Log evaluation results
    logger.info(f"Evaluation Report:\n{report}")

def main():
    """Main function"""
    # Parse arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    # Execute command
    if args.command == "dashboard":
        run_dashboard(args)
    elif args.command == "bot":
        run_discord_bot(args)
    elif args.command == "train":
        train_model(args)
    elif args.command == "evaluate":
        evaluate_model(args)
    else:
        logger.error("No command specified. Use --help to see available commands.")

if __name__ == "__main__":
    main()
