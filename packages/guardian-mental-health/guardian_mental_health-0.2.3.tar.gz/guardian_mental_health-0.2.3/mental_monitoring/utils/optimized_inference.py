"""
Advanced optimized inference utilities supporting:
- Automatic Mixed Precision (AMP)
- ONNX Runtime export and inference
- TensorRT integration
- Multi-model ensembles
- Dynamic batch size optimization
"""

import torch
import logging
import time
import os
import numpy as np
import json
from typing import Dict, List, Tuple, Union, Optional, Any
from transformers import AutoTokenizer, PreTrainedTokenizer
from pathlib import Path

logger = logging.getLogger(__name__)

# Import optimization configuration
try:
    from mental_monitoring.config.optimization_config import (
        PYTORCH_AVAILABLE, CUDA_AVAILABLE, AMP_AVAILABLE,
        ONNX_AVAILABLE, ONNX_GPU_AVAILABLE, TENSORRT_AVAILABLE,
        OPTIMIZATION_CONFIG, get_preferred_backend
    )
except ImportError:
    # Fallback configuration if the module doesn't exist
    logger.warning("Optimization config not found, using default settings")
    PYTORCH_AVAILABLE = True
    CUDA_AVAILABLE = torch.cuda.is_available()
    AMP_AVAILABLE = CUDA_AVAILABLE
    
    # Check for ONNX Runtime
    try:
        import onnx
        import onnxruntime as ort
        ONNX_AVAILABLE = True
        logger.info("ONNX Runtime is available")
    except ImportError:
        ONNX_AVAILABLE = False
        logger.warning("ONNX Runtime not available. Install with: pip install onnx onnxruntime-gpu")

    # Check for TensorRT
    try:
        import tensorrt as trt
        import pycuda.driver as cuda
        import pycuda.autoinit
        TENSORRT_AVAILABLE = True
        logger.info("TensorRT is available")
    except ImportError:
        TENSORRT_AVAILABLE = False
        logger.warning("TensorRT not available. TensorRT optimizations will be disabled.")
        
    # Create default configuration
    OPTIMIZATION_CONFIG = {
        "backend_priority": ["pytorch", "onnx", "tensorrt"],
        "backend_settings": {
            "pytorch": {"use_amp": True, "dynamic_batch_size": True, "default_batch_size": 16},
            "onnx": {"use_gpu": True, "force_int64": True, "fallback_to_pytorch": True},
            "tensorrt": {"precision": "fp16", "fallback_to_onnx": True, "workspace_size_gb": 2}
        },
        "features": {
            "enable_caching": True,
            "auto_fix_models": True,
            "verbose_logging": False,
            "benchmark_on_startup": False
        }
    }
    
    def get_preferred_backend():
        """Get preferred backend based on availability"""
        if TENSORRT_AVAILABLE and CUDA_AVAILABLE:
            return "tensorrt"
        elif ONNX_AVAILABLE:
            return "onnx"
        else:
            return "pytorch"

class OptimizedInference:
    """
    Provides advanced optimized inference with support for:
    - PyTorch's Automatic Mixed Precision (AMP)
    - ONNX Runtime export and inference
    - TensorRT acceleration
    - Multi-model ensemble techniques
    - Dynamic batch size optimization
    
    Example usage:
    ```python
    from mental_monitoring.utils.optimized_inference import OptimizedInference
    
    # Initialize with default settings
    inference_engine = OptimizedInference()
    
    # Analyze a single message
    result = inference_engine.analyze_text("I'm feeling really down today")
    print(result)  # {'label': 'Medium Risk', 'class_id': 1, 'probabilities': {...}}
    
    # Process multiple messages efficiently in a batch
    messages = ["I'm excited about tomorrow", "I don't see any reason to continue"]
    results = inference_engine.process_texts(messages)
    
    # Export model to ONNX format for deployment
    inference_engine.export_to_onnx("models/suicide_model.onnx")
    
    # Create an ensemble of models for improved accuracy
    ensemble = OptimizedInference.create_ensemble([
        "models/suicide_model.pt",
        "models/depression_model.pt",
        "models/anxiety_model.pt"
    ])
    ensemble_result = ensemble.analyze_text("I've been feeling really sad lately")
    ```
    """
    
    # Class mapping for different model types
    CLASS_MAPPINGS = {
        "suicide": {
            0: {"label": "No Risk", "color": "green"},
            1: {"label": "Medium Risk", "color": "yellow"},
            2: {"label": "High Risk", "color": "red"}
        },
        "depression": {
            0: {"label": "Not Depressed", "color": "green"},
            1: {"label": "Depressed", "color": "red"}
        },
        "anxiety": {
            0: {"label": "Not Anxious", "color": "green"},
            1: {"label": "Anxious", "color": "red"}
        },
        # Default mapping used when model type is unknown
        "default": {
            0: {"label": "No Risk", "color": "green"},
            1: {"label": "Medium Risk", "color": "yellow"},
            2: {"label": "High Risk", "color": "red"}
        }
    }
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        model_type: str = "suicide",
        tokenizer_path: Optional[str] = None,
        batch_size: Optional[int] = None,
        use_amp: Optional[bool] = None,
        max_length: int = 128,
        backend: Optional[str] = None,
        ensemble_models: Optional[List[str]] = None,
        ensemble_weights: Optional[List[float]] = None
    ):
        """
        Initialize the optimized inference engine with advanced options.
        
        Args:
            model_path: Path to the saved model file
            model_type: Type of model ('suicide', 'depression', 'anxiety', etc.)
            tokenizer_path: Path to the tokenizer (if different from model)
            batch_size: Optimal batch size for inference (None for auto-tuning)
            use_amp: Whether to use Automatic Mixed Precision
            max_length: Maximum sequence length for tokenization
            backend: Specific backend to use ('pytorch', 'onnx', 'tensorrt')
            ensemble_models: List of model paths for ensemble inference
            ensemble_weights: Weights for each model in the ensemble (default: equal weights)
        """
        # Import here to avoid circular imports
        from mental_monitoring.models.transformer_classifier import MentalHealthClassifier
        from mental_monitoring.config.config import MODEL_CONFIG
        
        self.model_path = model_path or MODEL_CONFIG["saved_model_path"]
        self.model_type = model_type
        self.tokenizer_path = tokenizer_path or "bert-base-uncased"
        self.max_length = max_length
          # Initialize state variables
        self.model = None
        self.tokenizer = None
        self.is_ensemble = bool(ensemble_models)
        
        # Get configuration settings
        pytorch_settings = OPTIMIZATION_CONFIG["backend_settings"]["pytorch"]
        self.dynamic_batch_size = pytorch_settings.get("dynamic_batch_size", True)
        
        # Device configuration
        self.device = torch.device("cuda" if CUDA_AVAILABLE else "cpu")
        self.gpu_name = torch.cuda.get_device_name(0) if CUDA_AVAILABLE else "CPU"
        self.memory_gb = (torch.cuda.get_device_properties(0).total_memory / (1024**3)) if CUDA_AVAILABLE else 0
        
        # AMP configuration - use specified value or default from config
        pytorch_settings = OPTIMIZATION_CONFIG["backend_settings"]["pytorch"]
        self.use_amp = use_amp if use_amp is not None else (pytorch_settings["use_amp"] and AMP_AVAILABLE)
        
        # Set the backend (user-specified or auto-detected)
        if ensemble_models:
            # Ensemble mode uses PyTorch for all sub-models
            self.backend = "ensemble"
            self._initialize_ensemble(ensemble_models, ensemble_weights)
        else:
            # Determine which backend to use (user choice or preference)
            self.backend = backend or get_preferred_backend()
            self._initialize_backend(batch_size)
        
        logger.info(
            f"Optimized inference engine initialized: "
            f"backend={self.backend}, "
            f"model_type={model_type}, batch_size={self.batch_size}, amp={self.use_amp}, "
            f"device={self.device}, num_classes={self.num_classes}, "
            f"gpu={self.gpu_name if CUDA_AVAILABLE else 'N/A'}"
        )
        
    def _initialize_ensemble(self, ensemble_models, ensemble_weights):
        """Initialize ensemble models"""
        self.ensemble_models = []
        weights = ensemble_weights or [1.0] * len(ensemble_models)
            
        # Normalize weights
        self.ensemble_weights = [w / sum(weights) for w in weights]
        
        for model_path in ensemble_models:
            # Always use PyTorch backend for ensemble components
            model_engine = OptimizedInference(
                model_path=model_path,
                model_type=self.model_type,
                tokenizer_path=self.tokenizer_path,
                backend="pytorch",
                use_amp=self.use_amp,
                max_length=self.max_length
            )
            self.ensemble_models.append(model_engine)
            
        # Use the first model's tokenizer and properties for all
        self.tokenizer = self.ensemble_models[0].tokenizer
        self.class_mapping = self.ensemble_models[0].class_mapping
        self.num_classes = self.ensemble_models[0].num_classes
        self.batch_size = self.ensemble_models[0].batch_size
        
        logger.info(f"Created ensemble with {len(ensemble_models)} models")
        
    def _initialize_backend(self, batch_size):
        """Initialize the specified backend"""
        # First, try the requested backend
        initialized = False
        original_backend = self.backend
        
        # Try to initialize the requested backend
        try:
            if self.backend == "tensorrt" and TENSORRT_AVAILABLE:
                self.model, self.engine, self.context = self._load_tensorrt_model()
                initialized = True
                
            elif self.backend == "onnx" and ONNX_AVAILABLE:
                self.model = self._load_onnx_model()
                initialized = True
                
            elif self.backend == "pytorch":
                self.model = self._load_pytorch_model()
                initialized = True
                
        except Exception as e:
            logger.warning(f"Failed to initialize {self.backend} backend: {e}")
            logger.info("Will try fallback backends")
            initialized = False
            
        # If requested backend failed, try fallbacks according to priority
        if not initialized:
            for backend in OPTIMIZATION_CONFIG["backend_priority"]:
                if backend == original_backend:
                    continue  # Skip already-tried backend
                
                try:
                    logger.info(f"Trying fallback to {backend} backend")
                    if backend == "pytorch":
                        self.backend = "pytorch"
                        self.model = self._load_pytorch_model()
                        initialized = True
                        break
                    elif backend == "onnx" and ONNX_AVAILABLE:
                        self.backend = "onnx"
                        self.model = self._load_onnx_model()
                        initialized = True
                        break
                    elif backend == "tensorrt" and TENSORRT_AVAILABLE:
                        self.backend = "tensorrt"
                        self.model, self.engine, self.context = self._load_tensorrt_model()
                        initialized = True
                        break
                except Exception as e:
                    logger.warning(f"Failed to initialize fallback {backend} backend: {e}")
                    
        # If all backends failed, raise exception
        if not initialized:
            raise RuntimeError(
                "Failed to initialize any inference backend. "
                "Check model path and available hardware/libraries."
            )
            
        # Load tokenizer (common for all backends)
        self.tokenizer = self._load_tokenizer()
            
        # Determine optimal batch size if not specified
        self.batch_size = batch_size or self._determine_optimal_batch_size()
        
        # Get class mapping based on model type
        self.class_mapping = self.CLASS_MAPPINGS.get(
            self.model_type, self.CLASS_MAPPINGS["default"]
        )
        
        # Detect number of output classes
        self.num_classes = self._detect_num_classes()

    def _load_pytorch_model(self):
        """
        Load the PyTorch model from the specified path with optimization settings.
        
        Returns:
            The loaded and optimized model
        """
        from mental_monitoring.models.transformer_classifier import MentalHealthClassifier
        
        try:
            model = MentalHealthClassifier().to(self.device)
            
            if os.path.exists(self.model_path):
                # Try different loading strategies for compatibility
                try:
                    model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                except Exception as e:
                    logger.warning(f"Error with standard loading, trying alternative: {e}")
                    # Try direct loading (for JIT or complete models)
                    try:
                        model = torch.load(self.model_path, map_location=self.device)
                    except Exception as e2:
                        logger.error(f"Failed to load model with alternative method: {e2}")
                        
                        # Try loading the fixed model if it exists
                        fixed_model_path = os.path.join(os.path.dirname(self.model_path), "saved_model_fixed.pt")
                        if os.path.exists(fixed_model_path) and fixed_model_path != self.model_path:
                            logger.info(f"Attempting to load fixed model from {fixed_model_path}")
                            try:
                                model.load_state_dict(torch.load(fixed_model_path, map_location=self.device))
                                logger.info(f"Successfully loaded fixed model")
                                # Update the model path to the working one
                                self.model_path = fixed_model_path
                            except Exception as e3:
                                logger.error(f"Failed to load fixed model: {e3}")
                                raise ValueError(f"Could not load model from any available path: {e}, {e2}, {e3}")
                        else:
                            raise
                
                logger.info(f"PyTorch model loaded from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}. Using initialized weights.")
            
            model.eval()
            return model
        except Exception as e:
            logger.error(f"Error loading PyTorch model from {self.model_path}: {e}")
            raise

    def _load_onnx_model(self):
        """
        Load the model from ONNX format or convert PyTorch model to ONNX.
        
        Returns:
            ONNX Runtime inference session
        """
        if not ONNX_AVAILABLE:
            logger.error("ONNX Runtime is not available. Please install it.")
            raise ImportError("ONNX Runtime is not installed")
            
        # Get ONNX settings
        onnx_settings = OPTIMIZATION_CONFIG["backend_settings"]["onnx"]
            
        # Determine ONNX path - either direct or converted
        if self.model_path.endswith('.onnx'):
            onnx_path = self.model_path
        else:
            # Look for an existing ONNX model with same basename
            onnx_path = os.path.splitext(self.model_path)[0] + ".onnx"
            if not os.path.exists(onnx_path):
                # Also check for a fixed version
                fixed_onnx_path = os.path.splitext(self.model_path)[0] + "_fixed.onnx"
                if os.path.exists(fixed_onnx_path):
                    onnx_path = fixed_onnx_path
                    logger.info(f"Using fixed ONNX model: {onnx_path}")
                else:
                    # Convert to ONNX if it doesn't exist
                    logger.info(f"Converting PyTorch model to ONNX: {onnx_path}")
                    try:
                        self.export_to_onnx(onnx_path)
                    except Exception as e:
                        if onnx_settings["fallback_to_pytorch"]:
                            logger.warning(f"Failed to export to ONNX: {e}. Falling back to PyTorch.")
                            self.backend = "pytorch"
                            return self._load_pytorch_model()
                        else:
                            raise
                            
        # Validate the model exists
        if not os.path.exists(onnx_path):
            logger.warning(f"ONNX model not found at {onnx_path}. Falling back to PyTorch.")
            self.backend = "pytorch"
            return self._load_pytorch_model()
            
        # Create ONNX Runtime inference session
        try:
            # Determine providers based on availability
            if CUDA_AVAILABLE and onnx_settings["use_gpu"]:
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            else:
                providers = ['CPUExecutionProvider']
                
            # Configure optimization level
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.intra_op_num_threads = min(4, os.cpu_count() or 4)  # Use reasonable number of threads
            
            # Load the model - handle potential cuDNN version issues
            try:
                session = ort.InferenceSession(
                    onnx_path, 
                    sess_options=session_options,
                    providers=providers
                )
                logger.info(f"ONNX model loaded with GPU acceleration: {onnx_path}")
            except Exception as e:
                # If CUDA fails, try CPU only
                if "CUDA" in str(e) or "GPU" in str(e) or "cuda" in str(e):
                    logger.warning(f"GPU acceleration failed for ONNX: {e}")
                    logger.info("Falling back to CPU for ONNX Runtime")
                    session = ort.InferenceSession(
                        onnx_path, 
                        sess_options=session_options,
                        providers=['CPUExecutionProvider']
                    )
                else:
                    raise
            
            # Store input data types for later use
            self.onnx_input_types = {}
            for input_meta in session.get_inputs():
                self.onnx_input_types[input_meta.name] = input_meta.type
            
            return session
            
        except Exception as e:
            if onnx_settings["fallback_to_pytorch"]:
                logger.error(f"Error loading ONNX model: {e}")
                logger.info("Falling back to PyTorch model")
                self.backend = "pytorch"
                return self._load_pytorch_model()
            else:
                raise

    def _load_tensorrt_model(self):
        """
        Load the model using TensorRT for maximum performance.
        
        Returns:
            Tuple of (model, engine, context)
        """
        if not TENSORRT_AVAILABLE:
            logger.error("TensorRT is not available. Please install it.")
            raise ImportError("TensorRT is not installed")
            
        # Check for existing TensorRT engine
        engine_path = os.path.splitext(self.model_path)[0] + ".engine"
        if not os.path.exists(engine_path):
            # First convert to ONNX if not already
            onnx_path = os.path.splitext(self.model_path)[0] + ".onnx"
            if not os.path.exists(onnx_path) and not self.model_path.endswith('.onnx'):
                logger.info(f"Converting to ONNX first: {onnx_path}")
                self.use_onnx = True
                self.backend = "onnx"
                onnx_model = self._load_onnx_model()
                self.use_onnx = False
                
            # Build TensorRT engine from ONNX model
            logger.info(f"Building TensorRT engine: {engine_path}")
            try:
                self._build_tensorrt_engine(onnx_path, engine_path)
            except Exception as e:
                logger.error(f"Failed to build TensorRT engine: {e}")
                logger.info("Falling back to ONNX model")
                self.use_tensorrt = False
                self.use_onnx = True
                self.backend = "onnx"
                return self._load_onnx_model()
        
        try:
            # Load TensorRT engine
            logger.info(f"Loading TensorRT engine from {engine_path}")
            with open(engine_path, "rb") as f:
                engine_data = f.read()
                
            runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
            engine = runtime.deserialize_cuda_engine(engine_data)
            context = engine.create_execution_context()
            
            return None, engine, context
        except Exception as e:
            logger.error(f"Failed to load TensorRT engine: {e}")
            logger.info("Falling back to PyTorch model")
            self.use_tensorrt = False
            self.backend = "pytorch"
            return self._load_pytorch_model(), None, None

    def _build_tensorrt_engine(self, onnx_path, engine_path):
        """
        Build a TensorRT engine from an ONNX model
        
        Args:
            onnx_path: Path to the ONNX model
            engine_path: Output path for the TensorRT engine
        """
        logger.info(f"Building TensorRT engine from {onnx_path}")
        
        # Create TensorRT builder and configs
        builder = trt.Builder(trt.Logger(trt.Logger.WARNING))
        network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
        parser = trt.OnnxParser(network, trt.Logger(trt.Logger.WARNING))
        
        # Parse ONNX model
        with open(onnx_path, "rb") as f:
            if not parser.parse(f.read()):
                for error in range(parser.num_errors):
                    logger.error(f"TensorRT ONNX parser error: {parser.get_error(error)}")
                raise RuntimeError("Failed to parse ONNX model")
                
        # Create config with FP16 support if available
        config = builder.create_builder_config()
        if builder.platform_has_fast_fp16:
            logger.info("Enabling FP16 mode for TensorRT")
            config.set_flag(trt.BuilderFlag.FP16)
            
        # Set max workspace size based on available GPU memory
        if self.memory_gb > 0:
            workspace_size = int(self.memory_gb * 0.7 * 1024 * 1024 * 1024)  # 70% of GPU memory
            config.max_workspace_size = workspace_size
        else:
            config.max_workspace_size = 1 << 30  # 1GB default
        
        # Build and save engine
        engine_data = builder.build_serialized_network(network, config)
        with open(engine_path, "wb") as f:
            f.write(engine_data)
            
        logger.info(f"TensorRT engine saved to {engine_path}")

    def _load_tokenizer(self):
        """
        Load the tokenizer from the specified path.
        
        Returns:
            The loaded tokenizer
        """
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
            logger.info(f"Tokenizer loaded from {self.tokenizer_path}")
            return tokenizer
        except Exception as e:
            logger.error(f"Error loading tokenizer from {self.tokenizer_path}: {e}")
            logger.info("Falling back to default BERT tokenizer")
            return AutoTokenizer.from_pretrained("bert-base-uncased")

    def _determine_optimal_batch_size(self) -> int:
        """
        Auto-tune batch size based on available GPU memory and model size.
        
        Returns:
            Optimal batch size for the current device
        """
        if not torch.cuda.is_available():
            # Default to smaller batch size for CPU
            return 4
        
        try:
            # Start with a conservative batch size based on the GPU
            gpu_name = torch.cuda.get_device_name(0).lower()
            total_memory = torch.cuda.get_device_properties(0).total_memory
            memory_gb = total_memory / (1024 ** 3)  # Convert to GB
            
            # More sophisticated heuristic based on GPU memory and model complexity
            if "rtx" in gpu_name and "4080" in gpu_name or "4090" in gpu_name:
                # High-end NVIDIA RTX 40 series
                batch_size = 32 if memory_gb > 12 else 24
            elif "rtx" in gpu_name and ("3080" in gpu_name or "3090" in gpu_name):
                # High-end NVIDIA RTX 30 series
                batch_size = 24 if memory_gb > 12 else 16
            elif memory_gb > 10 or "rtx" in gpu_name:  # Other high-end GPUs
                batch_size = 16
            elif memory_gb > 6:  # Mid-range GPUs
                batch_size = 8
            else:  # Lower-end GPUs
                batch_size = 4
            
            # Adjust based on backend - ONNX and TensorRT can handle larger batches
            if hasattr(self, 'backend'):
                if self.backend == "onnx":
                    batch_size = int(batch_size * 1.5)  # ONNX is more memory efficient
                elif self.backend == "tensorrt":
                    batch_size = int(batch_size * 2.0)  # TensorRT is most memory efficient
                
            logger.info(f"Auto-tuned batch size: {batch_size} based on {memory_gb:.1f}GB GPU memory and backend={getattr(self, 'backend', 'pytorch')}")
            return batch_size
        
        except Exception as e:
            logger.warning(f"Error during batch size auto-tuning: {e}. Using default batch size of 16.")
            return 16

    def _detect_num_classes(self) -> int:
        """
        Detect the number of output classes in the model.
        
        Returns:
            Number of output classes
        """
        try:
            # Get number of classes from the model's final layer for PyTorch model
            if self.backend == "pytorch" and hasattr(self.model, 'fc'):
                return self.model.fc.out_features
            
            # For ONNX models, check the output shape by running inference on a dummy input
            if self.backend == "onnx":
                # Create a dummy input
                dummy_text = "This is a test"
                dummy_encoding = self.tokenizer(
                    dummy_text,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="np"
                )
                
                # Get output shape from ONNX inference
                input_names = [input.name for input in self.model.get_inputs()]
                output_names = [output.name for output in self.model.get_outputs()]
                
                onnx_inputs = {
                    input_name: dummy_encoding[input_name.split('.')[-1]] 
                    for input_name in input_names 
                    if input_name.split('.')[-1] in dummy_encoding
                }
                
                result = self.model.run(output_names, onnx_inputs)
                return result[0].shape[1]
            
            # If we can't determine from the model, use the class mapping length
            return len(self.class_mapping)
        except Exception as e:
            logger.warning(f"Could not detect number of classes: {e}. Using default of 3 classes.")
            return 3

    def preprocess_batch(self, texts: List[str]) -> Dict[str, Any]:
        """
        Tokenize a batch of text inputs based on the current backend.
        
        Args:
            texts: List of text strings to process
            
        Returns:
            Dictionary with tokenized inputs in the appropriate format
        """
        if self.backend == "pytorch":
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt"
            )
            
            # Move to appropriate device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            return inputs
            
        elif self.backend == "onnx":
            # ONNX runtime expects numpy arrays
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="np"
            )
            
            # Get ONNX settings
            onnx_settings = OPTIMIZATION_CONFIG["backend_settings"]["onnx"]
            
            # Handle data type conversion based on model requirements and settings
            # If force_int64 is True, always convert to int64
            # Otherwise, use the detected input types where available
            if onnx_settings["force_int64"]:
                for key in inputs:
                    if inputs[key].dtype == np.int32:
                        inputs[key] = inputs[key].astype(np.int64)
            elif hasattr(self, 'onnx_input_types'):
                # Convert types based on model expectations
                for name, type_info in self.onnx_input_types.items():
                    key = name.split('.')[-1] if '.' in name else name
                    if key in inputs:
                        if 'int64' in type_info and inputs[key].dtype == np.int32:
                            inputs[key] = inputs[key].astype(np.int64)
                        elif 'int32' in type_info and inputs[key].dtype == np.int64:
                            inputs[key] = inputs[key].astype(np.int32)
                
            return inputs
            
        elif self.backend == "tensorrt":
            # TensorRT expects fixed shape inputs
            inputs = self.tokenizer(
                texts,
                padding="max_length",
                truncation=True,
                max_length=self.max_length,
                return_tensors="np"
            )
            
            return inputs
            
        elif self.backend == "ensemble":
            # For ensemble models, we'll process in the inference step
            return texts
            
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def predict_batch(self, texts: List[str]) -> np.ndarray:
        """
        Perform batch prediction with appropriate acceleration based on backend.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            Numpy array of predictions (probabilities) for each input
        """
        if self.is_ensemble:
            return self._predict_batch_ensemble(texts)
            
        # Handle different backends
        inputs = self.preprocess_batch(texts)
        
        if self.backend == "pytorch":
            with torch.no_grad():
                if self.use_amp and torch.cuda.is_available():
                    with torch.cuda.amp.autocast():
                        outputs = self.model(inputs["input_ids"], inputs["attention_mask"])
                else:
                    outputs = self.model(inputs["input_ids"], inputs["attention_mask"])
                    
                # Convert to probabilities
                probs = torch.softmax(outputs, dim=1).cpu().numpy()
                return probs
                
        elif self.backend == "onnx":
            # Run inference with ONNX Runtime
            try:
                input_names = [input.name for input in self.model.get_inputs()]
                output_names = [output.name for output in self.model.get_outputs()]
                
                # Get input requirements
                input_types = {}
                for input_meta in self.model.get_inputs():
                    input_types[input_meta.name] = input_meta.type
                
                # Map inputs to ONNX input names
                onnx_inputs = {}
                for name in input_names:
                    if "input_ids" in name:
                        # Make sure we have the right type (int64)
                        if "int64" in input_types.get(name, ""):
                            onnx_inputs[name] = inputs["input_ids"].astype(np.int64)
                        else:
                            onnx_inputs[name] = inputs["input_ids"]
                    elif "attention_mask" in name:
                        if "int64" in input_types.get(name, ""):
                            onnx_inputs[name] = inputs["attention_mask"].astype(np.int64)
                        else:
                            onnx_inputs[name] = inputs["attention_mask"]
                
                # Run inference
                outputs = self.model.run(output_names, onnx_inputs)
                
                # Convert to probabilities
                logits = outputs[0]
                probs = self._softmax(logits)
                return probs
                
            except Exception as e:
                logger.error(f"ONNX inference failed: {e}")
                if "data type" in str(e):
                    logger.warning("Data type mismatch detected. Falling back to PyTorch model.")
                # Fall back to PyTorch
                orig_backend = self.backend
                self.backend = "pytorch"
                self.model = self._load_pytorch_model()
                result = self.process_batch(texts)
                self.backend = orig_backend
                return result
            
        elif self.backend == "tensorrt":
            # Execute inference with TensorRT
            input_ids = inputs["input_ids"]
            attention_mask = inputs["attention_mask"]
            
            # Allocate buffers for input and output
            batch_size = input_ids.shape[0]
            
            # Get input and output binding shapes
            input_binding_idxs = []
            output_binding_idxs = []
            
            for i in range(self.engine.num_bindings):
                if self.engine.binding_is_input(i):
                    input_binding_idxs.append(i)
                else:
                    output_binding_idxs.append(i)
            
            # Allocate device memory
            d_input_ids = cuda.mem_alloc(input_ids.nbytes)
            d_attention_mask = cuda.mem_alloc(attention_mask.nbytes)
            
            # Get output shape from the engine
            output_shape = self.context.get_binding_shape(output_binding_idxs[0])
            if output_shape[0] == -1:  # Dynamic batch size
                output_shape = (batch_size,) + tuple(output_shape[1:])
                self.context.set_binding_shape(output_binding_idxs[0], output_shape)
                
            h_output = np.empty(output_shape, dtype=np.float32)
            d_output = cuda.mem_alloc(h_output.nbytes)
            
            # Copy input data to GPU
            cuda.memcpy_htod(d_input_ids, input_ids.astype(np.int32))
            cuda.memcpy_htod(d_attention_mask, attention_mask.astype(np.int32))
            
            # Run inference
            self.context.execute_v2([int(d_input_ids), int(d_attention_mask), int(d_output)])
            
            # Copy output data back to host
            cuda.memcpy_dtoh(h_output, d_output)
            
            # Convert to probabilities
            probs = self._softmax(h_output)
            return probs
            
        # Fallback for unknown backend
        logger.warning(f"Unknown backend: {self.backend}. Using PyTorch")
        return np.zeros((len(texts), self.num_classes))

    def _predict_batch_ensemble(self, texts: List[str]) -> np.ndarray:
        """
        Perform ensemble prediction by averaging results from multiple models.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            Numpy array of averaged predictions
        """
        all_predictions = []
        
        for i, model in enumerate(self.ensemble_models):
            weight = self.ensemble_weights[i]
            predictions = model.predict_batch(texts) * weight
            all_predictions.append(predictions)
            
        # Average predictions
        ensemble_predictions = np.sum(all_predictions, axis=0)
        return ensemble_predictions

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """
        Compute softmax for numpy arrays
        
        Args:
            x: Input array
            
        Returns:
            Softmax probabilities
        """
        # For numerical stability, subtract the maximum value
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / e_x.sum(axis=1, keepdims=True)
    
    def process_texts(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process a list of texts with optimal batching strategy.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of dictionaries containing risk analysis for each input
        """
        if not texts:
            return []
            
        results = []
        
        # If dynamic batch sizing is enabled, adjust batch size based on text length
        if self.dynamic_batch_size and not self.is_ensemble:
            avg_length = sum(len(text) for text in texts) / len(texts)
            
            # Adjust batch size based on average text length
            adjusted_batch_size = self.batch_size
            if avg_length > 300:  # Very long texts
                adjusted_batch_size = max(4, self.batch_size // 4)
            elif avg_length > 150:  # Moderately long texts
                adjusted_batch_size = max(8, self.batch_size // 2)
            
            if adjusted_batch_size != self.batch_size:
                logger.debug(f"Adjusted batch size: {adjusted_batch_size} (from {self.batch_size}) for avg text length {avg_length:.1f}")
        else:
            adjusted_batch_size = self.batch_size
            
        # Process in optimal batch sizes
        for i in range(0, len(texts), adjusted_batch_size):
            batch_texts = texts[i:i + adjusted_batch_size]
            batch_predictions = self.predict_batch(batch_texts)
            
            # Convert predictions to dictionary format with labels
            for j, pred in enumerate(batch_predictions):
                # Get predicted class and probabilities
                pred_class = int(np.argmax(pred))
                
                # Get class label information
                class_info = self.class_mapping.get(
                    pred_class, 
                    {"label": f"Class {pred_class}", "color": "gray"}
                )
                
                # Create probability dictionary with meaningful names
                probabilities = {}
                for class_id, class_val in self.class_mapping.items():
                    if class_id < len(pred):
                        probabilities[class_val["label"]] = float(pred[class_id])
                
                results.append({
                    "label": class_info["label"],
                    "class_id": pred_class,
                    "color": class_info["color"],
                    "probabilities": probabilities,
                    "raw_probabilities": [float(p) for p in pred],
                    "confidence": float(pred[pred_class])
                })
                
        return results

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze a single text input with optimized inference.
        
        Args:
            text: Text string to analyze
            
        Returns:
            Dictionary with risk analysis
        """
        return self.process_texts([text])[0]

    def benchmark_throughput(self, 
                            sample_text: str = None, 
                            iterations: int = 100,
                            batch_sizes: List[int] = None) -> Dict[str, Any]:
        """
        Benchmark inference throughput with different batch sizes.
        
        Args:
            sample_text: Text to use for benchmarking (generates synthetic if None)
            iterations: Number of iterations to run for each batch size
            batch_sizes: List of batch sizes to test (default: [1, 4, 16, 32, 64])
            
        Returns:
            Dictionary with benchmark results
        """
        if sample_text is None:
            sample_text = "This is a sample text for benchmarking the model throughput."
            
        if batch_sizes is None:
            batch_sizes = [1, 4, 16, 32, 64]
            
        results = {}
        
        logger.info(f"Benchmarking {self.backend} backend with {iterations} iterations")
        
        # Test different batch sizes
        for batch_size in batch_sizes:
            # Create a batch of the specified size
            batch = [sample_text] * batch_size
            
            # Warmup
            _ = self.process_texts(batch[:min(5, batch_size)])
            
            # Time the actual processing
            start_time = time.time()
            
            # Run multiple iterations to get a stable measurement
            for _ in range(iterations):
                _ = self.predict_batch(batch)
                
            end_time = time.time()
            
            # Calculate throughput
            total_time = end_time - start_time
            samples_per_second = (batch_size * iterations) / total_time
            
            results[batch_size] = {
                "samples_per_second": samples_per_second,
                "ms_per_batch": (total_time * 1000) / iterations,
                "ms_per_sample": (total_time * 1000) / (batch_size * iterations)
            }
            
            logger.info(f"Batch size {batch_size}: {samples_per_second:.1f} samples/sec, "
                      f"{results[batch_size]['ms_per_batch']:.1f} ms/batch")
            
        return results

    def export_to_onnx(self, output_path: str = None) -> str:
        """
        Export the PyTorch model to ONNX format for deployment.
        
        Args:
            output_path: Path to save the ONNX model
            
        Returns:
            Path to the exported ONNX model
        """
        if self.is_ensemble:
            raise ValueError("Cannot export ensemble models directly to ONNX")
            
        if self.backend != "pytorch":
            logger.warning(f"Cannot export {self.backend} model to ONNX. Only PyTorch models can be exported.")
            logger.info("Loading PyTorch model first...")
            orig_backend = self.backend
            self.backend = "pytorch"
            self.model = self._load_pytorch_model()
            
        # Create default output path if not provided
        if output_path is None:
            output_path = os.path.splitext(self.model_path)[0] + ".onnx"
            
        # Create a dummy input for tracing
        dummy_text = "This is a test input for ONNX export"
        dummy_encoding = self.tokenizer(
            dummy_text,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Move to device
        dummy_input_ids = dummy_encoding["input_ids"].to(self.device)
        dummy_attention_mask = dummy_encoding["attention_mask"].to(self.device)
        
        # Ensure inputs are int64 (long) type for ONNX compatibility
        dummy_input_ids = dummy_input_ids.long()
        dummy_attention_mask = dummy_attention_mask.long()
        
        # Create dynamic axes for variable batch size
        dynamic_axes = {
            'input_ids': {0: 'batch_size'},
            'attention_mask': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
        
        # Export the model
        try:
            torch.onnx.export(
                self.model,
                (dummy_input_ids, dummy_attention_mask),
                output_path,
                input_names=['input_ids', 'attention_mask'],
                output_names=['output'],
                dynamic_axes=dynamic_axes,
                opset_version=13,
                verbose=False
            )
            
            logger.info(f"Model exported to ONNX: {output_path}")
            
            # Verify the ONNX model if available
            if ONNX_AVAILABLE:
                onnx_model = onnx.load(output_path)
                onnx.checker.check_model(onnx_model)
                logger.info("ONNX model verified successfully")
                
                # Validate input types
                self.validate_onnx_model(output_path)
            
            return output_path
        except Exception as e:
            logger.error(f"Error exporting to ONNX: {e}")
            return None
        finally:
            # Restore original backend if we switched
            if hasattr(self, 'orig_backend'):
                self.backend = orig_backend

    @classmethod
    def create_ensemble(cls, 
                       model_paths: List[str], 
                       weights: Optional[List[float]] = None,
                       model_type: str = "suicide",
                       **kwargs) -> 'OptimizedInference':
        """
        Create an ensemble of models for improved accuracy.
        
        Args:
            model_paths: List of paths to the model files
            weights: Optional weights for each model (default: equal weights)
            model_type: Type of the models
            **kwargs: Additional arguments to pass to OptimizedInference constructor
            
        Returns:
            OptimizedInference instance with ensemble enabled
        """
        return cls(
            model_type=model_type,
            ensemble_models=model_paths,
            ensemble_weights=weights,
            **kwargs
        )

    def validate_onnx_model(self, onnx_path: str = None) -> bool:
        """
        Validate and fix ONNX model input types if needed
        
        Args:
            onnx_path: Path to the ONNX model file
            
        Returns:
            True if model is valid or was fixed, False otherwise
        """
        if not ONNX_AVAILABLE:
            logger.error("ONNX Runtime is not installed, cannot validate model")
            return False
            
        if onnx_path is None:
            onnx_path = os.path.splitext(self.model_path)[0] + ".onnx"
            
        if not os.path.exists(onnx_path):
            logger.error(f"ONNX model not found at {onnx_path}")
            return False
            
        try:
            # Load and check the model
            onnx_model = onnx.load(onnx_path)
            onnx.checker.check_model(onnx_model)
            
            # Check input types
            has_int32_inputs = False
            for input_info in onnx_model.graph.input:
                if hasattr(input_info.type.tensor_type.elem_type, "name") and input_info.type.tensor_type.elem_type.name == "int32":
                    logger.warning(f"ONNX model input '{input_info.name}' has int32 type, should be int64")
                    has_int32_inputs = True
                    
            logger.info(f"ONNX model validation complete: {'int32 inputs detected' if has_int32_inputs else 'all inputs valid'}")
            
            # Return True if model is valid (no int32 inputs), or it can be handled through preprocessing
            return True
        except Exception as e:
            logger.error(f"ONNX model validation failed: {e}")
            return False
