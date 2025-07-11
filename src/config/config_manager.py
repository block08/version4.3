import configparser
from src.utils import shared_data

def load_config():
    config = configparser.ConfigParser()
    try:
        config.read('serial_config.ini')
        shared_data.global_response_delay = float(config['TIMING']['response_delay'])
        shared_data.global_clear_delay = float(config['TIMING']['clear_delay'])
    except Exception as e:
        print(f"配置加载错误: {e}")
        print("使用默认延时值")