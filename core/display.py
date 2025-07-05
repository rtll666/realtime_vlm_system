"""
显示管理模块
"""
import cv2
import numpy as np
from typing import Optional
from models.data_models import DetectionInfo
from config.config import Config

class DisplayManager:
    """显示管理器类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.window_name = "YOLOv8 - local camera recognition (press 'q' to exit)"
        # 预定义所有可能的类别名称
        self.all_classes = ["good", "medium", "bad"]
        
    def draw_info_overlay(self, frame: np.ndarray, fps: float, 
                         detection_info: Optional[DetectionInfo], 
                         analysis_status: str, current_analysis: str, 
                         is_analyzing: bool) -> np.ndarray:
        """在帧上绘制信息覆盖层 - FPS和类别统计"""
        # 绘制FPS信息
        self._draw_fps(frame, fps)
        
        # 始终显示各类别数量统计（无目标时显示为0）
        self._draw_detection_counts(frame, detection_info)
        
        return frame
    
    def _draw_fps(self, frame: np.ndarray, fps: float):
        """绘制FPS信息 - 与Yolov8Detector.py完全一致"""
        framefps_text = f"FPS: {fps:.2f}"
        # 在左上角绘制黑色背景矩形
        cv2.rectangle(frame, (10, 5), (130, 25), (0, 0, 0), -1)
        # 在矩形上绘制FPS文本
        cv2.putText(frame, framefps_text, (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    def _draw_detection_counts(self, frame: np.ndarray, detection_info: Optional[DetectionInfo]):
        """绘制各类别数量统计 - 无目标时显示0"""
        y_offset = 30
        
        for class_name in self.all_classes:
            # 获取当前类别的数量，如果没有检测到则为0
            if detection_info and not detection_info.is_empty():
                count = detection_info.counts.get(class_name, 0)
            else:
                count = 0
            
            class_text = f"{class_name}: {count}"
            # 绘制黑色背景矩形
            cv2.rectangle(frame, (10, y_offset), (150, y_offset + 20), (0, 0, 0), -1)
            # 绘制类别统计文本
            cv2.putText(frame, class_text, (15, y_offset + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
    
    def resize_for_display(self, frame: np.ndarray) -> np.ndarray:
        """调整帧大小用于显示"""
        if self.config.display_scale != 1.0:
            height, width = frame.shape[:2]
            new_height = int(height * self.config.display_scale)
            new_width = int(width * self.config.display_scale)
            return cv2.resize(frame, (new_width, new_height))
        return frame
    
    def show_frame(self, frame: np.ndarray):
        """显示帧"""
        cv2.imshow(self.window_name, frame)
    
    def cleanup(self):
        """清理显示资源"""
        cv2.destroyAllWindows()
