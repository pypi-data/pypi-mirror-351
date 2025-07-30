import os
import sys
import discord
import torch
import logging
import asyncio
from datetime import datetime
from discord.ext import commands, tasks
from models.transformer_classifier import MentalHealthClassifier
from utils.tokenizer import tokenize_text
from utils.optimized_inference import OptimizedInference
from collections import deque
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("discord_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MentalHealthBot(commands.Bot):
    """Bot for monitoring mental health indicators in Discord messages"""
    
    def __init__(self, model_path, command_prefix="!", intents=None, parent_channel_id=None, 
                 batch_size=8, batch_interval=5.0):
        """
        Initialize bot with mental health classification model
        
        Args:
            model_path: Path to trained model
            command_prefix: Command prefix for bot commands
            intents: Discord intents
            parent_channel_id: Channel ID for sending alerts to parents
            batch_size: Maximum number of messages to process in a batch
            batch_interval: Time interval (in seconds) to process batched messages
        """
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True
        
        super().__init__(command_prefix=command_prefix, intents=intents)
          # Try to use optimized inference first, with fallback to standard model
        try:
            # Based on optimization report, prefer ONNX backend for RTX 4080
            self.inference_engine = OptimizedInference(
                model_path=model_path,
                backend="onnx" if "onnx" in sys.modules else None,  # Prefer ONNX if available
                batch_size=batch_size  # Use recommended batch size
            )
            self.use_optimized_inference = True
            logger.info(f"Using OptimizedInference engine with backend: {self.inference_engine.backend}")
        except Exception as e:
            logger.warning(f"Failed to initialize OptimizedInference: {str(e)}")
            logger.warning("Falling back to standard model loading")
            self.model = self._load_model(model_path)
            self.use_optimized_inference = False
        
        self.parent_channel_id = parent_channel_id
        self.risk_thresholds = {
            "medium": 0.5,  # Medium risk threshold
            "high": 0.7     # High risk threshold
        }
        
        # Batch processing settings
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.message_queue = deque()
        self.is_processing = False
        
        # Add commands
        self.add_commands()
        
    def _load_model(self, model_path):
        """Load the classification model"""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        model = MentalHealthClassifier().to(device)
        
        try:
            if os.path.exists(model_path):
                model.load_state_dict(torch.load(model_path, map_location=device))
                model.eval()
                logger.info(f"Model loaded from {model_path}")
            else:
                logger.warning(f"Model file not found at {model_path}. Using untrained model.")
                logger.warning(f"Please train the model first using: python main.py train --dataset <dataset_path>")
                # Continue with untrained model for demonstration purposes
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.warning("Using untrained model. Classification results will not be accurate.")
        
        return model
    
    def add_commands(self):
        """Add bot commands"""
        
        @self.command(name="status")
        async def status(ctx):
            """Check bot status"""
            if self.use_optimized_inference:
                await ctx.send(f"✅ Mental health monitoring bot is active using {self.inference_engine.backend} backend.")
            else:
                await ctx.send("✅ Mental health monitoring bot is active.")
                
            # Add queue status
            queue_length = len(self.message_queue)
            if queue_length > 0:
                await ctx.send(f"Currently processing {queue_length} message(s) in the queue.")
        
        @self.command(name="help_resources")
        async def help_resources(ctx):
            """Provide mental health resources"""
            resources = (
                "**Mental Health Resources**\n\n"
                "• Crisis Text Line: Text HOME to 741741\n"
                "• National Suicide Prevention Lifeline: 1-800-273-8255\n"
                "• Teen Line: Text TEEN to 839863\n"
                "• https://www.crisistextline.org/\n"
            )
            await ctx.send(resources)
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user.name}")
        logger.info(f"Bot is ready and monitoring messages")
        
        # Start the batch processing task
        self.process_message_batch.start()
    
    async def on_message(self, message):
        """Process incoming messages"""
        # Ignore messages from the bot itself
        if message.author == self.user:
            return
        
        # Process commands
        await self.process_commands(message)
        
        # Skip command messages
        if message.content.startswith(self.command_prefix):
            return
        
        # Add message to the processing queue instead of immediate analysis
        self.message_queue.append(message)
        
        # If queue size exceeds batch size, trigger processing
        if len(self.message_queue) >= self.batch_size and not self.is_processing:
            self.is_processing = True
            # Process the batch right away without waiting for the scheduled task
            await self._process_batch()
            self.is_processing = False
    
    @tasks.loop(seconds=5.0)  # Default interval is 5.0 seconds
    async def process_message_batch(self):
        """Process batched messages at regular intervals"""
        if self.message_queue and not self.is_processing:
            self.is_processing = True
            await self._process_batch()
            self.is_processing = False
    
    async def _process_batch(self):
        """Process a batch of messages from the queue"""
        # Limit batch size
        batch_size = min(len(self.message_queue), self.batch_size)
        if batch_size == 0:
            return
        
        logger.info(f"Processing batch of {batch_size} messages")
        
        # Extract messages from the queue while preserving their order
        messages = []
        for _ in range(batch_size):
            if self.message_queue:
                messages.append(self.message_queue.popleft())
        
        # Extract message contents
        contents = [message.content for message in messages]
        
        # Process the batch using the appropriate method
        if self.use_optimized_inference:
            # The OptimizedInference class handles batching efficiently
            try:
                # Process all texts at once
                results = self.inference_engine.process_texts(contents)
                
                # Handle results for each message
                for i, (message, result) in enumerate(zip(messages, results)):
                    high_risk_prob = result['probabilities'][2]
                    await self._handle_risk_level(message, high_risk_prob)
                    
            except Exception as e:
                logger.error(f"Error batch processing messages: {str(e)}")
                # Fall back to individual processing
                for message in messages:
                    await self._analyze_single_message(message)
        else:
            # Standard model doesn't handle batches, so process individually
            for message in messages:
                await self._analyze_single_message(message)
    
    async def _analyze_single_message(self, message):
        """
        Analyze a single message (used when batching fails or for standard model)
        
        Args:
            message: Discord message object
        """
        try:
            # Use OptimizedInference if available, otherwise use standard model
            if self.use_optimized_inference:
                # OptimizedInference handles tokenization internally
                result = self.inference_engine.analyze_text(message.content)
                # Extract risk probability (highest risk class)
                high_risk_prob = result['probabilities'][2]
            else:
                # Tokenize the message
                inputs = tokenize_text(message.content)
                
                # Get device
                device = next(self.model.parameters()).device
                
                # Run prediction
                with torch.no_grad():
                    input_ids = inputs["input_ids"].to(device)
                    attention_mask = inputs["attention_mask"].to(device)
                    outputs = self.model(input_ids, attention_mask)
                    probs = torch.softmax(outputs, dim=1).squeeze().cpu().tolist()
                
                # Check if high risk (index 2)
                if isinstance(probs, list):
                    high_risk_prob = probs[2]
                else:
                    high_risk_prob = probs
            
            await self._handle_risk_level(message, high_risk_prob)
                
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
    
    async def _handle_risk_level(self, message, risk_prob):
        """
        Handle message based on risk level
        
        Args:
            message: Discord message object
            risk_prob: Risk probability score
        """
        logger.info(f"Message risk assessment: {risk_prob:.4f}")
        
        # Take action based on risk level
        if risk_prob > self.risk_thresholds["high"]:
            await self._handle_high_risk(message, risk_prob)
        elif risk_prob > self.risk_thresholds["medium"]:
            await self._handle_medium_risk(message, risk_prob)
    
    async def _handle_high_risk(self, message, risk_prob):
        """Handle high risk messages"""
        logger.warning(f"HIGH RISK ({risk_prob:.4f}): User {message.author} in {message.channel}")
        
        # Notify parent channel if configured
        if self.parent_channel_id:
            parent_channel = self.get_channel(int(self.parent_channel_id))
            if parent_channel:
                alert = (
                    f"⚠️ **HIGH RISK ALERT** ⚠️\n\n"
                    f"User: {message.author.mention}\n"
                    f"Channel: {message.channel.mention}\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Risk Score: {risk_prob:.4f}\n\n"
                    f"Message: {message.content}"
                )
                await parent_channel.send(alert)
        
        # Send resources directly to the user
        try:
            resources = (
                "I noticed your message might indicate you're going through a tough time. "
                "Please know that help is available:\n\n"
                "• Crisis Text Line: Text HOME to 741741\n"
                "• National Suicide Prevention Lifeline: 1-800-273-8255\n"
                "• Teen Line: Text TEEN to 839863\n"
            )
            await message.author.send(resources)
        except discord.Forbidden:
            logger.warning(f"Could not send DM to {message.author}")
    
    async def _handle_medium_risk(self, message, risk_prob):
        """Handle medium risk messages"""
        logger.info(f"Medium risk ({risk_prob:.4f}): User {message.author}")
        
        # For medium risk, just log and monitor

def run_bot(token, model_path, parent_channel_id=None, batch_size=8, batch_interval=5.0):
    """
    Run the Discord bot
    
    Args:
        token: Discord bot token
        model_path: Path to trained model
        parent_channel_id: Channel ID for parent notifications
        batch_size: Maximum number of messages to process in a batch
        batch_interval: Time interval (in seconds) to process batched messages
    """
    # Try to get token from environment variable if not provided
    if token == "YOUR_DISCORD_BOT_TOKEN" or not token:
        import os
        env_token = os.environ.get("DISCORD_BOT_TOKEN")
        if env_token:
            logger.info("Using Discord bot token from environment variable")
            token = env_token
        else:
            logger.error("No Discord bot token provided. Set in config.py or DISCORD_BOT_TOKEN environment variable.")
            return
            
    bot = MentalHealthBot(
        model_path=model_path, 
        parent_channel_id=parent_channel_id,
        batch_size=batch_size,
        batch_interval=batch_interval
    )
    bot.run(token)
