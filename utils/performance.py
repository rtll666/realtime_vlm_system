"""
性能监控模块
"""
from typing import Dict, List
import time
from utils.logger import Logger

class PerformanceMonitor:
    """性能监控器类"""
    
    def __init__(self, logger: Logger, window_size: int = 30, fps_threshold: float = 10.0):
        self.logger = logger
        self.window_size = window_size
        self.fps_threshold = fps_threshold
        self.frame_times: List[float] = []
        self.frame_count = 0
        self.start_time = time.time()
        
    def record_frame_time(self, frame_time: float):
        """记录帧处理时间"""
        self.frame_times.append(frame_time)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        self.frame_count += 1
        
    def get_current_fps(self, frame_time: float) -> float:
        """获取当前FPS"""
        return 1.0 / frame_time if frame_time > 0 else 0.0
    
    def get_average_fps(self) -> float:
        """获取平均FPS"""
        if not self.frame_times:
            return 0.0
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0.0
    
    def check_performance(self):
        """检查性能并记录警告"""
        if self.frame_count % self.window_size == 0 and self.frame_times:
            avg_fps = self.get_average_fps()
            if avg_fps < self.fps_threshold:
                self.logger.warning(f"性能警告: 平均FPS仅为 {avg_fps:.1f}")
            else:
                self.logger.debug(f"性能正常: 平均FPS为 {avg_fps:.1f}")
    
    def get_summary(self) -> Dict[str, float]:
        """获取性能摘要"""
        total_time = time.time() - self.start_time
        return {
            'total_frames': self.frame_count,
            'total_time': total_time,
            'average_fps': self.get_average_fps(),
            'average_frame_time': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0,
            'overall_fps': self.frame_count / total_time if total_time > 0 else 0
        }
    
    def reset(self):
        """重置监控器"""
        self.frame_times.clear()
        self.frame_count = 0
        self.start_time = time.time()
