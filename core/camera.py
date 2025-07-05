"""
摄像头管理模块
"""
import cv2
import numpy as np
from typing import Tuple, Optional
from utils.logger import Logger
from config.config import Config

class CameraManager:
    """摄像头管理器类"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.cap = None
        self.frame_width = 0
        self.frame_height = 0
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """初始化摄像头"""
        try:
            self.cap = cv2.VideoCapture(self.config.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                self.logger.error(f"无法打开摄像头索引 {self.config.camera_index}")
                return False
            
            # 设置摄像头参数
            self._configure_camera()
            
            # 获取第一帧以确定尺寸
            success, frame = self.cap.read()
            if not success:
                self.logger.error("无法从摄像头读取第一帧")
                self.cap.release()
                return False
            
            self.frame_height, self.frame_width = frame.shape[:2]
            self.is_initialized = True
            self.logger.info(f"摄像头初始化成功 - 分辨率: {self.frame_width}x{self.frame_height}")
            return True
            
        except Exception as e:
            self.logger.error(f"摄像头初始化异常: {e}")
            return False
    
    def _configure_camera(self):
        """配置摄像头参数"""
        try:
            # 设置缓冲区大小
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            # 设置FPS
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.logger.debug("摄像头参数配置完成")
        except Exception as e:
            self.logger.warning(f"摄像头参数配置失败: {e}")
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """读取一帧"""
        if not self.is_initialized or self.cap is None:
            return False, None
        
        try:
            return self.cap.read()
        except Exception as e:
            self.logger.error(f"读取帧异常: {e}")
            return False, None
    
    def get_frame_size(self) -> Tuple[int, int]:
        """获取帧尺寸"""
        return self.frame_width, self.frame_height
    
    def get_camera_info(self) -> dict:
        """获取摄像头信息"""
        if not self.is_initialized:
            return {}
        
        return {
            'width': self.frame_width,
            'height': self.frame_height,
            'fps': self.cap.get(cv2.CAP_PROP_FPS) if self.cap else 0,
            'backend': self.cap.getBackendName() if self.cap else "Unknown"
        }
    
    def release(self):
        """释放摄像头资源"""
        if self.cap:
            self.cap.release()
            self.is_initialized = False
            self.logger.info("摄像头资源已释放")
