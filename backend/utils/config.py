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
    ),
    "sota": ModelConfig(
        name="mask2former-swin-large-ade20k",
        backbone="swin_large",
        input_size=(1024, 1024),
        num_classes=150,
        optimization="pytorch",
        expected_fps=7,
        memory_mb=6500
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

# WebSocket message types (constants for type safety)
class MessageType:
    """WebSocket message type constants."""
    FRAME = "frame"
    CHANGE_MODE = "change_mode"
    UPDATE_VIZ = "update_viz"
    GET_STATS = "get_stats"
    CONNECTED = "connected"
    SEGMENTATION = "segmentation"
    MODE_CHANGED = "mode_changed"
    VIZ_UPDATED = "viz_updated"
    STATS = "stats"
    ERROR = "error"

# Server configuration
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "log_level": "info",
    "cors_origins": ["*"],  # Allow all for demo
    "max_queue_size": 3,  # Drop frames if queue exceeds this
    "default_model": "sota"
}

# Frame processing configuration
FRAME_CONFIG = {
    "jpeg_quality": 60,  # Reduced from 80 for faster transmission
    "png_compression": 6,  # 0-9, higher = smaller but slower
    "max_width": 960,  # Reduced from 1280 for better performance
    "max_height": 540  # Reduced from 720 for better performance
}

# Visualization mode constants
class VizMode:
    """Visualization mode constants."""
    FILLED = "filled"
    CONTOUR = "contour"
    SIDE_BY_SIDE = "side-by-side"
    BLEND = "blend"

# Visualization configuration
VIZ_CONFIG = {
    "default_opacity": 0.6,
    "default_mode": VizMode.FILLED,
    "available_modes": [VizMode.FILLED, VizMode.CONTOUR, VizMode.SIDE_BY_SIDE, VizMode.BLEND],
    "colormap": "ade20k"
}

# Device configuration - robust CUDA detection
def _detect_device() -> str:
    """Detect best available compute device."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"

DEVICE = _detect_device()
USE_FP16 = DEVICE == "cuda"
