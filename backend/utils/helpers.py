"""Helper utilities for common operations."""

from typing import List
from utils.config import MODEL_PROFILES, COCO_CLASSES, ADE20K_CLASSES


def get_class_labels_for_model(model_mode: str, max_classes: int = 30) -> List[str]:
    """
    Get appropriate class labels for a given model mode.

    Args:
        model_mode: Model mode identifier (fast, balanced, accurate, sota)
        max_classes: Maximum number of classes to return for large class sets

    Returns:
        List of class label strings appropriate for the model

    Raises:
        ValueError: If model_mode is not found in MODEL_PROFILES
    """
    if model_mode not in MODEL_PROFILES:
        raise ValueError(f"Unknown model mode: {model_mode}")

    config = MODEL_PROFILES[model_mode]

    if config.num_classes == 21:
        return COCO_CLASSES
    else:
        # For models with 150 classes (ADE20K), return truncated list
        return ADE20K_CLASSES[:max_classes]


def create_error_response(
    error_code: str,
    message: str,
    recoverable: bool = True
) -> dict:
    """
    Create a standardized error response.

    Args:
        error_code: Error code identifier
        message: Human-readable error message
        recoverable: Whether the error can be recovered from

    Returns:
        Dictionary with error response structure
    """
    return {
        "type": "error",
        "code": error_code,
        "message": message,
        "recoverable": recoverable
    }
