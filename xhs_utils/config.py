import os
from dotenv import load_dotenv
from loguru import logger

# 加载.env文件
load_dotenv()

class Config:
    """
    配置管理类
    """
    
    def __init__(self):
        # API配置
        self.BASE_URL = os.getenv('BASE_URL', 'https://edith.xiaohongshu.com')
        self.USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        
        # 请求配置
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))  # 10秒超时
        self.API_DELAY_MIN = float(os.getenv('API_DELAY_MIN', '1'))  # 最小延迟1秒
        self.API_DELAY_MAX = float(os.getenv('API_DELAY_MAX', '3'))  # 最大延迟3秒
        
        # 并发配置
        self.THREAD_POOL_SIZE = int(os.getenv('THREAD_POOL_SIZE', '4'))  # 线程池大小
        
        # 文件配置
        self.STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
        self.TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'datas', 'temp')
        
        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # 初始化检查
        self._check_config()
    
    def _check_config(self):
        """
        检查配置的有效性
        """
        # 确保临时目录存在
        if not os.path.exists(self.TEMP_DIR):
            os.makedirs(self.TEMP_DIR)
            logger.info(f"创建临时目录: {self.TEMP_DIR}")
    
    def get(self, key, default=None):
        """
        获取配置项
        :param key: 配置项名称
        :param default: 默认值
        :return: 配置项值
        """
        return getattr(self, key, default)

# 创建全局配置实例
config = Config()
