# Guardian: Mental Health Monitoring System

## Complete Setup and Usage Guide

This document provides a quick overview of how to set up and use the Guardian mental health monitoring system.

---

## 1️⃣ System Overview

Guardian is a mental health monitoring system with three main components:

- **AI Model**: BERT-based transformer model to detect mental health risk signals in text
- **Discord Bot**: Monitors Discord messages for concerning content
- **Dashboard**: Streamlit interface for parents/guardians to review alerts and trends

---

## 2️⃣ Initial Setup

### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Prepare Configuration

Update the configuration in `mental_monitoring/config.py` with appropriate settings:

- Set Discord bot token (or use environment variable `DISCORD_BOT_TOKEN`)
- Configure parent notification channel ID
- Adjust risk thresholds if needed

---

## 3️⃣ Train the Model

### Option 1: Use the Training Script

```bash
# Train using Kaggle suicide detection dataset (recommended)
python train_model.py --dataset kaggle --csv-path path/to/suicide_watch.csv --balance

# Train with advanced options
python train_model.py --dataset kaggle --epochs 10 --batch-size 16 --balance
```

### Option 2: Use the CLI Interface

```bash
python mental_monitoring/main.py train --dataset path/to/dataset.csv
```

For detailed training instructions, see `training_guide.md`.

---

## 4️⃣ Set Up Discord Bot

### Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application named "Guardian"
3. Go to Bot tab and create a bot
4. Enable all privileged intents (especially Message Content)
5. Copy the bot token

### Configure Bot Settings

1. Add token to system (environment variable or config file)
2. Set up a parent notification channel ID in config

For detailed Discord setup instructions, see `discord_bot_setup.md`.

---

## 5️⃣ Run the System

### Start the Dashboard

```bash
python mental_monitoring/main.py dashboard
```

Or use the VS Code task: "Run Dashboard"

### Start the Discord Bot

```bash
python mental_monitoring/main.py bot
```

Or use the VS Code task: "Run Discord Bot"

---

## 6️⃣ Using the System

### Dashboard Features

- **Overview**: Key metrics and risk summary
- **Trends**: Visual representation of risk levels over time
- **Message History**: Review monitored messages with risk assessment
- **Analysis Tool**: Manually analyze text for risk indicators
- **Resources**: Mental health support resources

### Discord Bot Features

- Real-time message monitoring
- Risk assessment for each message
- Automatic alerts to parent channel for high-risk messages
- Resource sharing with at-risk individuals
- Support commands:
  - `!status`: Check bot status
  - `!help_resources`: Show mental health resources

---

## 7️⃣ Privacy and Ethical Considerations

- **Inform Users**: Always inform users that monitoring is in place
- **Consent**: Obtain proper consent for monitoring
- **Data Security**: Handle message data securely, avoid unnecessary storage
- **False Positives**: Review alerts manually before taking action
- **Support, Not Replace**: Use as a supplement to proper mental health care

---

## 8️⃣ Troubleshooting

### Model Issues
- **Poor predictions**: Retrain with larger or better dataset
- **Slow performance**: Enable CUDA or decrease model size

### Discord Bot Issues
- **Not reading messages**: Ensure Message Content intent is enabled
- **No alerts**: Verify parent_channel_id is correct

### Dashboard Issues
- **Not showing data**: Check data path configuration
- **Model errors**: Verify model path is correct

---

## 9️⃣ Extending the System

- Add more communication platforms (SMS, email, other chat apps)
- Implement multi-language support
- Create mobile notifications
- Add user demographics for better context
- Implement automatic resource recommendations

---

For more detailed information, refer to:
- `README.md`: Project overview
- `training_guide.md`: Detailed model training instructions
- `discord_bot_setup.md`: Discord bot configuration
