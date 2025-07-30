import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer

class MentalHealthClassifier(nn.Module):
    """
    BERT-based classifier for mental health risk assessment.
    
    This model classifies text into different risk categories:
    - 0: No risk
    - 1: Low risk
    - 2: High risk (suicidal ideation)
    """
    def __init__(self, pretrained="bert-base-uncased", num_classes=3):
        super().__init__()
        self.bert = BertModel.from_pretrained(pretrained)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(self.bert.config.hidden_size, num_classes)
        
    def forward(self, input_ids, attention_mask):
        """
        Forward pass through the model
        
        Args:
            input_ids: Tokenized input text
            attention_mask: Attention mask for padded sequences
            
        Returns:
            Logits for each class
        """
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        x = self.dropout(pooled_output)
        return self.fc(x)
    
    def predict(self, tokenized_text, device=None):
        """
        Make prediction on tokenized text
        
        Args:
            tokenized_text: Dictionary with 'input_ids' and 'attention_mask'
            device: Device to run inference on
            
        Returns:
            Tuple of (prediction class, probabilities)
        """
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
        self.eval()
        with torch.no_grad():
            input_ids = tokenized_text["input_ids"].to(device)
            attention_mask = tokenized_text["attention_mask"].to(device)
            outputs = self(input_ids, attention_mask)
            probs = torch.softmax(outputs, dim=1)
            prediction = torch.argmax(probs, dim=1)
            return prediction.item(), probs.squeeze().tolist()
