"""
主应用程序类
"""
import time
import cv2
from typing import Optional
from config.config import Config
from utils.logger import Logger
from utils.performance import PerformanceMonitor
from core.camera import CameraManager
from core.detector import YOLODetector
from core.analyzer import QwenAnalyzer
from core.display import DisplayManager
from models.data_models import DetectionInfo

class RealtimeVLMApp:
    """实时视觉语言模型应用程序主类"""
    
    def __init__(self, config: Config):
        # 验证配置
        config.validate()
        
        self.config = config
        self.logger = Logger(config.log_level, config.log_file)
        
        # 初始化各个组件
        self.camera_manager = CameraManager(config, self.logger)
        self.detector = YOLODetector(config, self.logger)
        self.analyzer = QwenAnalyzer(config, self.logger)
        self.display_manager = DisplayManager(config)
        self.performance_monitor = PerformanceMonitor(
            self.logger, 
            config.performance_window_size, 
            config.fps_warning_threshold
        )
        
        # 状态变量
        self.last_analysis_time = 0
        self.running = False
        
    def initialize(self) -> bool:
        """初始化应用程序"""
        self.logger.info("正在初始化应用程序...")
        
        try:
            # 初始化摄像头
            if not self.camera_manager.initialize():
                return False
            
            # 启动分析器
            self.analyzer.start_worker()
            
            # 记录系统信息
            self._log_system_info()
            
            self.logger.info("应用程序初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"应用程序初始化失败: {e}")
            return False
    
    def _log_system_info(self):
        """记录系统信息"""
        camera_info = self.camera_manager.get_camera_info()
        model_info = self.detector.get_model_info()
        
        self.logger.info(f"摄像头信息: {camera_info}")
        self.logger.info(f"模型信息: {model_info}")
        self.logger.info(f"配置参数: 分析间隔={self.config.analysis_interval}s")
    
    def run(self):
        """运行主循环"""
        if not self.initialize():
            self.logger.error("应用程序初始化失败")
            return
        
        self.running = True
        self.logger.info("开始实时检测，按 'q' 退出...")
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.logger.info("收到键盘中断信号")
        except Exception as e:
            self.logger.error(f"主循环异常: {e}")
        finally:
            self._cleanup()
    
    def _main_loop(self):
        """主处理循环"""
        frame_count = 0
        
        while self.running:
            loop_start_time = time.time()
            
            # 读取帧
            success, frame = self.camera_manager.read_frame()
            if not success:
                self.logger.error("读取帧失败")
                break
            
            # YOLO检测
            processed_frame, detection_info = self.detector.detect(frame)
            
            # 定时分析
            self._handle_analysis(processed_frame, detection_info, frame_count)
            
            # 性能监控
            frame_time = time.time() - loop_start_time
            self.performance_monitor.record_frame_time(frame_time)
            self.performance_monitor.check_performance()
            
            # 显示处理
            self._handle_display(processed_frame, detection_info, frame_time)
            
            frame_count += 1
            
            # 检查退出条件
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.logger.info("检测到 'q' 键按下，正在退出...")
                break
    
    def _handle_analysis(self, frame, detection_info: Optional[DetectionInfo], frame_count: int):
        """处理分析逻辑"""
        current_time = time.time()
        should_analyze = (
            current_time - self.last_analysis_time >= self.config.analysis_interval
            and detection_info is not None
            and not detection_info.is_empty()
            and not self.analyzer.is_busy()
        )
        
        if should_analyze:
            if self.analyzer.add_analysis_task(frame, detection_info):
                self.logger.info(f"已提交第{frame_count}帧进行后台分析")
                self.last_analysis_time = current_time
            else:
                self.logger.warning("提交分析任务失败")
    
    def _handle_display(self, frame, detection_info: Optional[DetectionInfo], 
                       frame_time: float):
        """处理显示逻辑"""
        # 获取当前状态
        fps = self.performance_monitor.get_current_fps(frame_time)
        current_analysis = self.analyzer.get_current_analysis()
        is_analyzing = self.analyzer.is_busy()
        status_text = "正在分析中..." if is_analyzing else "分析空闲"
        
        # 绘制信息覆盖层
        display_frame = self.display_manager.draw_info_overlay(
            frame, fps, detection_info, status_text, current_analysis, is_analyzing
        )
        
        # 调整显示大小并显示
        display_frame = self.display_manager.resize_for_display(display_frame)
        self.display_manager.show_frame(display_frame)
    
    def _cleanup(self):
        """清理资源"""
        self.logger.info("正在清理资源...")
        self.running = False
        
        # 停止各个组件
        self.analyzer.stop()
        self.camera_manager.release()
        self.display_manager.cleanup()
        
        # 输出性能和分析统计
        self._log_final_stats()
        self.logger.info("所有资源已释放，程序结束")
    
    def _log_final_stats(self):
        """记录最终统计信息"""
        perf_summary = self.performance_monitor.get_summary()
        analysis_stats = self.analyzer.get_stats()
        
        self.logger.info("=== 性能总结 ===")
        for key, value in perf_summary.items():
            self.logger.info(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
        
        self.logger.info("=== 分析统计 ===")
        for key, value in analysis_stats.items():
            self.logger.info(f"{key}: {value}")
