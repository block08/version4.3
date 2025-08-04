#!/usr/bin/env python3
"""
EEG心理学绘图实验系统 - 主入口文件
"""

import sys
import os

# 获取当前执行文件的目录
if getattr(sys, 'frozen', False):
    # 打包后的环境 (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 开发环境
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置工作目录为程序所在目录
os.chdir(BASE_DIR)

# 将项目根目录和src目录添加到 sys.path
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from src.ui.LoginWindow import LoginWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys
import ctypes
import platform

def set_app_icon(app):
    """设置应用图标，包含错误处理"""
    icon_paths = [
        'icons/EEG_paint.ico',
        os.path.join(BASE_DIR, 'icons/EEG_paint.ico'),
        'icons/EEG_paint.jpg'
    ]
    
    for icon_path in icon_paths:
        try:
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
                print(f"成功设置应用图标: {icon_path}")
                return True
        except Exception as e:
            print(f"设置图标 {icon_path} 失败: {e}")
            continue
    
    print("警告: 未找到可用的图标文件，使用默认图标")
    return False

def set_windows_taskbar_icon():
    """修复Windows任务栏图标显示问题"""
    if platform.system() == 'Windows':
        try:
            myappid = 'EEG.DrawingExperiment.v4.3'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            print("Windows任务栏图标已设置")
        except Exception as e:
            print(f"设置Windows任务栏图标失败: {e}")

if __name__ == "__main__":
    # 启动登录界面
    app = QApplication(sys.argv)
    
    # 设置Windows任务栏图标
    set_windows_taskbar_icon()
    
    # 设置应用图标
    set_app_icon(app)
    
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())