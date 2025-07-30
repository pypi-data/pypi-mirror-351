import cv2
from mmllm_face_refinement.detector import Detector, infer_faces, preprocess_frame

__all__ = ['Detector', 'infer_faces', 'preprocess_frame', 'init']

def init(model_paths=None, config_path=None):
    """
    Initialize the face detector and any models needed.
    Args:
        model_paths: dict of model paths (optional)
        config_path: path to config.yaml (optional)
    Returns:
        Detector instance
    """
    return Detector(model_paths=model_paths, config_path=config_path)

# infer_faces and preprocess_frame will be imported from detector.py and exposed here 