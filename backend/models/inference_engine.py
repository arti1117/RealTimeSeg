"""Inference engine for real-time segmentation."""

import time
from typing import Tuple, Dict
import numpy as np
import torch

from models.model_loader import ModelLoader
from utils.frame_processor import FrameProcessor
from utils.config import MODEL_PROFILES, DEVICE, USE_FP16


class InferenceEngine:
    """Handles model inference with performance tracking."""

    def __init__(self, model_loader: ModelLoader, frame_processor: FrameProcessor):
        self.model_loader = model_loader
        self.frame_processor = frame_processor
        self.current_mode = "balanced"
        self.current_model = None
        self.device = DEVICE
        self.use_fp16 = USE_FP16

        # Performance tracking
        self.inference_times = []
        self.max_history = 30  # Track last 30 inferences

    def set_model_mode(self, mode: str):
        """
        Switch to a different model mode.

        Args:
            mode: Model mode ("fast", "balanced", "accurate")
        """
        if mode not in MODEL_PROFILES:
            raise ValueError(f"Unknown model mode: {mode}")

        if mode != self.current_mode:
            print(f"Switching model from {self.current_mode} to {mode}")
            self.current_mode = mode
            self.current_model = self.model_loader.load_model(mode)

    def predict(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Run inference on a frame.

        Args:
            frame: Input frame as numpy array (H, W, 3) in RGB format

        Returns:
            Tuple of (segmentation mask, metadata dict)
        """
        start_time = time.time()

        # Load model if not already loaded
        if self.current_model is None:
            self.current_model = self.model_loader.load_model(self.current_mode)

        # Get model configuration
        config = MODEL_PROFILES[self.current_mode]

        # Preprocess frame
        input_tensor, original_size = self.frame_processor.preprocess_for_model(
            frame,
            target_size=config.input_size,
            normalize=True
        )

        # Move to device and convert to FP16 if needed
        input_tensor = input_tensor.to(self.device)
        if self.use_fp16 and self.device == "cuda":
            input_tensor = input_tensor.half()

        # Run inference
        with torch.no_grad():
            inference_start = time.time()

            if self.current_mode in ["fast", "balanced"]:
                # DeepLabV3 models
                output = self.current_model(input_tensor)['out']
            else:
                # SegFormer model
                output = self.current_model(pixel_values=input_tensor)
                output = output.logits

            inference_time = (time.time() - inference_start) * 1000  # Convert to ms

        # Get segmentation mask
        mask = torch.argmax(output, dim=1).squeeze(0)

        # Postprocess mask to original size
        mask_np = self.frame_processor.postprocess_mask(mask, original_size)

        # Calculate total processing time
        total_time = (time.time() - start_time) * 1000

        # Track performance
        self.inference_times.append(inference_time)
        if len(self.inference_times) > self.max_history:
            self.inference_times.pop(0)

        # Prepare metadata
        metadata = {
            "inference_time_ms": round(inference_time, 2),
            "total_time_ms": round(total_time, 2),
            "model_mode": self.current_mode,
            "fps": round(1000 / total_time, 1) if total_time > 0 else 0,
            "avg_inference_ms": round(np.mean(self.inference_times), 2)
        }

        return mask_np, metadata

    def get_detected_classes(self, mask: np.ndarray) -> list:
        """
        Get list of unique classes detected in the mask.

        Args:
            mask: Segmentation mask (H, W)

        Returns:
            List of class IDs present in the mask
        """
        unique_classes = np.unique(mask).tolist()
        # Remove background (class 0)
        if 0 in unique_classes:
            unique_classes.remove(0)

        return unique_classes

    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get current performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        if not self.inference_times:
            return {
                "avg_inference_ms": 0,
                "min_inference_ms": 0,
                "max_inference_ms": 0,
                "avg_fps": 0
            }

        avg_inference = np.mean(self.inference_times)

        return {
            "avg_inference_ms": round(avg_inference, 2),
            "min_inference_ms": round(np.min(self.inference_times), 2),
            "max_inference_ms": round(np.max(self.inference_times), 2),
            "avg_fps": round(1000 / avg_inference, 1) if avg_inference > 0 else 0
        }

    def warm_up(self, num_iterations: int = 3):
        """
        Warm up the model with dummy inputs to optimize performance.

        Args:
            num_iterations: Number of warm-up iterations
        """
        print(f"Warming up {self.current_mode} model...")

        config = MODEL_PROFILES[self.current_mode]

        # Create dummy input
        dummy_input = torch.randn(1, 3, *config.input_size).to(self.device)
        if self.use_fp16 and self.device == "cuda":
            dummy_input = dummy_input.half()

        # Run warm-up iterations
        with torch.no_grad():
            for i in range(num_iterations):
                if self.current_mode in ["fast", "balanced"]:
                    _ = self.current_model(dummy_input)['out']
                else:
                    _ = self.current_model(pixel_values=dummy_input)

        print(f"Warm-up complete")

    def reset_performance_stats(self):
        """Reset performance tracking."""
        self.inference_times.clear()
