"""Model loading and initialization utilities."""

import os
from typing import Dict, Optional
import torch
import torchvision.models.segmentation as models
from transformers import SegformerForSemanticSegmentation

from utils.config import MODEL_PROFILES, DEVICE, USE_FP16


class ModelLoader:
    """Loads and manages segmentation models."""

    def __init__(self, cache_dir: str = "./models"):
        self.cache_dir = cache_dir
        self.device = DEVICE
        self.use_fp16 = USE_FP16
        self.loaded_models: Dict[str, torch.nn.Module] = {}

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

    def load_model(self, mode: str = "balanced") -> torch.nn.Module:
        """
        Load a model for the specified mode.

        Args:
            mode: Model mode ("fast", "balanced", "accurate")

        Returns:
            Loaded PyTorch model
        """
        if mode in self.loaded_models:
            print(f"Model '{mode}' already loaded, returning cached version")
            return self.loaded_models[mode]

        if mode not in MODEL_PROFILES:
            raise ValueError(f"Unknown model mode: {mode}")

        config = MODEL_PROFILES[mode]
        print(f"Loading model: {config.name} ({mode} mode)")

        # Load model based on configuration
        if mode in ["fast", "balanced"]:
            model = self._load_deeplabv3(config.backbone)
        elif mode == "accurate":
            model = self._load_segformer()
        else:
            raise ValueError(f"Unsupported model mode: {mode}")

        # Move to device
        model = model.to(self.device)

        # Set to evaluation mode
        model.eval()

        # Apply FP16 if available
        if self.use_fp16 and self.device == "cuda":
            model = model.half()
            print(f"Model converted to FP16")

        # Cache the model
        self.loaded_models[mode] = model

        print(f"Model loaded successfully on {self.device}")
        return model

    def _load_deeplabv3(self, backbone: str) -> torch.nn.Module:
        """
        Load DeepLabV3 model with specified backbone.

        Args:
            backbone: Backbone architecture ("mobilenet_v3" or "resnet50")

        Returns:
            DeepLabV3 model
        """
        if backbone == "mobilenet_v3":
            model = models.deeplabv3_mobilenet_v3_large(pretrained=True)
        elif backbone == "resnet50":
            model = models.deeplabv3_resnet50(pretrained=True)
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")

        return model

    def _load_segformer(self) -> torch.nn.Module:
        """
        Load SegFormer model from Hugging Face.

        Returns:
            SegFormer model
        """
        model = SegformerForSemanticSegmentation.from_pretrained(
            "nvidia/segformer-b3-finetuned-ade-512-512",
            cache_dir=self.cache_dir
        )

        return model

    def get_model_info(self, mode: str) -> Dict[str, any]:
        """
        Get information about a model mode.

        Args:
            mode: Model mode

        Returns:
            Dictionary with model information
        """
        if mode not in MODEL_PROFILES:
            raise ValueError(f"Unknown model mode: {mode}")

        config = MODEL_PROFILES[mode]

        return {
            "mode": mode,
            "name": config.name,
            "backbone": config.backbone,
            "input_size": config.input_size,
            "num_classes": config.num_classes,
            "optimization": config.optimization,
            "expected_fps": config.expected_fps,
            "memory_mb": config.memory_mb
        }

    def preload_all_models(self):
        """Preload all model profiles for faster switching."""
        print("Preloading all models...")
        for mode in MODEL_PROFILES.keys():
            try:
                self.load_model(mode)
                print(f"✓ {mode} model loaded")
            except Exception as e:
                print(f"✗ Failed to load {mode} model: {str(e)}")

    def get_available_modes(self) -> list:
        """Get list of available model modes."""
        return list(MODEL_PROFILES.keys())

    def clear_cache(self):
        """Clear loaded models from memory."""
        self.loaded_models.clear()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        print("Model cache cleared")
