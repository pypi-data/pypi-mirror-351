from transformers import BertTokenizer
import re

def clean_text(text):
    """
    Clean text by removing URLs, special characters, and normalizing whitespace
    
    Args:
        text: Input text string
        
    Returns:
        Cleaned text
    """
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove special characters but keep letters, numbers, and basic punctuation
    text = re.sub(r'[^\w\s.,!?]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize_text(texts, pretrained="bert-base-uncased", max_len=128):
    """
    Tokenize text for input to BERT model
    
    Args:
        texts: List of text strings or single text string
        pretrained: Pretrained model name
        max_len: Maximum sequence length
        
    Returns:
        Dictionary with input_ids and attention_mask
    """
    tokenizer = BertTokenizer.from_pretrained(pretrained)
    
    # Handle single string case
    if isinstance(texts, str):
        texts = [texts]
    
    # Clean texts
    cleaned_texts = [clean_text(text) for text in texts]
    
    # Tokenize
    encodings = tokenizer(
        cleaned_texts,
        padding='max_length',
        truncation=True,
        max_length=max_len,
        return_tensors='pt'
    )
    
    return encodings
