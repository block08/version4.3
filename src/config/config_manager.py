import configparser
import os
import sys
from src.utils import shared_data

def get_base_dir():
    """获取程序基础目录，支持打包后的环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境 (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # 开发环境 - 返回项目根目录
        current_file = os.path.abspath(__file__)
        # 从 src/config/config_manager.py 回到根目录
        return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

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

def get_serial_config_path():
    """获取串口配置文件的绝对路径"""
    return get_config_file_path("serial_config.ini")

def load_config():
    config = configparser.ConfigParser()
    try:
        config_path = get_serial_config_path()
        config.read(config_path)
        shared_data.global_response_delay = float(config['TIMING']['response_delay'])
        shared_data.global_clear_delay = float(config['TIMING']['clear_delay'])
        print(f"配置加载成功: {config_path}")
    except Exception as e:
        print(f"配置加载错误: {e}")
        print("使用默认延时值")
        # 设置默认值
        shared_data.global_response_delay = 0.01
        shared_data.global_clear_delay = 0.01