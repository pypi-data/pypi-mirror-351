import cv2
import yaml
from pathlib import Path
from typing import Any, Dict, Union, Tuple
from PIL import Image
import numpy as np
import os
import tempfile
from mmllm_face_refinement.face_detector import YoloFaceDetector

__all__ = ['Detector', 'infer_faces', 'preprocess_frame']

def preprocess_frame(img: Union[np.ndarray, str]) -> Tuple[str, bool]:
    """
    Preprocess an image for face detection.
    Args:
        img: np.ndarray (BGR or RGB) or image path
    Returns:
        Tuple of (image_path, is_temp_file) where is_temp_file indicates if a temporary file was created
    """
    if isinstance(img, np.ndarray):
        if img.shape[-1] == 3:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("Input image must have 3 channels (BGR or RGB)")
        pil_img = Image.fromarray(img_rgb)
        # Use system temp directory instead of local temp directory
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'mmllm_face_infer_temp.jpg')
        pil_img.save(temp_path)
        return temp_path, True
    elif isinstance(img, str):
        # Convert to absolute path and verify file exists
        abs_path = os.path.abspath(img)
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"Image file not found: {abs_path}")
        return abs_path, False
    else:
        raise ValueError("img must be a numpy array or image path")

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
            img: np.ndarray (BGR or RGB) or image path
            model: ignored (for API compatibility)
            model_config: must have .name (should start with 'yolo')
            preprocess: whether to preprocess the image (default: False)
        Returns:
            faces: list of [x, y, w, h] (int)
        """
        temp_path = None
        try:
            if preprocess:
                image_path, is_temp = preprocess_frame(img)
                detections = self.detector.detect(image_path)
            else:
                # When preprocess is False, img should be a numpy array
                if not isinstance(img, np.ndarray):
                    raise ValueError("When preprocess=False, img must be a numpy array")
                if img.shape[-1] != 3:
                    raise ValueError("Input image must have 3 channels (BGR or RGB)")
                # Convert BGR to RGB if needed
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, 'mmllm_face_infer_temp.jpg')
                pil_img.save(temp_path)
                detections = self.detector.detect(temp_path)

            faces = []
            for det in detections:
                x1, y1, x2, y2 = map(int, det['bbox'])
                w = x2 - x1
                h = y2 - y1
                faces.append([x1, y1, w, h])
            return faces
        finally:
            # Clean up temporary file if we created one
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass  # Ignore cleanup errors

def infer_faces(img, model, model_config, preprocess: bool = False):
    """
    API-compatible face inference function for external use.
    Args:
        img: np.ndarray (BGR or RGB)
        model: Detector instance
        model_config: must have .name (should start with 'yolo')
        preprocess: whether to preprocess the image (default: False)
    Returns:
        faces: list of [x, y, w, h] (int)
    """
    if hasattr(model, 'infer_faces'):
        return model.infer_faces(img, model, model_config, preprocess)
    raise ValueError("Model must be an instance of Detector from mmllm_face_refinement.init()") 