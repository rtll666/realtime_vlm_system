"""
实时视觉语言模型系统 - 主入口
"""
from app import RealtimeVLMApp
from config.config import Config

def main():
    """主函数"""
    # 创建配置
    config = Config()
    
    # 创建并运行应用程序
    app = RealtimeVLMApp(config)
    app.run()

if __name__ == "__main__":
    main()
