import os
import yaml
import sys

def load_config():
    """加载配置文件"""
    try:
        # 获取程序运行的目录路径，打包后为exe后frozen会被设置成True
        if getattr(sys, 'frozen', False):
            # 打包后的exe运行路径
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境运行路径,以执行程序所在目录为基准
            import __main__
            base_path = os.path.dirname(os.path.abspath( __main__.__file__))
        config_path = os.path.join(base_path, 'config.yml')
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            return {}
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config if config is not None else {}
    except Exception as e:
        print(f"加载配置文件时发生错误: {e}")
        return {}

class Config:
    """
    配置文件类,用于获取执行文件所在目录下的config.yml文件的内容
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.data = load_config()