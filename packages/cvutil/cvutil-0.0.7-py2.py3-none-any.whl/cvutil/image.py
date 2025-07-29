"""
    Image auxiliary functions.
"""

__all__ = ['resize_image', 'resize_image_with_min_size', 'crop_image', 'center_crop_image']

import numpy as np
import cv2
from .math import calc_pad_value


def resize_image(image: np.ndarray,
                 image_size: tuple[int, int],
                 interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
    """
    Resize image.

    Parameters
    ----------
    image : np.ndarray
        Original image.
    image_size : tuple(int, int)
        Image size (height x width).
    interpolation : int, default cv2.INTER_LINEAR
        OpenCV interpolation mode.

    Returns
    -------
    np.ndarray
        Resized image.
    """
    image_height, image_width = image.shape[:2]
    height, width = image_size
    if (height == image_height) and (width == image_width):
        return image
    else:
        return cv2.resize(image, dsize=image_size[::-1], interpolation=interpolation)


def resize_image_with_min_size(image: np.ndarray,
                               min_size: int,
                               downscale: bool = False,
                               interpolation: int = cv2.INTER_LINEAR) -> tuple[np.ndarray, tuple[int, int]]:
    """
    Resize image with minimal size.

    Parameters
    ----------
    image : np.ndarray
        Original image.
    min_size : int
        Minimal size value.
    downscale : bool, default False
        Whether to downscale image.
    interpolation : int, default cv2.INTER_LINEAR
        OpenCV interpolation mode.

    Returns
    -------
    np.ndarray
        Resized image.
    tuple(int, int)
        Original image size.
    """
    height, width = image.shape[:2]
    scale = min_size / float(min(width, height))
    if (scale != 1.0) and ((scale > 1.0) or downscale):
        new_height, new_width = tuple(round(dim * scale) for dim in (height, width))
        image = cv2.resize(image, dsize=(new_width, new_height), interpolation=interpolation)
    return image, (height, width)


def crop_image(image: np.ndarray,
               crop_params: tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop image patch.

    Parameters
    ----------
    image : np.ndarray
        Cropping image.
    crop_params : tuple(int, int, int, int)
        Cropping parameters (see code).

    Returns
    -------
    np.ndarray
        Cropped image.
    """
    height, width = image.shape[:2]
    x_left_pad, y_left_pad, x_right_pad, y_right_pad = crop_params
    return image[y_left_pad:(height - y_right_pad), x_left_pad:(width - x_right_pad)]


def center_crop_image(image: np.ndarray,
                      dst_image_size: tuple[int, int]) -> np.ndarray:
    """
    Crop image patch from the center so that sides are equal to pads.

    Parameters
    ----------
    image : np.ndarray
        Cropping image.
    dst_image_size : tuple(int, int)
        Desired image size (height x width).

    Returns
    -------
    np.ndarray
        Cropped image.
    """
    dst_height, dst_width = dst_image_size
    height, width = image.shape[:2]
    if (dst_height > height) or (dst_width > width):
        raise Exception("Image size too small")
    y_left_pad, y_right_pad = calc_pad_value(src_value=dst_height, dst_value=height)
    x_left_pad, x_right_pad = calc_pad_value(src_value=dst_width, dst_value=width)
    return image[y_left_pad:(height - y_right_pad), x_left_pad:(width - x_right_pad)]
