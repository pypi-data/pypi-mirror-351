"""
M3da - ONNX model inference for image classification

This package provides a simple interface for image classification using ONNX models.
"""

from .tools import classify_image as execute

__all__ = ["execute"]


__version__ = "0.1.0"
