#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
字体路径工具模块
提供统一的字体文件路径解析功能
"""

import os
import sys

def get_base_dir():
    """获取程序基础目录，支持打包后的环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境 (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # 开发环境 - 返回项目根目录
        current_file = os.path.abspath(__file__)
        # 从 src/utils/font_utils.py 回到根目录
        return os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

def get_font_path(font_name='msyh.ttc'):
    """
    获取字体文件的绝对路径，支持打包后的环境
    
    Args:
        font_name (str): 字体文件名，默认为 'msyh.ttc'
    
    Returns:
        str: 字体文件的绝对路径
    """
    base_dir = get_base_dir()
    font_path = os.path.join(base_dir, 'font', font_name)
    
    # 如果字体文件不存在，返回系统默认字体
    if not os.path.exists(font_path):
        print(f"警告：字体文件不存在 {font_path}，将使用系统默认字体")
        # 尝试使用系统字体
        if os.name == 'nt':  # Windows
            return 'C:/Windows/Fonts/msyh.ttc'
        else:  # Linux/Mac
            return '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    
    return os.path.normpath(font_path)