import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm
from transformers import BertTokenizer
from torch.utils.data import DataLoader, Dataset
import logging

# Use absolute imports to avoid path issues
from mental_monitoring.models.transformer_classifier import MentalHealthClassifier
from mental_monitoring.utils.tokenizer import tokenize_text

# Configure logger
logger = logging.getLogger(__name__)

class TextDataset(Dataset):
    """Dataset for text classification"""
    
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

def train_model(train_data, val_data=None, model_save_path='./saved_model', 
                num_epochs=5, batch_size=16, learning_rate=2e-5):
    """
    Train the mental health classifier
    
    Args:
        train_data: DataFrame with 'text' and 'label' columns
        val_data: Optional validation DataFrame with 'text' and 'label' columns
        model_save_path: Path to save the trained model
        num_epochs: Number of training epochs
        batch_size: Batch size for training
        learning_rate: Learning rate for optimizer
      Returns:
        Trained model
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        logger.info(f"CUDA is available: {torch.cuda.get_device_name(0)}")
        logger.info(f"Using CUDA version: {torch.version.cuda}")
        # Enable cuDNN auto-tuner for fastest training speeds
        torch.backends.cudnn.benchmark = True
        
        # Set device count and distributed training if multiple GPUs
        if torch.cuda.device_count() > 1:
            logger.info(f"Using {torch.cuda.device_count()} GPUs for training")
            # For multi-GPU setup, you could use DataParallel
            # model = nn.DataParallel(model)
    else:
        logger.warning("CUDA is not available. Using CPU for training (this will be slow).")
    
    # Create model
    model = MentalHealthClassifier().to(device)
    
    # Initialize tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    
    # Create datasets
    train_dataset = TextDataset(train_data['text'].values, train_data['label'].values, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, 
                             num_workers=0 if device.type == 'cuda' else 0)
    
    if val_data is not None:
        val_dataset = TextDataset(val_data['text'].values, val_data['label'].values, tokenizer)
        val_loader = DataLoader(val_dataset, batch_size=batch_size,
                              num_workers=0 if device.type == 'cuda' else 0)
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate)
    
    # Training loop
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")
        for batch in progress_bar:
            optimizer.zero_grad()
            
            # Move batch data to the appropriate device (GPU or CPU)
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            # Forward pass
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = criterion(outputs, labels)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            progress_bar.set_postfix({'loss': loss.item()})
        
        avg_train_loss = train_loss / len(train_loader)
        logger.info(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {avg_train_loss:.4f}")
        
        # Validation
        if val_data is not None:
            model.eval()
            val_loss = 0
            val_preds = []
            val_labels = []
            
            with torch.no_grad():
                for batch in val_loader:
                    # Move batch data to the appropriate device (GPU or CPU)
                    input_ids = batch['input_ids'].to(device)
                    attention_mask = batch['attention_mask'].to(device)
                    labels = batch['label'].to(device)
                    
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                    loss = criterion(outputs, labels)
                    
                    val_loss += loss.item()
                    
                    _, preds = torch.max(outputs, dim=1)
                    val_preds.extend(preds.cpu().numpy())
                    val_labels.extend(labels.cpu().numpy())
            
            avg_val_loss = val_loss / len(val_loader)
            logger.info(f"Epoch {epoch+1}/{num_epochs}, Val Loss: {avg_val_loss:.4f}")
            
            # Print classification report
            report = classification_report(val_labels, val_preds)
            logger.info(f"Validation Classification Report:\n{report}")
            
            # Save best model
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                # Ensure directory exists
                os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
                torch.save(model.state_dict(), model_save_path)
                logger.info(f"Model saved to {model_save_path}")
    
    # Load best model if validation was done
    if val_data is not None and os.path.exists(model_save_path):
        model.load_state_dict(torch.load(model_save_path))
    
    return model

def evaluate_model(model, test_data, batch_size=16):
    """
    Evaluate the model on test data
    
    Args:
        model: Trained MentalHealthClassifier model
        test_data: DataFrame with 'text' and 'label' columns
        batch_size: Batch size for evaluation
    
    Returns:
        Classification report and confusion matrix
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    test_dataset = TextDataset(test_data['text'].values, test_data['label'].values, tokenizer)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, attention_mask)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())
    
    # Generate reports
    report = classification_report(all_labels, all_preds, output_dict=True)
    cm = confusion_matrix(all_labels, all_preds)
    
    print(classification_report(all_labels, all_preds))
    print("Confusion Matrix:")
    print(cm)
    
    return report, cm

def load_model(model_path, device=None):
    """
    Load a saved model
    
    Args:
        model_path: Path to the saved model
        device: Device to load the model on (default: auto-detect)
    
    Returns:
        Loaded model
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = MentalHealthClassifier().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    return model

def preprocess_suicide_detection_dataset(csv_path):
    """
    Preprocess the Suicide Detection dataset specifically
    
    Args:
        csv_path: Path to the Suicide_Detection.csv file
        
    Returns:
        Tuple of (train_data, val_data)
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Load dataset
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded dataset with {len(df)} samples")
    
    # Map classes to numerical values
    # 'suicide' -> 2 (high risk), 'non-suicide' -> 0 (no risk)
    label_map = {'suicide': 2, 'non-suicide': 0}
    df['label'] = df['class'].map(label_map)
    
    # Make sure all required columns exist
    if 'text' not in df.columns:
        raise ValueError("Dataset must contain a 'text' column")
    if 'label' not in df.columns:
        raise ValueError("Failed to create 'label' column from 'class' column")
        
    # Split into train/validation
    train_df, val_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df['label']
    )
    
    logger.info(f"Training samples: {len(train_df)}, Validation samples: {len(val_df)}")
    
    # Class balance info
    logger.info(f"Class distribution in training: {train_df['label'].value_counts()}")
    logger.info(f"Class distribution in validation: {val_df['label'].value_counts()}")
    
    return train_df, val_df
