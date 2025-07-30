"""
Configuration for optimization strategies and backends
"""

import os
import logging
import torch

# Configure logger
logger = logging.getLogger(__name__)

# Detect available optimization libraries
PYTORCH_AVAILABLE = True  # Base requirement
CUDA_AVAILABLE = torch.cuda.is_available()
AMP_AVAILABLE = CUDA_AVAILABLE

# Check for ONNX
try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
    ort_providers = ort.get_available_providers()
    ONNX_GPU_AVAILABLE = 'CUDAExecutionProvider' in ort_providers or 'TensorrtExecutionProvider' in ort_providers
except ImportError:
    ONNX_AVAILABLE = False
    ONNX_GPU_AVAILABLE = False

# Check for TensorRT
try:
    import tensorrt as trt
    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False

# Optimization strategy configuration
OPTIMIZATION_CONFIG = {
    # Priority order of backends to try (first available will be used)
    "backend_priority": [
        "pytorch",   # Always available and most stable
        "onnx",      # Good balance of speed and compatibility
        "tensorrt"   # Fastest but requires specific hardware/drivers
    ],
    
    # Default settings for each backend
    "backend_settings": {
        "pytorch": {
            "use_amp": True,          # Use Automatic Mixed Precision when available
            "dynamic_batch_size": True,  # Dynamically adjust batch size
            "default_batch_size": 16     # Default if auto-tuning fails
        },
        "onnx": {
            "use_gpu": True,          # Try to use GPU with ONNX Runtime
            "force_int64": True,      # Convert int32 tensors to int64 for compatibility
            "fallback_to_pytorch": True   # Fall back to PyTorch if ONNX fails
        },
        "tensorrt": {
            "precision": "fp16",      # "fp32", "fp16", or "int8"
            "fallback_to_onnx": True,   # Fall back to ONNX if TensorRT fails
            "workspace_size_gb": 2      # GPU memory to use for optimization
        }
    },
    
    # Feature flags for controlling optimizations
    "features": {
        "enable_caching": True,        # Cache models for faster loading
        "auto_fix_models": True,       # Automatically try to fix model issues
        "verbose_logging": False,      # Detailed performance logging
        "benchmark_on_startup": False  # Run benchmark on first initialization
    }
}

# Get preferred backend based on available libraries
def get_preferred_backend():
    """
    Get the best available backend based on priority order and availability
    """
    for backend in OPTIMIZATION_CONFIG["backend_priority"]:
        if backend == "pytorch":
            return "pytorch"
        elif backend == "onnx" and ONNX_AVAILABLE:
            return "onnx"
        elif backend == "tensorrt" and TENSORRT_AVAILABLE and CUDA_AVAILABLE:
            return "tensorrt"
    
    # Default fallback
    return "pytorch"

# Export availability flags
__all__ = [
    "PYTORCH_AVAILABLE",
    "CUDA_AVAILABLE", 
    "AMP_AVAILABLE",
    "ONNX_AVAILABLE",
    "ONNX_GPU_AVAILABLE",
    "TENSORRT_AVAILABLE",
    "OPTIMIZATION_CONFIG",
    "get_preferred_backend"
]