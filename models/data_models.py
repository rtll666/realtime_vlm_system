"""
数据模型定义
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class DetectionResult:
    """检测结果数据类"""
    class_name: str
    confidence: float
    center_x: float
    center_y: float
    bbox: Tuple[float, float, float, float]

class DetectionInfo:
    """检测信息管理类"""
    def __init__(self):
        self.counts: Dict[str, int] = {}
        self.detections: List[DetectionResult] = []
        self.total_count: int = 0
    
    def add_detection(self, detection: DetectionResult):
        """添加检测结果"""
        self.detections.append(detection)
        self.counts[detection.class_name] = self.counts.get(detection.class_name, 0) + 1
        self.total_count += 1
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return self.total_count == 0
    
    def get_summary_text(self) -> str:
        """获取摘要文本"""
        if self.is_empty():
            return "未检测到铁屑"
        labels_text = "\n".join([f"{k}: {v}个" for k, v in self.counts.items()])
        return f"{labels_text}\n共检测到 {self.total_count} 个铁屑"
    
    def clear(self):
        """清空检测信息"""
        self.counts.clear()
        self.detections.clear()
        self.total_count = 0

@dataclass
class AnalysisResult:
    """分析结果数据类"""
    text: str
    timestamp: float
    success: bool
    error_msg: str = ""
