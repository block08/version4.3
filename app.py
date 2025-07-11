#!/usr/bin/env python3
"""
EEG心理学绘图实验系统 - 主入口文件
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.LoginWindow import LoginWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    # 启动登录界面
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())