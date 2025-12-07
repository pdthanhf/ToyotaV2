"""
File inference.py - Xử lý nhận diện xe bằng YOLOv8
"""

from ultralytics import YOLO
from PIL import Image
import numpy as np
from typing import List, Dict, Tuple
import json
from pathlib import Path


class CarDetector:
    """Class xử lý nhận diện xe Toyota"""
    
    def __init__(self, model_path: str = "app/car_classifier/best.pt"):
        """
        Khởi tạo detector
        
        Args:
            model_path: Đường dẫn đến file model weights
        """
        self.model_path = Path(model_path)
        self.model = None
        self.class_names = {}
        
        self._load_model()
        self._load_class_names()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            
            self.model = YOLO(str(self.model_path))
            print(f"✅ Model loaded successfully: {self.model_path}")
        except Exception as e:
            print(f" Error loading model: {e}")
            raise
    
    def _load_class_names(self):
        """Load class names từ class_info.json"""
        try:
            class_info_path = self.model_path.parent / "class_info.json"
            
            if class_info_path.exists():
                with open(class_info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.class_names = data.get("class_names", {})
            else:
                # Fallback: dùng class names từ model
                self.class_names = self.model.names
            
            print(f" Loaded {len(self.class_names)} classes")
        except Exception as e:
            print(f" Error loading class names: {e}")
            self.class_names = {}
    
    def predict(
        self, 
        image: Image.Image,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45
    ) -> List[Dict]:
        """
        Nhận diện xe trong ảnh
        
        Args:
            image: PIL Image
            conf_threshold: Ngưỡng confidence (0-1)
            iou_threshold: Ngưỡng IoU cho NMS
            
        Returns:
            List of detections: [
                {
                    "class_id": int,
                    "class_name": str,
                    "confidence": float,
                    "bbox": {"x1": float, "y1": float, "x2": float, "y2": float}
                }
            ]
        """
        try:
            # Chạy prediction
            results = self.model.predict(
                source=image,
                conf=conf_threshold,
                iou=iou_threshold,
                verbose=False
            )
            
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                # Parse boxes
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Lấy tên class
                    class_name = self.class_names.get(
                        str(class_id),
                        result.names.get(class_id, f"Unknown_{class_id}")
                    )
                    
                    detections.append({
                        "class_id": class_id,
                        "class_name": class_name,
                        "confidence": confidence,
                        "bbox": {
                            "x1": bbox[0],
                            "y1": bbox[1],
                            "x2": bbox[2],
                            "y2": bbox[3]
                        }
                    })
            
            return detections
            
        except Exception as e:
            print(f" Prediction error: {e}")
            return []
    
    def predict_batch(
        self, 
        images: List[Image.Image],
        conf_threshold: float = 0.5
    ) -> List[List[Dict]]:
        """
        Nhận diện nhiều ảnh cùng lúc
        
        Args:
            images: List of PIL Images
            conf_threshold: Ngưỡng confidence
            
        Returns:
            List of detections cho mỗi ảnh
        """
        all_detections = []
        
        for image in images:
            detections = self.predict(image, conf_threshold)
            all_detections.append(detections)
        
        return all_detections
    
    def get_annotated_image(
        self, 
        image: Image.Image,
        conf_threshold: float = 0.5
    ) -> Image.Image:
        """
        Trả về ảnh đã vẽ bounding boxes
        
        Args:
            image: PIL Image
            conf_threshold: Ngưỡng confidence
            
        Returns:
            PIL Image với bounding boxes
        """
        try:
            results = self.model.predict(
                source=image,
                conf=conf_threshold,
                verbose=False
            )
            
            if results and len(results) > 0:
                # YOLOv8 tự động vẽ boxes
                annotated_array = results[0].plot()
                
                # Convert numpy array to PIL Image
                from PIL import Image
                annotated_image = Image.fromarray(annotated_array)
                return annotated_image
            
            return image
            
        except Exception as e:
            print(f" Annotation error: {e}")
            return image
    
    def get_class_distribution(self, detections: List[Dict]) -> Dict[str, int]:
        """
        Thống kê số lượng xe theo class
        
        Args:
            detections: List of detections
            
        Returns:
            Dict: {"class_name": count}
        """
        distribution = {}
        
        for det in detections:
            class_name = det["class_name"]
            distribution[class_name] = distribution.get(class_name, 0) + 1
        
        return distribution


# ==================== HELPER FUNCTIONS ====================

def load_detector(model_path: str = "app/car_classifier/best.pt") -> CarDetector:
    """
    Factory function để tạo detector
    
    Args:
        model_path: Đường dẫn model
        
    Returns:
        CarDetector instance
    """
    return CarDetector(model_path)


def detect_from_file(
    image_path: str,
    model_path: str = "app/car_classifier/best.pt",
    conf_threshold: float = 0.5
) -> List[Dict]:
    """
    Nhận diện từ file ảnh
    
    Args:
        image_path: Đường dẫn ảnh
        model_path: Đường dẫn model
        conf_threshold: Ngưỡng confidence
        
    Returns:
        List of detections
    """
    detector = load_detector(model_path)
    image = Image.open(image_path)
    return detector.predict(image, conf_threshold)


# ==================== TESTING ====================

if __name__ == "__main__":
    # Test detector
    print("Testing CarDetector...")
    
    try:
        detector = CarDetector()
        print(" Detector initialized successfully")
        
        # Test với ảnh mẫu
        test_image = Image.new('RGB', (640, 640), color='white')
        detections = detector.predict(test_image)
        
        print(f"Detections: {len(detections)}")
        
    except Exception as e:
        print(f" Test failed: {e}")