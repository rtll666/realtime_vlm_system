"""
日志工具模块
"""
import logging
import os
from datetime import datetime

class Logger:
    """日志管理类"""
    
    def __init__(self, log_level: str = "INFO", log_file: str = "detection_log.log"):
        self.log_file = log_file
        self._setup_logger(log_level)
    
    def _setup_logger(self, log_level: str):
        """设置日志器"""
        # 创建日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file_path = os.path.join(log_dir, self.log_file)
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 创建logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 文件handler
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def log_performance(self, fps: float, frame_time: float):
        """记录性能信息"""
        self.info(f"Performance - FPS: {fps:.2f}, Frame Time: {frame_time:.3f}s")
