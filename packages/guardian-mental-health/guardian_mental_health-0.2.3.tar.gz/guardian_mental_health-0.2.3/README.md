# Guardian - Mental Health Monitoring System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/guardian-mental-health/)

Guardian is an advanced mental health monitoring system designed to detect and alert parents or guardians about potential mental health risks in adolescents' online communications. The system uses transformer-based deep learning models to analyze text for indicators of depression, anxiety, and suicidal ideation.

> **Security Note**: This project requires a Discord bot token for monitoring messages. For security, tokens should NEVER be committed to version control. Instead, use environment variables or a `.env` file (see `.env.example`). See the [Discord Bot Setup Guide](discord_bot_setup.md) for details.

## 🧠 Key Features

- **Transformer-based classification**: Uses BERT to analyze text for mental health risk indicators
- **Real-time monitoring**: Monitors Discord messages and other platforms
- **Streamlit dashboard**: Interactive dashboard for parents to review alerts and trends
- **Multi-level risk assessment**: Classifies communications into different risk levels
- **Privacy-focused**: Only alerts on concerning patterns, not normal conversations
- **Optimized inference**: Accelerated with CUDA, ONNX Runtime, and batch processing
- **Efficient batch processing**: Handles multiple messages at once for better performance
- **Automatic hardware adaptation**: Selects the best backend based on available hardware

## 📋 Project Structure

```text
mental_monitoring/
├── models/                      # ML models and training code
│   ├── transformer_classifier.py # BERT-based classifier model
│   └── training.py              # Training and evaluation code
├── data/                        # Dataset files
│   └── samples.json             # Sample message data
├── discord_bot/                 # Discord integration
│   └── monitor.py               # Discord message monitoring with batch processing
├── dashboard/                   # Parent dashboard UI
│   └── streamlit_app.py         # Streamlit dashboard application
├── utils/                       # Helper utilities
│   ├── tokenizer.py             # Text preprocessing
│   └── optimized_inference.py   # Accelerated inference engine (CUDA, ONNX, TensorRT)
├── config/                      # Configuration modules
│   ├── config.py                # Main configuration settings
│   └── optimization_config.py   # Inference optimization settings
└── main.py                      # Main entry point with batch processing options
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- PyTorch 2.0+ (with CUDA support recommended)
- Streamlit
- Discord.py

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/guardian.git
cd guardian
```

2. Create a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r requirements.txt
```

5. Configure the application:
   - Edit `config.py` to set your Discord bot token and other settings
   - Place your trained model in the models directory, or train a new one

### Running the Application

Start the Streamlit dashboard:

```bash
python main.py dashboard
```

Start the Discord bot:

```bash
# Basic usage
python main.py bot --token YOUR_DISCORD_BOT_TOKEN

# With optimized batch processing
python main.py bot --token YOUR_DISCORD_BOT_TOKEN --batch-size 16 --batch-interval 3.0 --optimize
```

Optimize the Discord bot for your hardware:

```bash
# Get recommendations for your system
python optimize_discord_bot.py --benchmark
```

Train a model:

```bash
python main.py train --dataset path/to/dataset.csv
```

Evaluate a model:

```bash
python main.py evaluate --dataset path/to/dataset.csv
```

## 🧪 Training the Model

The system can be fine-tuned on various mental health datasets:

1. **Reddit SuicideWatch and Mental Health Collection**
2. **DepressionEmo Dataset**
3. **Robin: A Novel Online Suicidal Text Corpus**
4. **Suicide and Depression Detection Dataset (Kaggle)**

Example training command:

```bash
python main.py train --dataset data/combined_dataset.csv --epochs 5 --batch-size 16
```

## 📊 Dashboard

The Streamlit dashboard provides:

- Overview of risk metrics
- Timeline of detected risk indicators
- Message history with risk assessment
- Analysis tool for manual message evaluation
- Mental health resources for parents

## 🔒 Privacy and Ethics

This tool is designed with privacy and ethical considerations in mind:

- Data is processed locally and not stored on external servers
- Only high-risk communications trigger alerts
- The system is designed as a supplementary tool, not a replacement for proper mental health care
- Parents should discuss monitoring with adolescents and ensure proper consent

## � Performance Optimization

Guardian uses advanced optimization techniques to improve inference speed:

- **CUDA Acceleration**: Leverages NVIDIA GPUs for faster model inference
- **ONNX Runtime**: Export and run models through ONNX for significant speedup
- **TensorRT Integration**: Optional TensorRT support for maximum performance
- **Batch Processing**: Process multiple messages at once for higher throughput
- **Automatic Mixed Precision**: Use FP16 calculations where appropriate
- **Dynamic Backend Selection**: Automatically choose the best inference backend

### Example Scripts

The `examples/` directory contains scripts demonstrating how to use optimization features:

```bash
# Run batch message processing benchmark
python examples/batch_message_processing.py

# Run Discord bot with optimized settings
python examples/run_optimized_bot.py --batch-size 16
```

## �📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- HuggingFace Transformers library
- Mental health research community for datasets and guidance
- Streamlit for the dashboard framework
