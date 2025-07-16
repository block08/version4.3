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
import sys

if __name__ == "__main__":
    # 启动登录界面
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())