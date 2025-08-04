import configparser
import os
from src.utils import shared_data

def get_config_file_path(filename):
    """获取配置文件的绝对路径，确保打包后能正确找到"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, filename)

def get_id_file_path():
    """获取id.txt文件的绝对路径"""
    return get_config_file_path("id.txt")

def get_name_file_path():
    """获取name.txt文件的绝对路径"""
    return get_config_file_path("name.txt")

def load_config():
    config = configparser.ConfigParser()
    try:
        config.read('serial_config.ini')
        shared_data.global_response_delay = float(config['TIMING']['response_delay'])
        shared_data.global_clear_delay = float(config['TIMING']['clear_delay'])
    except Exception as e:
        print(f"配置加载错误: {e}")
        print("使用默认延时值")