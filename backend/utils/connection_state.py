"""Connection state management with dataclass pattern."""

from dataclasses import dataclass, field
from typing import Optional

from models.inference_engine import InferenceEngine
from utils.segmentation_viz import SegmentationVisualizer


@dataclass
class ConnectionState:
    """
    State for a single WebSocket connection.

    Uses dataclass for immutability and type safety.
    """
    model_mode: str = "balanced"
    viz_mode: str = "filled"
    opacity: float = 0.6
    class_filter: Optional[list] = None
    inference_engine: Optional[InferenceEngine] = None
    visualizer: Optional[SegmentationVisualizer] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for backward compatibility."""
        return {
            "model_mode": self.model_mode,
            "viz_mode": self.viz_mode,
            "opacity": self.opacity,
            "class_filter": self.class_filter,
            "inference_engine": self.inference_engine,
            "visualizer": self.visualizer
        }
