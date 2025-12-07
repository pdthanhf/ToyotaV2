from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

from app.core.config import settings

class DetectionService:
    """Service xử lý nhận diện xe bằng YOLOv8"""
    
    def __init__(self):
        self.model = None
        self.class_names = {}
        self.load_model()
        self.load_class_info()
    
    def load_model(self):
        """Load YOLOv8 model"""
        try:
            model_path = Path(settings.MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {settings.MODEL_PATH}")
            
            self.model = YOLO(str(model_path))
            print(f" YOLOv8 model loaded: {settings.MODEL_PATH}")
        except Exception as e:
            print(f" Error loading model: {e}")
            raise
    
    def load_class_info(self):
        """Load class names từ class_info.json"""
        try:
            class_info_path = Path("app/car_classifier/class_info.json")
            if class_info_path.exists():
                with open(class_info_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.class_names = data.get("class_names", {})
                print(f" Loaded {len(self.class_names)} class names")
            else:
                # Fallback: Dùng class names từ model
                if self.model:
                    self.class_names = self.model.names
                print(" class_info.json not found, using model names")
        except Exception as e:
            print(f" Error loading class info: {e}")
            self.class_names = {}
    
    def detect(
        self, 
        image: Image.Image,
        confidence_threshold: float = None,
        draw_boxes: bool = True
    ) -> Dict:
        """
        Nhận diện xe trong ảnh
        
        Args:
            image: PIL Image
            confidence_threshold: Ngưỡng confidence (mặc định từ config)
            draw_boxes: Có vẽ bounding box lên ảnh không
            
        Returns:
            Dict chứa detections và annotated image
        """
        if confidence_threshold is None:
            confidence_threshold = settings.CONFIDENCE_THRESHOLD
        
        try:
            # Chạy inference
            results = self.model.predict(
                source=image,
                conf=confidence_threshold,
                verbose=False
            )
            
            detections = []
            annotated_image = None
            
            if results and len(results) > 0:
                result = results[0]
                
                # Parse detections
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Lấy tên class
                    class_name = self.class_names.get(
                        str(class_id), 
                        result.names.get(class_id, f"Class_{class_id}")
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
                
                # Vẽ bounding boxes
                if draw_boxes and len(detections) > 0:
                    annotated_image = self._draw_boxes(image.copy(), detections)
            
            return {
                "success": True,
                "detections": detections,
                "annotated_image": annotated_image,
                "total_detections": len(detections)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "detections": [],
                "annotated_image": None
            }
    
    def _draw_boxes(self, image: Image.Image, detections: List[Dict]) -> Image.Image:
        """Vẽ bounding boxes lên ảnh"""
        draw = ImageDraw.Draw(image)
        
        # Màu sắc cho các boxes
        colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", 
            "#FF00FF", "#00FFFF", "#FFA500", "#800080"
        ]
        
        try:
            # Load font (nếu có)
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        for idx, det in enumerate(detections):
            bbox = det["bbox"]
            x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
            
            # Chọn màu
            color = colors[idx % len(colors)]
            
            # Vẽ rectangle
            draw.rectangle(
                [(x1, y1), (x2, y2)],
                outline=color,
                width=3
            )
            
            # Vẽ label
            label = f"{det['class_name']} {det['confidence']:.2f}"
            
            # Background cho text
            text_bbox = draw.textbbox((x1, y1 - 25), label, font=font)
            draw.rectangle(
                [text_bbox[0] - 2, text_bbox[1] - 2, text_bbox[2] + 2, text_bbox[3] + 2],
                fill=color
            )
            
            # Text
            draw.text((x1, y1 - 25), label, fill="white", font=font)
        
        return image
    
    def get_classes(self) -> Dict:
        """Lấy danh sách tất cả classes"""
        return {
            "total": len(self.class_names),
            "classes": [
                {"id": k, "name": v} 
                for k, v in self.class_names.items()
            ]
        }
    
    def get_model_info(self) -> Dict:
        """Lấy thông tin model"""
        if not self.model:
            return {"error": "Model not loaded"}
        
        return {
            "model_path": settings.MODEL_PATH,
            "num_classes": len(self.class_names),
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "model_type": "YOLOv8"
        }