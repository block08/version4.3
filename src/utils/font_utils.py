#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
字体路径工具模块
提供统一的字体文件路径解析功能
"""

import os

def get_font_path(font_name='msyh.ttc'):
    """
    获取字体文件的绝对路径
    
    Args:
        font_name (str): 字体文件名，默认为 'msyh.ttc'
    
    Returns:
        str: 字体文件的绝对路径
    """
    # 获取当前文件所在目录
    current_dir = os.path.dirname(__file__)
    # 构建字体文件路径（相对于项目根目录）
    font_path = os.path.join(current_dir, '../../font', font_name)
    # 返回规范化的绝对路径
    return os.path.normpath(font_path)