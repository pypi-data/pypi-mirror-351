"""
Model downloader utility for Guardian Mental Health package.
Downloads pre-trained models from GitHub releases when needed.
"""

import os
import requests
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class ModelDownloader:
    """Downloads and manages pre-trained model files."""
    
    GITHUB_RELEASES_URL = "https://api.github.com/repos/scoorpion1008/Guardian/releases/latest"
    MODEL_FILES = {
        "saved_model_fixed.pt": "pytorch_model.pt",
        "saved_model_fixed.onnx": "onnx_model.onnx",
        "model.onnx": "base_model.onnx"
    }
    
    def __init__(self, models_dir: Optional[str] = None):
        """Initialize downloader with models directory."""
        if models_dir is None:
            models_dir = Path(__file__).parent.parent / "models" / "checkpoints"
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def get_model_path(self, model_name: str) -> Path:
        """Get the local path for a model file."""
        return self.models_dir / model_name
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if model file exists locally."""
        return self.get_model_path(model_name).exists()
    
    def download_model(self, model_name: str, force: bool = False) -> Path:
        """
        Download a specific model file from GitHub releases.
        
        Args:
            model_name: Name of the model file to download
            force: Force re-download even if file exists
            
        Returns:
            Path to downloaded model file
        """
        local_path = self.get_model_path(model_name)
        
        if local_path.exists() and not force:
            logger.info(f"Model {model_name} already exists at {local_path}")
            return local_path
        
        try:
            # Get latest release info
            response = requests.get(self.GITHUB_RELEASES_URL)
            response.raise_for_status()
            release_data = response.json()
            
            # Find the model asset
            model_url = None
            for asset in release_data.get("assets", []):
                if asset["name"] == model_name:
                    model_url = asset["browser_download_url"]
                    break
            
            if not model_url:
                raise FileNotFoundError(f"Model {model_name} not found in latest release")
            
            logger.info(f"Downloading {model_name} from {model_url}")
            
            # Download the model
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            # Save to local file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Successfully downloaded {model_name} to {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download {model_name}: {e}")
            raise
    
    def ensure_model(self, model_name: str) -> Path:
        """
        Ensure model is available locally, download if needed.
        
        Args:
            model_name: Name of the model file
            
        Returns:
            Path to the model file
        """
        if not self.is_model_available(model_name):
            logger.info(f"Model {model_name} not found locally, downloading...")
            return self.download_model(model_name)
        return self.get_model_path(model_name)
    
    def download_all_models(self) -> dict:
        """Download all available models."""
        results = {}
        for model_name in self.MODEL_FILES.keys():
            try:
                path = self.download_model(model_name)
                results[model_name] = str(path)
            except Exception as e:
                results[model_name] = f"Error: {e}"
        return results


def get_model_path(model_name: str) -> str:
    """
    Convenience function to get model path, downloading if needed.
    
    Args:
        model_name: Name of the model file
        
    Returns:
        String path to the model file
    """
    downloader = ModelDownloader()
    return str(downloader.ensure_model(model_name))


if __name__ == "__main__":
    # Test the downloader
    logging.basicConfig(level=logging.INFO)
    downloader = ModelDownloader()
    results = downloader.download_all_models()
    
    print("Download results:")
    for model, result in results.items():
        print(f"  {model}: {result}")
