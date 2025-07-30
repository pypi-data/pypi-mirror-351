# Discord Bot Setup Guide

This guide walks you through setting up the Guardian Discord bot for mental health monitoring.

## 1. Create a Discord Bot in the Developer Portal

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it "Guardian"
3. Upload a guardian/shield icon (1024x1024 pixels)
4. Add a description:
   ```
   Guardian is a mental health monitoring bot that uses AI to detect signs of depression, anxiety, and suicidal ideation in Discord messages. It provides early warning to parents/guardians while respecting privacy. The bot only flags concerning patterns and offers resources when needed.
   ```
5. Add tags: "mental-health", "wellness", "monitoring", "ai", "support"

## 2. Configure the Bot

1. Go to the "Bot" tab in the left sidebar
2. Click "Add Bot" if not already added
3. Under "Privileged Gateway Intents", enable ALL THREE intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent (CRITICAL - required to read message content)
4. Click "Reset Token" and copy your token (keep this secure!)

## 3. Set Bot Permissions and Generate Invite Link

1. Go to the "OAuth2" → "URL Generator" tab
2. Under "Scopes", select "bot" 
3. Under "Bot Permissions", select:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Add Reactions
   - Attach Files
   - Embed Links
4. Copy the generated URL at the bottom of the page

## 4. Add the Bot to Your Server

1. Paste the URL from Step 3 into a web browser
2. Select the server to add the bot to
3. Follow the authorization prompts
4. Verify the bot appears in your server member list

## 5. Configure the Guardian System

1. Add your bot token to the application (NEVER commit tokens to version control!):

   **Option 1: Environment Variable (Recommended for Security)**
   
   ```bash
   # On Windows:
   setx DISCORD_BOT_TOKEN "your_token_here"
   
   # On Linux/macOS:
   export DISCORD_BOT_TOKEN="your_token_here"
   ```
   
   **Option 2: Create a .env File (For Development)**
   - Copy the template from `.env.example` to `.env`
   - Add your token to the .env file:
   
   ```plaintext
   DISCORD_BOT_TOKEN=your_token_here
   ```
   
   - Make sure to add `.env` to your `.gitignore` file
     **Option 3: Command Line Argument (For Testing)**
   
   ```bash
   python mental_monitoring/main.py bot --token "your_token_here"
   ```
   ```bash
   # On Windows PowerShell
   $env:DISCORD_BOT_TOKEN="your_token_here"
   
   # On Linux/macOS
   export DISCORD_BOT_TOKEN="your_token_here"
   ```

## 6. Advanced Bot Configuration

### Performance Optimization

You can optimize the bot's message processing using batch processing:

```bash
python mental_monitoring/main.py bot --batch-size 16 --batch-interval 5.0 --optimize
```

Parameters:
- `--batch-size`: Maximum number of messages to process at once (default: 8)  
  Higher values improve throughput but increase memory usage
- `--batch-interval`: Time between batch processing in seconds (default: 5.0)  
  Lower values reduce latency but increase CPU/GPU usage
- `--optimize`: Force use of the optimized inference engine

### Finding Optimal Settings

Run the optimization utility to get personalized recommendations:

```bash
python optimize_discord_bot.py --benchmark
```

This will:
1. Detect your system hardware capabilities
2. Benchmark different batch sizes
3. Recommend optimal settings for your hardware

### Optimized Settings for RTX 4080 Laptop GPU

Based on benchmarks, the optimal settings for NVIDIA RTX 4080 Laptop GPU are:

- **Batch size**: 8 (processes 8 messages at once)
- **Batch interval**: 3.0 seconds
- **Backend**: ONNX with CUDA provider
- **Expected throughput**: ~756 messages/second

To use these settings, run:

```bash
# Windows PowerShell
.\run_optimized_bot.bat

# Or manually
python mental_monitoring\main.py bot --batch-size 8 --batch-interval 3.0 --optimize
```

   **Option 2: Update config.py**
   Edit `mental_monitoring/config.py` and replace:
   ```python
   "token": "YOUR_DISCORD_BOT_TOKEN"
   ```
   with
   ```python
   "token": "your_actual_token_here"
   ```

2. Set up a parent notification channel:
   - Create a private channel in your Discord server
   - Right-click the channel and select "Copy ID" (Developer Mode must be enabled)
   - Add this ID to your config:
     ```python
     "parent_channel_id": "1234567890123456789"
     ```

## 6. Start the Bot

Run the bot using:

```bash
python mental_monitoring/main.py bot
```

Or use the VS Code task "Run Discord Bot"

## 7. Bot Commands

The Guardian bot supports these commands:

- `!status` - Check if the bot is running
- `!help_resources` - Display mental health resources

## 8. Privacy and Usage Notes

- The bot analyzes message content for mental health risk indicators
- High-risk messages trigger alerts to the designated parent channel
- The system respects privacy by only flagging concerning patterns
- Consider informing users that the bot is monitoring messages
- Use the dashboard to review alerts and analyze trends

## Troubleshooting

- **Bot doesn't respond**: Ensure token is correct and intents are enabled
- **Can't read messages**: Message Content Intent must be enabled
- **Missing permissions**: Ensure bot has proper permissions in the server
- **No alerts**: Check parent_channel_id and risk thresholds in config
