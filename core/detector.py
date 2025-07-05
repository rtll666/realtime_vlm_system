"""
YOLO检测器模块
"""
from ultralytics import YOLO
import numpy as np
from typing import Tuple, Optional
from models.data_models import DetectionInfo, DetectionResult
from utils.logger import Logger
from config.config import Config

class YOLODetector:
    """YOLO检测器类"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.model = self._load_model()
        
    def _load_model(self) -> YOLO:
        """加载YOLO模型"""
        try:
            model = YOLO(self.config.model_path)
            self.logger.info(f"成功加载YOLO模型: {self.config.model_path}")
            return model
        except Exception as e:
            self.logger.error(f"加载YOLO模型失败: {e}")
            raise
            
    def detect(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[DetectionInfo]]:
        """执行检测并返回结果"""
        try:
            results = self.model.predict(
                source=frame, 
                imgsz=self.config.image_size, 
                conf=self.config.conf_threshold, 
                verbose=False
            )
            
            detection_info = self._extract_detection_info(results)
            annotated_frame = results[0].plot()
            
            return annotated_frame, detection_info
            
        except Exception as e:
            self.logger.error(f"YOLO检测过程异常: {e}")
            return frame, None
            
    def _extract_detection_info(self, results) -> Optional[DetectionInfo]:
        """从YOLO结果中提取检测信息"""
        if not results or not results[0].boxes:
            return None
            
        boxes = results[0].boxes
        names = results[0].names
        
        if boxes is None or len(boxes) == 0:
            return None
            
        detection_info = DetectionInfo()
        
        for i, box in enumerate(boxes.xyxy):
            x1, y1, x2, y2 = box.cpu().numpy()
            confidence = float(boxes.conf[i].cpu().numpy())
            class_id = int(boxes.cls[i].cpu().numpy())
            class_name = names[class_id]
            
            detection = DetectionResult(
                class_name=class_name,
                confidence=confidence,
                center_x=float((x1 + x2) / 2),
                center_y=float((y1 + y2) / 2),
                bbox=(float(x1), float(y1), float(x2), float(y2))
            )
            detection_info.add_detection(detection)
            
        return detection_info
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            'model_path': self.config.model_path,
            'image_size': self.config.image_size,
            'conf_threshold': self.config.conf_threshold,
            'model_names': getattr(self.model, 'names', {})
        }
