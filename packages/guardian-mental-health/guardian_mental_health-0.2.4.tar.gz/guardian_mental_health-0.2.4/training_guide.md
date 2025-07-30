# Training Guide: Mental Health Monitoring Models

This guide provides step-by-step instructions for training the transformer-based mental health monitoring models used in the Guardian system.

## Prerequisites

Before you begin training, ensure you have:

- Installed all required dependencies: `pip install -r requirements.txt`
- Access to a machine with CUDA-enabled GPU (recommended for faster training)
- Downloaded appropriate mental health datasets (see below)

## Recommended Datasets

For effective training, we recommend using one or more of these datasets:

1. **Reddit SuicideWatch and Mental Health Collection (SWMH)**
   - [Available on HuggingFace](https://huggingface.co/datasets/AIMH/SWMH)
   - Contains 54,000+ posts from mental health subreddits

2. **Robin: Online Suicidal Text Corpus**
   - [Available on arXiv](https://arxiv.org/abs/2209.05707)
   - Contains 1.1+ million posts with various suicide-related content

3. **DepressionEmo Dataset**
   - [Available on GitHub](https://github.com/SandipanSengupta/DepressionEmo)
   - Contains 6,037 examples annotated for depression-related emotions

4. **Suicide and Depression Detection Dataset**
   - [Available on Kaggle](https://www.kaggle.com/datasets/nikhileswarkomati/suicide-watch)
   - Contains labeled texts for suicide and depression detection

## Data Preparation

1. **Download the datasets** from the sources provided above.

2. **Format the data** as a CSV file with at least two columns:
   - `text`: The message content
   - `label`: The risk level (0: No risk, 1: Low risk, 2: High risk)

   Example:
   ```
   text,label
   "I had a good day today!",0
   "I'm feeling kind of down, not sure why.",1
   "I can't take this pain anymore, I just want it to end.",2
   ```

3. **Place the dataset** in the `mental_monitoring/data/` directory.

## Configuration

You can customize training parameters in `mental_monitoring/config.py`:

```python
# Training configuration
TRAINING_CONFIG = {
    "batch_size": 16,           # Increase for faster training (if GPU memory allows)
    "learning_rate": 2e-5,      # Typically 2e-5 to 5e-5 works well for BERT
    "num_epochs": 5,            # Increase for potentially better results
    "train_test_split": 0.2,    # 80% training, 20% validation
    "random_seed": 42,          # For reproducible results
    "early_stopping_patience": 3 # Stop if validation loss doesn't improve for 3 epochs
}

# Model configuration
MODEL_CONFIG = {
    "pretrained_model": "bert-base-uncased",  # Can try other models like distilbert-base-uncased
    "max_length": 128,  # Maximum sequence length (increase if needed)
    "num_classes": 3,   # Risk levels
    "saved_model_path": os.path.join(MODEL_DIR, "saved_model.pt")
}
```

## Training Methods

### Method 1: Command Line Interface

Use the built-in CLI for training:

```bash
# Basic training command
python mental_monitoring/main.py train --dataset mental_monitoring/data/combined_dataset.csv

# With additional options
python mental_monitoring/main.py train --dataset mental_monitoring/data/combined_dataset.csv --epochs 10 --batch-size 32
```

### Method 2: Direct Training Script

For more control over the training process:

1. Create a Python script (e.g., `train_custom.py`) in the project root:

```python
import pandas as pd
import os
from mental_monitoring.models.training import train_model
from mental_monitoring.config import MODEL_CONFIG, TRAINING_CONFIG
from sklearn.model_selection import train_test_split

# Load dataset
data_path = "mental_monitoring/data/combined_dataset.csv"
data = pd.read_csv(data_path)

# Split data
train_data, val_data = train_test_split(
    data,
    test_size=TRAINING_CONFIG["train_test_split"],
    random_state=TRAINING_CONFIG["random_seed"],
    stratify=data["label"] if "label" in data.columns else None
)

# Train model
model = train_model(
    train_data=train_data,
    val_data=val_data,
    model_save_path=MODEL_CONFIG["saved_model_path"],
    num_epochs=TRAINING_CONFIG["num_epochs"],
    batch_size=TRAINING_CONFIG["batch_size"],
    learning_rate=TRAINING_CONFIG["learning_rate"]
)

print(f"Model saved to {MODEL_CONFIG['saved_model_path']}")
```

2. Run the script:

```bash
python train_custom.py
```

### Method 3: Using VS Code Task

1. The repository includes a VS Code task for training (if not, you can add it in `.vscode/tasks.json`):

```json
{
    "label": "Train Model",
    "type": "shell",
    "command": "${command:python.interpreterPath}",
    "args": [
        "${workspaceFolder}/mental_monitoring/main.py",
        "train",
        "--dataset",
        "${workspaceFolder}/mental_monitoring/data/combined_dataset.csv"
    ],
    "presentation": {
        "reveal": "always",
        "panel": "new"
    },
    "problemMatcher": []
}
```

2. Press `Ctrl+Shift+P`, type "Run Task", and select "Train Model".

## Advanced Training Techniques

### 1. Class Weighting for Imbalanced Data

If your dataset has imbalanced classes (e.g., fewer high-risk examples):

```python
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Compute class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data['label']),
    y=train_data['label']
)

# Convert to dictionary
weight_dict = {i: weight for i, weight in enumerate(class_weights)}

# Update training code to use weights
criterion = nn.CrossEntropyLoss(weight=torch.tensor(list(weight_dict.values())).float().to(device))
```

### 2. Fine-tuning in Stages

For better results, you can fine-tune in stages:

1. First, freeze most BERT layers and train only the top layers:

```python
# Freeze BERT layers
for param in model.bert.parameters():
    param.requires_grad = False

# Unfreeze the top 2 layers
for param in model.bert.encoder.layer[-2:].parameters():
    param.requires_grad = True

# Train with a higher learning rate
optimizer = optim.AdamW(model.parameters(), lr=5e-4)
```

2. Then unfreeze all layers and continue training with a lower learning rate:

```python
# Unfreeze all BERT layers
for param in model.bert.parameters():
    param.requires_grad = True

# Train with a lower learning rate
optimizer = optim.AdamW(model.parameters(), lr=2e-5)
```

### 3. K-fold Cross-validation

For more robust evaluation:

```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=TRAINING_CONFIG["random_seed"])

for fold, (train_idx, val_idx) in enumerate(kf.split(data)):
    print(f"Training fold {fold+1}/5")
    train_fold = data.iloc[train_idx]
    val_fold = data.iloc[val_idx]
    
    model = train_model(
        train_data=train_fold,
        val_data=val_fold,
        model_save_path=f"{MODEL_CONFIG['saved_model_path']}.fold{fold+1}",
        num_epochs=TRAINING_CONFIG["num_epochs"],
        batch_size=TRAINING_CONFIG["batch_size"],
        learning_rate=TRAINING_CONFIG["learning_rate"]
    )
```

## Evaluating the Model

After training, evaluate your model to ensure it performs well:

```bash
python mental_monitoring/main.py evaluate --dataset mental_monitoring/data/test_dataset.csv --model mental_monitoring/models/saved_model.pt
```

The evaluation will output:
- Classification report (precision, recall, F1-score)
- Confusion matrix
- Accuracy and other metrics

## Integrating the Trained Model

Once you have a trained model:

1. Make sure it's saved at the location specified in `config.py` (or update the path)
2. Start the dashboard or Discord bot to use the trained model:

```bash
# Start the dashboard
python mental_monitoring/main.py dashboard

# Start the Discord bot
python mental_monitoring/main.py bot --token YOUR_DISCORD_BOT_TOKEN
```

## Troubleshooting

### Common Issues:

1. **Out of memory errors**:
   - Reduce batch size in `config.py`
   - Try a smaller model like "distilbert-base-uncased"
   - Reduce max sequence length

2. **Poor performance**:
   - Try class weighting for imbalanced datasets
   - Increase training epochs
   - Use a larger dataset or combine multiple datasets
   - Experiment with different learning rates

3. **Overfitting**:
   - Add dropout (default is already 0.3)
   - Use early stopping (already implemented)
   - Apply more regularization (increase weight_decay)

4. **CUDA errors**:
   - Make sure you have a CUDA-compatible GPU
   - Update GPU drivers
   - Install the correct PyTorch version for your CUDA version
