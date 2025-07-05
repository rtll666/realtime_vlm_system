"""
配置管理模块
"""
from dataclasses import dataclass
import os

@dataclass
class Config:
    """配置参数类"""
    # 模型配置
    model_path: str = "your_model_path/yolo_model.pt"
    image_size: int = 640
    conf_threshold: float = 0.3
    
    # 摄像头配置
    camera_index: int = 0
    display_scale: float = 0.8
    
    # 分析配置
    analysis_interval: int = 10
    jpeg_quality: int = 80
    max_tokens: int = 100
    temperature: float = 0.5
    
    # API配置
    api_key: str = os.getenv("QWEN_API_KEY")
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model_name: str = "qwen-vl-max"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "detection_log.log"
    
    # 性能监控配置
    performance_window_size: int = 30
    fps_warning_threshold: float = 10.0
    
    def validate(self) -> bool:
        """验证配置参数的有效性"""
        if not os.path.exists(self.model_path):
            raise ValueError(f"模型文件不存在: {self.model_path}")
        
        if self.analysis_interval <= 0:
            raise ValueError("分析间隔必须大于0")
        
        if not self.api_key:
            raise ValueError("API密钥不能为空")
        
        return True
