"""Segmentation visualization utilities with multiple rendering modes."""

import numpy as np
import cv2
from typing import List, Optional, Tuple


class SegmentationVisualizer:
    """Creates visualizations of segmentation masks."""

    def __init__(self, num_classes: int = 21):
        self.num_classes = num_classes
        self.colormap = self._generate_colormap(num_classes)

    def _generate_colormap(self, num_classes: int) -> np.ndarray:
        """
        Generate a colormap for segmentation classes.

        Args:
            num_classes: Number of classes

        Returns:
            Colormap array of shape (num_classes, 3) in RGB format
        """
        # Use a variation of the PASCAL VOC colormap
        colormap = np.zeros((num_classes, 3), dtype=np.uint8)

        for i in range(num_classes):
            r = 0
            g = 0
            b = 0
            c = i
            for j in range(8):
                r |= ((c >> 0) & 1) << (7 - j)
                g |= ((c >> 1) & 1) << (7 - j)
                b |= ((c >> 2) & 1) << (7 - j)
                c >>= 3

            colormap[i] = [r, g, b]

        # Set background to black
        colormap[0] = [0, 0, 0]

        return colormap

    def apply_colormap(self, mask: np.ndarray) -> np.ndarray:
        """
        Apply colormap to segmentation mask.

        Args:
            mask: Segmentation mask (H, W) with class indices

        Returns:
            Colorized mask (H, W, 3) in RGB format
        """
        h, w = mask.shape
        colored_mask = np.zeros((h, w, 3), dtype=np.uint8)

        for class_id in range(self.num_classes):
            colored_mask[mask == class_id] = self.colormap[class_id]

        return colored_mask

    def create_filled_overlay(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        opacity: float = 0.6,
        class_filter: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Create filled overlay visualization.

        Args:
            image: Original image (H, W, 3)
            mask: Segmentation mask (H, W)
            opacity: Overlay opacity (0-1)
            class_filter: List of class IDs to show (None = show all)

        Returns:
            Image with overlay (H, W, 3)
        """
        # Apply colormap
        colored_mask = self.apply_colormap(mask)

        # Apply class filter if specified
        if class_filter is not None:
            filter_mask = np.zeros_like(mask, dtype=bool)
            for class_id in class_filter:
                filter_mask |= (mask == class_id)
            colored_mask[~filter_mask] = 0

        # Blend with original image
        overlay = cv2.addWeighted(
            image,
            1 - opacity,
            colored_mask,
            opacity,
            0
        )

        return overlay

    def create_contour_overlay(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        thickness: int = 2,
        class_filter: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Create contour-only overlay visualization.

        Args:
            image: Original image (H, W, 3)
            mask: Segmentation mask (H, W)
            thickness: Contour line thickness
            class_filter: List of class IDs to show (None = show all)

        Returns:
            Image with contours (H, W, 3)
        """
        result = image.copy()

        # Process each class separately
        classes_to_show = class_filter if class_filter else range(1, self.num_classes)

        for class_id in classes_to_show:
            # Create binary mask for this class
            class_mask = (mask == class_id).astype(np.uint8) * 255

            # Find contours
            contours, _ = cv2.findContours(
                class_mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            # Draw contours with class color
            color = tuple(int(c) for c in self.colormap[class_id])
            cv2.drawContours(result, contours, -1, color, thickness)

        return result

    def create_side_by_side(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        class_filter: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Create side-by-side visualization.

        Args:
            image: Original image (H, W, 3)
            mask: Segmentation mask (H, W)
            class_filter: List of class IDs to show (None = show all)

        Returns:
            Side-by-side image (H, W*2, 3)
        """
        # Apply colormap
        colored_mask = self.apply_colormap(mask)

        # Apply class filter if specified
        if class_filter is not None:
            filter_mask = np.zeros_like(mask, dtype=bool)
            for class_id in class_filter:
                filter_mask |= (mask == class_id)
            colored_mask[~filter_mask] = 0

        # Concatenate horizontally
        result = np.hstack([image, colored_mask])

        return result

    def create_blend_mode(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        class_filter: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Create artistic blend visualization using HSV color space.

        Args:
            image: Original image (H, W, 3)
            mask: Segmentation mask (H, W)
            class_filter: List of class IDs to show (None = show all)

        Returns:
            Blended image (H, W, 3)
        """
        # Apply colormap
        colored_mask = self.apply_colormap(mask)

        # Apply class filter if specified
        if class_filter is not None:
            filter_mask = np.zeros_like(mask, dtype=bool)
            for class_id in class_filter:
                filter_mask |= (mask == class_id)
            colored_mask[~filter_mask] = 0

        # Convert to HSV
        image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        mask_hsv = cv2.cvtColor(colored_mask, cv2.COLOR_RGB2HSV)

        # Blend: Use hue from mask, saturation/value from image
        result_hsv = image_hsv.copy()
        non_black = np.any(colored_mask > 0, axis=2)
        result_hsv[non_black, 0] = mask_hsv[non_black, 0]  # Hue from mask

        # Convert back to RGB
        result = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)

        return result

    def render(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        mode: str = "filled",
        opacity: float = 0.6,
        class_filter: Optional[List[int]] = None
    ) -> np.ndarray:
        """
        Render segmentation with specified visualization mode.

        Args:
            image: Original image (H, W, 3)
            mask: Segmentation mask (H, W)
            mode: Visualization mode ("filled", "contour", "side-by-side", "blend")
            opacity: Overlay opacity for filled mode
            class_filter: List of class IDs to show (None = show all)

        Returns:
            Rendered visualization (H, W, 3) or (H, W*2, 3) for side-by-side
        """
        if mode == "filled":
            return self.create_filled_overlay(image, mask, opacity, class_filter)
        elif mode == "contour":
            return self.create_contour_overlay(image, mask, class_filter=class_filter)
        elif mode == "side-by-side":
            return self.create_side_by_side(image, mask, class_filter)
        elif mode == "blend":
            return self.create_blend_mode(image, mask, class_filter)
        else:
            raise ValueError(f"Unknown visualization mode: {mode}")
