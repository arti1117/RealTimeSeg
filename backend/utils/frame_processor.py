"""Frame encoding, decoding, and preprocessing utilities."""

import base64
import io
from typing import Tuple, Optional

import cv2
import numpy as np
from PIL import Image
import torch

from utils.config import FRAME_CONFIG


class FrameProcessor:
    """Handles frame encoding, decoding, and preprocessing."""

    def __init__(self, jpeg_quality: int = FRAME_CONFIG["jpeg_quality"]):
        self.jpeg_quality = jpeg_quality
        self.max_width = FRAME_CONFIG["max_width"]
        self.max_height = FRAME_CONFIG["max_height"]

        # Performance: Pre-allocate reusable buffers
        self._decode_cache = {}
        self._last_frame_size = None

    def decode_frame(self, base64_data: str) -> np.ndarray:
        """
        Decode base64 JPEG frame to numpy array.

        Args:
            base64_data: Base64-encoded JPEG image

        Returns:
            Decoded image as numpy array (H, W, C) in RGB format

        Raises:
            ValueError: If frame is empty, invalid format, or decoding fails
        """
        if not base64_data:
            raise ValueError("Empty frame data received")

        try:
            # Remove data URL prefix if present
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]

            # Decode base64 to bytes
            img_bytes = base64.b64decode(base64_data)

            if len(img_bytes) == 0:
                raise ValueError("Decoded frame has zero bytes")

            # Convert to numpy array
            nparr = np.frombuffer(img_bytes, np.uint8)

            # Decode JPEG
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("cv2.imdecode returned None - invalid image format")

            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            return img
        except base64.binascii.Error as e:
            raise ValueError(f"Invalid base64 encoding: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to decode frame: {type(e).__name__}: {str(e)}")

    def encode_frame(self, frame: np.ndarray, format: str = "jpeg") -> str:
        """
        Encode numpy array to base64 string.

        Args:
            frame: Image as numpy array (H, W, C)
            format: Output format ("jpeg" or "png")

        Returns:
            Base64-encoded image string

        Raises:
            ValueError: If frame is invalid, unsupported format, or encoding fails
        """
        if frame is None or frame.size == 0:
            raise ValueError("Empty or None frame provided for encoding")

        if len(frame.shape) != 3 or frame.shape[2] != 3:
            raise ValueError(f"Invalid frame shape: {frame.shape}. Expected (H, W, 3)")

        try:
            if format == "jpeg":
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Encode as JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
                success, buffer = cv2.imencode('.jpg', frame_bgr, encode_param)

                if not success:
                    raise ValueError("JPEG encoding failed")

            elif format == "png":
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # Encode as PNG
                encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), FRAME_CONFIG["png_compression"]]
                success, buffer = cv2.imencode('.png', frame_bgr, encode_param)

                if not success:
                    raise ValueError("PNG encoding failed")
            else:
                raise ValueError(f"Unsupported format: {format}. Use 'jpeg' or 'png'")

            # Convert to base64
            base64_data = base64.b64encode(buffer).decode('utf-8')

            return base64_data

        except cv2.error as e:
            raise ValueError(f"OpenCV encoding error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to encode frame: {type(e).__name__}: {str(e)}")

    def preprocess_for_model(
        self,
        frame: np.ndarray,
        target_size: Tuple[int, int],
        normalize: bool = True
    ) -> Tuple[torch.Tensor, Tuple[int, int]]:
        """
        Preprocess frame for model inference (optimized).

        Args:
            frame: Input frame as numpy array (H, W, C)
            target_size: Target size (width, height)
            normalize: Whether to normalize to [0, 1]

        Returns:
            Tuple of (preprocessed tensor, original size)
        """
        original_size = (frame.shape[1], frame.shape[0])  # (W, H)

        # Performance: Use INTER_AREA for downscaling (faster than INTER_LINEAR)
        interpolation = cv2.INTER_AREA if (target_size[0] < frame.shape[1]) else cv2.INTER_LINEAR
        resized = cv2.resize(frame, target_size, interpolation=interpolation)

        # Performance: Direct tensor creation from numpy (faster than from_numpy + permute)
        # Convert to contiguous array first for faster processing
        resized = np.ascontiguousarray(resized)

        # Create tensor directly in correct format (C, H, W)
        tensor = torch.from_numpy(resized.transpose(2, 0, 1)).float()

        # Normalize to [0, 1] if requested (in-place for speed)
        if normalize:
            tensor.div_(255.0)  # In-place division

        # Add batch dimension (1, C, H, W)
        tensor = tensor.unsqueeze(0)

        return tensor, original_size

    def postprocess_mask(
        self,
        mask: torch.Tensor,
        original_size: Tuple[int, int]
    ) -> np.ndarray:
        """
        Postprocess segmentation mask to original size.

        Args:
            mask: Segmentation mask tensor (1, H, W) or (H, W)
            original_size: Original frame size (width, height)

        Returns:
            Resized mask as numpy array (H, W)
        """
        # Remove batch dimension if present
        if mask.dim() == 3:
            mask = mask.squeeze(0)

        # Convert to numpy
        mask_np = mask.cpu().numpy().astype(np.uint8)

        # Resize to original size
        mask_resized = cv2.resize(
            mask_np,
            original_size,
            interpolation=cv2.INTER_NEAREST
        )

        return mask_resized

    def resize_if_needed(self, frame: np.ndarray) -> np.ndarray:
        """Resize frame if it exceeds maximum dimensions."""
        h, w = frame.shape[:2]

        if w <= self.max_width and h <= self.max_height:
            return frame

        # Calculate scaling factor
        scale = min(self.max_width / w, self.max_height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        return resized
