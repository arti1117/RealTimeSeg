"""Configuration management for the segmentation server."""

import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ModelConfig:
    """Configuration for a specific model profile."""
    name: str
    backbone: str
    input_size: tuple
    num_classes: int
    optimization: str  # "onnx", "tensorrt", "pytorch"
    expected_fps: int
    memory_mb: int


# Model profiles configuration
MODEL_PROFILES: Dict[str, ModelConfig] = {
    "fast": ModelConfig(
        name="deeplabv3_mobilenet_v3_large",
        backbone="mobilenet_v3",
        input_size=(512, 512),
        num_classes=21,
        optimization="onnx",
        expected_fps=35,
        memory_mb=1200
    ),
    "balanced": ModelConfig(
        name="deeplabv3_resnet50",
        backbone="resnet50",
        input_size=(640, 640),
        num_classes=21,
        optimization="onnx",
        expected_fps=22,
        memory_mb=2500
    ),
    "accurate": ModelConfig(
        name="segformer-b3-ade20k",
        backbone="segformer",
        input_size=(768, 768),
        num_classes=150,
        optimization="pytorch",
        expected_fps=12,
        memory_mb=4500
    )
}

# COCO Stuff classes (21 classes for Fast/Balanced modes)
COCO_CLASSES: List[str] = [
    "background", "person", "bicycle", "car", "motorcycle",
    "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter",
    "bench", "bird", "cat", "dog", "horse", "sheep", "cow"
]

# ADE20K classes (abbreviated - first 30 most common)
ADE20K_CLASSES: List[str] = [
    "wall", "building", "sky", "floor", "tree", "ceiling", "road",
    "bed", "windowpane", "grass", "cabinet", "sidewalk", "person",
    "earth", "door", "table", "mountain", "plant", "curtain", "chair",
    "car", "water", "painting", "sofa", "shelf", "house", "sea",
    "mirror", "rug", "field"
    # ... (150 total, abbreviated for config)
]

# Server configuration
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "log_level": "info",
    "cors_origins": ["*"],  # Allow all for demo
    "max_queue_size": 3,  # Drop frames if queue exceeds this
    "default_model": "balanced"
}

# Frame processing configuration
FRAME_CONFIG = {
    "jpeg_quality": 80,
    "png_compression": 6,  # 0-9, higher = smaller but slower
    "max_width": 1280,
    "max_height": 720
}

# Visualization configuration
VIZ_CONFIG = {
    "default_opacity": 0.6,
    "default_mode": "filled",
    "available_modes": ["filled", "contour", "side-by-side", "blend"],
    "colormap": "ade20k"
}

# Device configuration
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
USE_FP16 = True if DEVICE == "cuda" else False
