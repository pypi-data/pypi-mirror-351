#!/usr/bin/env python3
import os
import cv2
import numpy as np
import logging
from PIL import Image, ImageDraw
from typing import List, Dict, Tuple, Any, Optional
from ultralytics import YOLO
import supervision as sv

class YoloFaceDetector:
    """
    Face detector using YOLOv11-Face
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cpu"
    ):
        """
        Initialize YOLOv11-Face detector
        
        Args:
            model_path: Path to the model weights, if None will use local model
            confidence_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.logger = logging.getLogger(__name__)
        
        # Use local YOLOv11-Face model if no model path provided
        if model_path is None:
            local_model_path = os.path.join("models", "yolov11l-face.pt")
            if os.path.exists(local_model_path):
                self.logger.info(f"Using local YOLOv11-Face model: {local_model_path}")
                model_path = local_model_path
            else:
                self.logger.warning("Local YOLOv11-Face model not found, falling back to downloading YOLOv8-Face")
                # This will use ultralytics' built-in functionality to download the model
                try:
                    self.model = YOLO("akanametov/yolov8n-face")
                except Exception as e:
                    self.logger.error(f"Failed to download model: {e}")
                    raise
        
        if model_path is not None:
            try:
                self.model = YOLO(model_path)
                self.logger.info(f"Loaded YOLO model from: {model_path}")
            except Exception as e:
                self.logger.error(f"Failed to load model from {model_path}: {e}")
                raise
        
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        
        # Configure model parameters
        self.model.to(device)
        
        self.logger.info(f"Initialized YOLO Face detector with confidence threshold {confidence_threshold}")
    
    def detect(self, image: Any) -> List[Dict[str, Any]]:
        """
        Detect faces in an image
        Args:
            image: Path to the image, numpy array, or PIL Image
        Returns:
            List of detections, each detection is a dict with keys:
                - bbox: [x1, y1, x2, y2]
                - confidence: float
                - landmarks: facial landmarks if available
        """
        # Accept file path, numpy array, or PIL Image
        if isinstance(image, str):
            if not os.path.exists(image):
                self.logger.error(f"Image not found: {image}")
                return []
            input_data = image
        elif isinstance(image, np.ndarray) or isinstance(image, Image.Image):
            input_data = image
        else:
            self.logger.error(f"Unsupported image type: {type(image)}")
            return []

        # Run inference
        results = self.model(
            input_data,
            conf=self.confidence_threshold,
            iou=self.iou_threshold
        )

        # Extract detections
        detections = []
        for result in results:
            boxes = result.boxes

            for i in range(len(boxes)):
                bbox = boxes.xyxy[i].cpu().numpy().tolist()
                conf = float(boxes.conf[i].cpu().numpy())

                # Extract landmarks if available (depends on YOLO model version)
                landmarks = None
                if hasattr(result, 'keypoints') and result.keypoints is not None:
                    landmarks = result.keypoints[i].xy.cpu().numpy().tolist() if i < len(result.keypoints) else None

                detection = {
                    "bbox": bbox,
                    "confidence": conf,
                    "landmarks": landmarks
                }
                detections.append(detection)

        self.logger.info(f"Detected {len(detections)} faces with confidence >= {self.confidence_threshold}")
        return detections
    
    def crop_face(
        self, 
        image_path: str, 
        detection: Dict[str, Any], 
        padding: float = 0.2,
        min_size: int = 224,
        annotate: bool = True
    ) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Crop a detected face from an image with padding
        
        Args:
            image_path: Path to the image
            detection: Detection from detect()
            padding: Padding percentage (0.2 = 20% padding)
            min_size: Minimum size of the crop
            annotate: Whether to annotate the bounding box on the crop
            
        Returns:
            Tuple of (cropped image, metadata)
        """
        # Load image
        image = Image.open(image_path)
        img_width, img_height = image.size
        
        # Get bounding box
        x1, y1, x2, y2 = detection["bbox"]
        
        # Calculate box dimensions
        box_width = x2 - x1
        box_height = y2 - y1
        
        # Apply padding
        padding_x = box_width * padding
        padding_y = box_height * padding
        
        # Calculate padded bounding box, ensuring it's within image bounds
        x1_padded = max(0, x1 - padding_x)
        y1_padded = max(0, y1 - padding_y)
        x2_padded = min(img_width, x2 + padding_x)
        y2_padded = min(img_height, y2 + padding_y)
        
        # Make sure the crop is at least min_size in each dimension
        width = x2_padded - x1_padded
        height = y2_padded - y1_padded
        
        if width < min_size:
            diff = min_size - width
            x1_padded = max(0, x1_padded - diff/2)
            x2_padded = min(img_width, x2_padded + diff/2)
            
        if height < min_size:
            diff = min_size - height
            y1_padded = max(0, y1_padded - diff/2)
            y2_padded = min(img_height, y2_padded + diff/2)
        
        # Crop image
        crop = image.crop((x1_padded, y1_padded, x2_padded, y2_padded))
        
        # Calculate original box coordinates in the cropped image's coordinate system
        original_bbox_in_crop = [
            x1 - x1_padded,
            y1 - y1_padded,
            x2 - x1_padded,
            y2 - y1_padded
        ]
        
        # Annotate original detection on crop if requested
        if annotate:
            draw = ImageDraw.Draw(crop)
            draw.rectangle(
                original_bbox_in_crop,
                outline="red",
                width=3
            )
        
        # Create metadata
        metadata = {
            "original_image": os.path.basename(image_path),
            "original_image_size": (img_width, img_height),
            "original_bbox": detection["bbox"],
            "padded_bbox": [x1_padded, y1_padded, x2_padded, y2_padded],
            "bbox_in_crop": original_bbox_in_crop,
            "confidence": detection["confidence"],
            "landmarks": detection["landmarks"]
        }
        
        return crop, metadata


# For testing purposes
def test_detector():
    """
    Test the face detector with a sample image
    """
    import matplotlib.pyplot as plt
    
    # Create a detector
    detector = YoloFaceDetector(confidence_threshold=0.3)
    
    # Sample image path
    image_path = "input/sample.jpg"
    
    # Detect faces
    detections = detector.detect(image_path)
    print(f"Detected {len(detections)} faces")
    
    # Display detections
    if len(detections) > 0:
        # Load the image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Draw detections
        for detection in detections:
            bbox = detection["bbox"]
            conf = detection["confidence"]
            
            # Draw bounding box
            cv2.rectangle(
                image,
                (int(bbox[0]), int(bbox[1])),
                (int(bbox[2]), int(bbox[3])),
                (0, 255, 0),
                2
            )
            
            # Draw confidence
            cv2.putText(
                image,
                f"{conf:.2f}",
                (int(bbox[0]), int(bbox[1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        # Display the image
        plt.figure(figsize=(10, 10))
        plt.imshow(image)
        plt.title("Detected Faces")
        plt.axis('off')
        plt.show()
        
        # Test cropping
        for i, detection in enumerate(detections):
            crop, metadata = detector.crop_face(image_path, detection, padding=0.2, annotate=True)
            
            # Display the crop
            plt.figure(figsize=(5, 5))
            plt.imshow(crop)
            plt.title(f"Face {i+1}, Confidence: {detection['confidence']:.2f}")
            plt.axis('off')
            plt.show()
            
            print(f"Metadata for face {i+1}:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Test the detector
    test_detector() 