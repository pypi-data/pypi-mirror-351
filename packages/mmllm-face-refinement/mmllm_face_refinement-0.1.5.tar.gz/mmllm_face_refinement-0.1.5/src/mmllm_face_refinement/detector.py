import cv2
import yaml
from pathlib import Path
from typing import Any, Dict, Union, Tuple
from PIL import Image
import numpy as np
import os
from mmllm_face_refinement.face_detector import YoloFaceDetector

__all__ = ['Detector', 'infer_faces', 'preprocess_frame']

def preprocess_frame(img: Union[np.ndarray, str]) -> np.ndarray:
    """
    Preprocess an image for face detection and return a blob (RGB, float32, normalized 0-1).
    Args:
        img: np.ndarray (BGR or RGB) or image path
    Returns:
        blob: np.ndarray (RGB, float32, normalized 0-1)
    """
    if isinstance(img, str):
        img = cv2.imread(img)
        if img is None:
            raise FileNotFoundError(f"Image file not found or unreadable: {img}")
    if not isinstance(img, np.ndarray):
        raise ValueError("Input must be a numpy array or image path")
    if img.shape[-1] != 3:
        raise ValueError("Input image must have 3 channels (BGR or RGB)")
    # Convert BGR to RGB if needed
    if img.shape[-1] == 3:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = img
    blob = img_rgb.astype(np.float32) / 255.0
    return blob

class Detector:
    def __init__(self, model_paths: dict = None, config_path: str = None):
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / 'config.yaml')
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        # Optionally override model paths
        if model_paths:
            self.config['yolo']['model_path'] = model_paths.get('yolo', self.config['yolo']['model_path'])
        self.detector = YoloFaceDetector(
            model_path=self.config['yolo'].get('model_path'),
            confidence_threshold=self.config['yolo']['confidence_threshold'],
            iou_threshold=self.config['yolo']['iou_threshold'],
            device=self.config['yolo']['device']
        )

    def infer_faces(self, img, model=None, model_config=None, preprocess: bool = False):
        """
        Detect faces in an image using YOLO face detector.
        Args:
            img: np.ndarray (RGB, float32, normalized 0-1) if preprocess=False, else raw image or path
            model: ignored (for API compatibility)
            model_config: must have .name (should start with 'yolo')
            preprocess: whether to preprocess the image (default: False)
        Returns:
            faces: list of [x, y, w, h] (int)
        """
        if preprocess:
            blob = preprocess_frame(img)
        else:
            blob = img
            if not (isinstance(blob, np.ndarray) and blob.dtype == np.float32 and blob.max() <= 1.0 and blob.min() >= 0.0):
                raise ValueError("When preprocess=False, img must be a normalized float32 RGB numpy array (blob)")
        detections = self.detector.detect(blob)
        faces = []
        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])
            w = x2 - x1
            h = y2 - y1
            faces.append([x1, y1, w, h])
        return faces

def infer_faces(img, model, model_config, preprocess: bool = False):
    """
    API-compatible face inference function for external use.
    Args:
        img: np.ndarray (RGB, float32, normalized 0-1) if preprocess=False, else raw image or path
        model: Detector instance
        model_config: must have .name (should start with 'yolo')
        preprocess: whether to preprocess the image (default: False)
    Returns:
        faces: list of [x, y, w, h] (int)
    """
    if hasattr(model, 'infer_faces'):
        return model.infer_faces(img, model, model_config, preprocess)
    raise ValueError("Model must be an instance of Detector from mmllm_face_refinement.init()") 