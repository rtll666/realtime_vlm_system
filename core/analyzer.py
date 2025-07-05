"""
Qwen分析器模块
"""
import threading
import time
import base64
from queue import Queue, Empty
import cv2
import numpy as np
from openai import OpenAI
from typing import Optional
from models.data_models import DetectionInfo, AnalysisResult
from utils.logger import Logger
from config.config import Config

class QwenAnalyzer:
    """Qwen分析器类"""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.analysis_queue = Queue(maxsize=1)
        self.current_analysis = "等待分析..."
        self.is_analyzing = False
        self.worker_thread = None
        self.stop_thread = False
        self.client = self._init_client()
        self.analysis_count = 0
        
    def _init_client(self) -> OpenAI:
        """初始化OpenAI客户端"""
        try:
            client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
            self.logger.info("Qwen客户端初始化成功")
            return client
        except Exception as e:
            self.logger.error(f"初始化Qwen客户端失败: {e}")
            raise
            
    def start_worker(self):
        """启动分析工作线程"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.stop_thread = False
            self.worker_thread = threading.Thread(target=self._worker, daemon=True, name="QwenWorker")
            self.worker_thread.start()
            self.logger.info("Qwen分析工作线程已启动")
            
    def _worker(self):
        """后台工作线程，处理分析请求"""
        self.logger.info("Qwen工作线程开始运行")
        
        while not self.stop_thread:
            try:
                frame, detection_info = self.analysis_queue.get(timeout=1)
                if frame is not None and detection_info is not None:
                    self._process_analysis(frame, detection_info)
                self.analysis_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"分析工作线程异常: {e}")
                continue
        
        self.logger.info("Qwen工作线程已停止")
                
    def _process_analysis(self, frame: np.ndarray, detection_info: DetectionInfo):
        """处理单个分析任务"""
        try:
            self.is_analyzing = True
            self.analysis_count += 1
            self.logger.info(f"开始第{self.analysis_count}次分析...")
            
            start_time = time.time()
            result = self._analyze_frame_with_qwen(frame, detection_info)
            analysis_time = time.time() - start_time
            
            self.current_analysis = result
            self.logger.info(f"分析完成 (耗时: {analysis_time:.2f}s): {result}")
            
        except Exception as e:
            self.logger.error(f"分析过程异常: {e}")
            self.current_analysis = "分析失败"
        finally:
            self.is_analyzing = False
            
    def _analyze_frame_with_qwen(self, frame: np.ndarray, detection_info: DetectionInfo) -> str:
        """调用Qwen API进行分析"""
        if detection_info.is_empty():
            return "未检测到铁屑"
        
        try:
            # 图像编码优化
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.config.jpeg_quality]
            success, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            if not success:
                raise Exception("图像编码失败")
            
            base64_image = base64.b64encode(buffer).decode('utf-8')
            prompt = self._build_prompt(detection_info)
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{
                    "role": "user", 
                    "content": [
                        {"type": "image_url", 
                         "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        {"type": "text", "text": prompt}
                    ]
                }],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Qwen API调用失败: {e}")
            return f"API调用失败: {str(e)}"
    
    def _build_prompt(self, detection_info: DetectionInfo) -> str:
        """构建分析提示词"""
        summary = detection_info.get_summary_text()
        return (
            "机床铁屑实时监控，铁屑分为bad, medium, good三类。"
            f"检测结果：\n{summary}\n"
            "请用一句话简述刀头磨损状态。"
        )
    
    def add_analysis_task(self, frame: np.ndarray, detection_info: DetectionInfo) -> bool:
        """添加分析任务到队列"""
        try:
            # 清空旧任务
            while not self.analysis_queue.empty():
                try:
                    self.analysis_queue.get_nowait()
                    self.analysis_queue.task_done()
                except Empty:
                    break
            
            # 添加新任务
            self.analysis_queue.put((frame.copy(), detection_info), block=False)
            return True
        except Exception as e:
            self.logger.warning(f"添加分析任务失败: {e}")
            return False
    
    def get_current_analysis(self) -> str:
        """获取当前分析结果"""
        return self.current_analysis
    
    def is_busy(self) -> bool:
        """检查是否正在分析"""
        return self.is_analyzing
    
    def get_stats(self) -> dict:
        """获取分析统计信息"""
        return {
            'total_analysis': self.analysis_count,
            'is_analyzing': self.is_analyzing,
            'queue_size': self.analysis_queue.qsize()
        }
    
    def stop(self):
        """停止工作线程"""
        self.stop_thread = True
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=3)
        self.logger.info("Qwen分析器已停止")
