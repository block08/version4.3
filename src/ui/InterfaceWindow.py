#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import threading
import time
from src.utils.thread_manager import thread_manager
import pandas as pd
import serial
import serial.tools.list_ports
import glob
import re
from PyQt5 import QtCore, QtGui
# 修正并补充所有需要的 PyQt5 类导入，避免 "Qt" 相关的报错
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QDialog, QStyle, QFrame,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QWidget)

from src.tests import ABtest
from src.tests import ACtest
from src.tests import Atest
from src.tests import Btest
from src.tests import Ctest
from src.ui import InterfaceUI
from src.core import main
from src.core import main_simulation
from src.utils import shared_data
from src.hardware.check_serial_connection import check_serial_connection
from src.hardware.serial_marker import serial_marker, initialize_serial, close_serial
from src.config.serial_config_manager import serial_config
# from src.utils.input_method_detector import get_input_method_detector  # 已替换为Caps Lock检测


# 为了让此文件独立运行，我们在此处进行前向声明。
# 在您的实际项目中，这个类应该从定义它的文件中导入。
class LoginWindow(QMainWindow):
    pass


class CustomDialog(QDialog):
    """
    完全自定义的对话框，用于替代QMessageBox，以实现更好的布局控制和样式。
    """

    def __init__(self, parent, icon_type, title, text, font_size=22, width=700, height=350, button_type='ok'):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建主容器框架，用于实现明显的边框 (根据用户需求恢复)
        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, width, height)
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 20px;
                border: 2px solid #555;  /* 恢复边框 */
            }}
        """)

        # 在主框架内创建布局
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        main_layout.addStretch(1)

        # --- 修改为 QGridLayout 来实现特殊对齐 ---
        content_layout = QGridLayout()  # <-- 修改：使用网格布局
        content_layout.setSpacing(20)

        # 文字标签
        text_label = QLabel(text, self)
        text_label.setFont(QFont("Microsoft YaHei", font_size))
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignCenter)  # <-- 修改：让文字在自己的控件内也居中
        text_label.setMinimumWidth(500)  # 设置最小宽度确保文字有足够空间
        text_label.setStyleSheet("border: none; color: black;")
        # <-- 修改：将文字放置在0行0列，并让它在单元格内居中
        content_layout.addWidget(text_label, 0, 0, Qt.AlignCenter)

        # 图标标签
        icon_label = QLabel(self)
        icon_pixmap = self.style().standardIcon(icon_type).pixmap(64, 64)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(64, 64)
        icon_label.setStyleSheet("border: none;")
        # <-- 修改：将图标也放置在0行0列，但让它在单元格内靠左
        content_layout.addWidget(icon_label, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)
        # --- 修改区域结束 ---

        main_layout.addLayout(content_layout)
        main_layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if button_type == 'yes_no':
            # 创建"是"按钮和其容器
            yes_container = QVBoxLayout()
            yes_button = QPushButton("确认", self)
            yes_button.setCursor(QCursor(Qt.PointingHandCursor))
            yes_button.setFixedSize(220, 65)
            yes_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            yes_button.setStyleSheet("""
                QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                QPushButton:hover { background-color: #1f4788; color: white; border: 2px solid #1f4788; }
                QPushButton:pressed { background-color: #1f4788; color: white; }
            """)
            yes_button.clicked.connect(self.accept)
            
            yes_hint = QLabel("按Y键", self)
            yes_hint.setAlignment(Qt.AlignCenter)
            yes_hint.setFont(QFont("Microsoft YaHei", 25))
            yes_hint.setStyleSheet("color: #000000; border: none;")
            
            yes_container.addWidget(yes_button)
            yes_container.addWidget(yes_hint)
            yes_container.setSpacing(5)
            
            yes_widget = QWidget()
            yes_widget.setLayout(yes_container)
            button_layout.addWidget(yes_widget)

            # 创建"否"按钮和其容器
            no_container = QVBoxLayout()
            no_button = QPushButton("取消", self)
            no_button.setCursor(QCursor(Qt.PointingHandCursor))
            no_button.setFixedSize(220, 65)
            no_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            no_button.setStyleSheet("""
                QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                QPushButton:hover { background-color: #1f4788; color: white; border: 2px solid #1f4788; }
                QPushButton:pressed { background-color: #1f4788; color: white; }
            """)
            no_button.clicked.connect(self.reject)
            
            no_hint = QLabel("按N键", self)
            no_hint.setAlignment(Qt.AlignCenter)
            no_hint.setFont(QFont("Microsoft YaHei", 25))
            no_hint.setStyleSheet("color: #000000; border: none;")
            
            no_container.addWidget(no_button)
            no_container.addWidget(no_hint)
            no_container.setSpacing(5)
            
            no_widget = QWidget()
            no_widget.setLayout(no_container)
            button_layout.addWidget(no_widget)
        else:  # 默认为 'ok'
            # 创建"确定"按钮和其容器
            ok_container = QVBoxLayout()
            ok_button = QPushButton("确定", self)
            ok_button.setCursor(QCursor(Qt.PointingHandCursor))
            ok_button.setFixedSize(220, 65)
            ok_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            ok_button.setStyleSheet("""
                QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                QPushButton:hover { background-color: #1f4788; color: white; border: 2px solid #1f4788; }
                QPushButton:pressed { background-color: #1f4788; color: white; }
            """)
            ok_button.clicked.connect(self.accept)
            
            ok_hint = QLabel("按Y键", self)
            ok_hint.setAlignment(Qt.AlignCenter)
            ok_hint.setFont(QFont("Microsoft YaHei", 25))
            ok_hint.setStyleSheet("color: #000000; border: none;")
            
            ok_container.addWidget(ok_button)
            ok_container.addWidget(ok_hint)
            ok_container.setSpacing(5)
            
            ok_widget = QWidget()
            ok_widget.setLayout(ok_container)
            button_layout.addWidget(ok_widget)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)

    def keyPressEvent(self, event):
        """处理键盘事件"""
        try:
            if event.key() == Qt.Key_Y:
                self.accept()
            elif event.key() == Qt.Key_N:
                self.reject()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"KeyPressEvent error: {e}")
            super().keyPressEvent(event)

    def showEvent(self, event):
        """重写 showEvent 以在显示时调整窗口位置到父窗口正中心。"""
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().geometry()
            parent_center = parent_rect.center()
            x = parent_center.x() - self.width() // 2
            y = parent_center.y() - self.height() // 2
            self.move(x, y)

    @staticmethod
    def show_message(parent, icon_type, title, text, font_size=22):
        # 根据文字长度自动调整对话框尺寸
        text_length = len(text)
        if text_length > 12:  # 对于较长文字使用更大尺寸
            width, height = 750, 380
        elif text_length > 8:  # 中等长度文字
            width, height = 700, 350
        else:  # 短文字
            width, height = 600, 300
        dialog = CustomDialog(parent, icon_type, title, text, font_size, width, height, button_type='ok')
        return dialog.exec_()

    @staticmethod
    def ask_question(parent, icon_type, title, text, font_size=22):
        # 根据文字长度自动调整对话框尺寸
        text_length = len(text)
        if text_length > 12:  # 对于较长文字使用更大尺寸
            width, height = 750, 380
        elif text_length > 8:  # 中等长度文字
            width, height = 700, 350
        else:  # 短文字
            width, height = 600, 300
        dialog = CustomDialog(parent, icon_type, title, text, font_size, width, height, button_type='yes_no')
        return dialog.exec_()


class Interfacewindow(QMainWindow):
    """
    应用程序的主窗口类。
    """

    def __init__(self):
        super().__init__()
        self.ui = InterfaceUI.Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 不在构造函数中显示窗口，等待登录完成后再显示

        # 初始化线程管理
        self.current_game_thread = None
        self.current_stop_event = None
        self.is_game_running = False  # 游戏运行状态标志

        # 初始化导航按钮状态管理
        self.init_navigation_system()

        # 集中设置所有信号连接
        self.setup_connections()
        
        # 设置所有按钮的手型光标
        self.setup_button_cursors()


        # 用于在重新登录时创建新的登录窗口实例
        self.login_window_instance = None

        # 重新登录标志，用于区分重新登录和正常退出
        self.is_relogin = False

        # 串口检测相关变量
        self.current_detected_port = None

        # 初始化串口状态显示
        self.initialize_serial_ui()
        
        # 初始化Caps Lock状态显示
        self.initialize_caps_lock_ui()

    def init_navigation_system(self):
        """初始化导航按钮状态管理系统"""
        # 定义页面索引到按钮的映射关系
        self.nav_buttons = {
            0: self.ui.pushButton_macro_guidance,  # page_home 对应 宏观指导语按钮
            1: self.ui.pushButton_exercise,  # page_exercise 对应 练习按钮
            2: self.ui.pushButton_main,  # page_main 对应 正式实验按钮
            3: self.ui.pushButton_highestscore,  # page_highestscore 对应 最高纪录按钮
            4: self.ui.pushButton_data,  # page_data 对应 数据查看按钮
            # 5: self.ui.pushButton_setting  # page_serial 对应 串口设置按钮 - 已注释
        }

        # 定义按钮的正常状态样式
        self.normal_button_style = """
            QPushButton{
                background-color: rgb(255, 255, 255);
                border: 2px solid rgb(51, 51, 51);
                color: rgb(51, 51, 51);
                font: 50pt "微软雅黑";
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover{
                background-color: rgb(230, 240, 255);
                border: 2px solid rgb(34, 34, 34);
                color: rgb(34, 34, 34);
            }
            QPushButton:pressed{
                background-color: #1f4788;
                border: 2px solid #1f4788;
                color: white;
                padding-left:12px;
                padding-top:12px;
            }
        """

        # 定义按钮的激活状态样式 - 使用深蓝色高亮
        self.active_button_style = """
            QPushButton{
                background-color: #1f4788;
                border: 2px solid #1f4788;
                color: rgb(255, 255, 255);
                font: 50pt "微软雅黑";
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:pressed{
                background-color: #1f4788;
                padding-left:3px;
                padding-top:3px;
            }
        """

        # 连接stackedWidget的页面切换信号
        self.ui.stackedWidget.currentChanged.connect(self.on_page_changed)

        # 初始化所有按钮状态
        self.update_navigation_buttons(self.ui.stackedWidget.currentIndex())

    @pyqtSlot(int)
    def on_page_changed(self, index):
        """页面切换时的回调函数"""
        self.update_navigation_buttons(index)

    def update_navigation_buttons(self, current_page_index):
        """更新导航按钮状态"""
        try:
            # 重置所有按钮为正常状态
            for button in self.nav_buttons.values():
                if button:  # 确保按钮存在
                    button.setStyleSheet(self.normal_button_style)

            # 设置当前页面对应的按钮为激活状态
            if current_page_index in self.nav_buttons:
                current_button = self.nav_buttons[current_page_index]
                if current_button:
                    current_button.setStyleSheet(self.active_button_style)

        except Exception as e:
            print(f"更新导航按钮状态时出错: {e}")

    def update_button_state_manual(self, page_index):
        """手动更新按钮状态，用于直接执行功能的按钮"""
        self.update_navigation_buttons(page_index)

    def go_main_with_state(self):
        """执行正式实验"""
        # 直接执行功能，不更新按钮状态（因为不切换页面）
        self.go_main()


    def initialize_serial_ui(self):
        """初始化串口UI状态"""
        # 设置初始状态
        self.ui.label_current_port.setText("未检测")
        self.ui.label_status_text.setText("端口未连接")
        
        # 动态创建COM状态标签
        self.create_com_status_label()

        # 启动优化的串口监控（Win7 SP1优化）
        self.setup_optimized_serial_monitoring()

    def create_com_status_label(self):
        """动态创建COM状态标签"""
        try:
            # 创建COM状态容器
            self.com_status_widget = QWidget()
            self.com_status_layout = QHBoxLayout(self.com_status_widget)
            self.com_status_layout.setContentsMargins(0, 0, 0, 0)
            self.com_status_layout.setSpacing(5)
            
            # 创建图标标签
            self.com_status_icon_label = QLabel()
            self.com_status_icon_label.setFixedSize(80, 80)  # 增大图标尺寸到最大
            self.com_status_icon_label.setStyleSheet("""
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)
            self.com_status_icon_label.setAlignment(Qt.AlignCenter)  # 图标居中
            
            # 创建文本标签
            self.com_status_text_label = QLabel("COM未连接")
            self.com_status_text_label.setMinimumSize(200, 50)
            self.com_status_text_label.setFont(QFont("微软雅黑", 36, QFont.Bold))
            self.com_status_text_label.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(231, 76, 60);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)
            self.com_status_text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # 添加Qt警告图标
            warning_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            warning_pixmap = warning_icon.pixmap(32, 32)  # 先获取标准尺寸
            # 强制缩放到80x80像素
            scaled_pixmap = warning_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.com_status_icon_label.setPixmap(scaled_pixmap)
            
            # 添加到布局
            self.com_status_layout.addStretch()
            self.com_status_layout.addWidget(self.com_status_icon_label)
            self.com_status_layout.addWidget(self.com_status_text_label)
            
            # 找到重新登录按钮的布局
            relogin_button = self.ui.pushButton_relogin
            parent_layout = relogin_button.parent().layout()
            
            if parent_layout:
                # 获取重新登录按钮在布局中的位置
                button_index = -1
                for i in range(parent_layout.count()):
                    if parent_layout.itemAt(i).widget() == relogin_button:
                        button_index = i
                        break
                
                if button_index >= 0:
                    # 在重新登录按钮前插入COM状态容器
                    parent_layout.insertWidget(button_index, self.com_status_widget)
                    print("COM状态标签已成功添加到界面")
                else:
                    print("未找到重新登录按钮的位置")
            else:
                print("未找到重新登录按钮的父布局")
                
        except Exception as e:
            print(f"创建COM状态标签时出错: {e}")

    def initialize_caps_lock_ui(self):
        """初始化Caps Lock状态UI"""
        try:
            # 创建输入法状态容器
            self.input_method_widget = QWidget()
            self.input_method_layout = QHBoxLayout(self.input_method_widget)
            self.input_method_layout.setContentsMargins(0, 0, 0, 0)
            self.input_method_layout.setSpacing(5)
            
            # 创建图标标签
            self.input_method_icon_label = QLabel()
            self.input_method_icon_label.setFixedSize(80, 80)  # 增大图标尺寸到最大
            self.input_method_icon_label.setStyleSheet("""
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)
            self.input_method_icon_label.setAlignment(Qt.AlignCenter)  # 图标居中
            
            # 创建文本标签
            self.input_method_text_label = QLabel("大写锁定已开启")
            self.input_method_text_label.setFont(QFont("微软雅黑", 36, QFont.Bold))
            
            # 添加到布局
            self.input_method_layout.addWidget(self.input_method_icon_label)
            self.input_method_layout.addWidget(self.input_method_text_label)
            self.input_method_layout.addStretch()
            
            # 设置初始样式（假设Caps Lock开启）
            self.set_caps_lock_status_style(True)
            
            # 将容器添加到COM状态标签的旁边
            if hasattr(self, 'com_status_widget'):
                # 获取COM状态容器的父布局
                com_parent_layout = self.com_status_widget.parent().layout()
                if com_parent_layout:
                    # 获取COM状态容器的位置
                    com_index = -1
                    for i in range(com_parent_layout.count()):
                        if com_parent_layout.itemAt(i).widget() == self.com_status_widget:
                            com_index = i
                            break
                    
                    if com_index >= 0:
                        # 在COM状态容器前插入Caps Lock状态容器
                        com_parent_layout.insertWidget(com_index, self.input_method_widget)
                        print("Caps Lock状态标签已成功添加到界面")
                    else:
                        print("未找到COM状态容器的位置")
                else:
                    print("未找到COM状态容器的父布局")
            
            # 安装事件过滤器来检测按键事件
            QApplication.instance().installEventFilter(self)
            print("Caps Lock事件监听已启动")
            
            # 立即检查一次当前Caps Lock状态并设置初始显示
            current_status = self.is_caps_lock_on()
            self.on_caps_lock_changed(current_status)
            
        except Exception as e:
            print(f"初始化Caps Lock状态UI时出错: {e}")

    def is_caps_lock_on(self):
        """检测Caps Lock是否打开"""
        try:
            import ctypes
            # 使用Windows API检测Caps Lock状态
            # VK_CAPITAL = 0x14 是Caps Lock的虚拟键码
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 1)
        except Exception as e:
            print(f"检测Caps Lock状态时出错: {e}")
            return False

    def eventFilter(self, obj, event):
        """事件过滤器，监听Caps Lock按键事件"""
        try:
            if event.type() == QEvent.KeyPress or event.type() == QEvent.KeyRelease:
                # 检查是否是Caps Lock键 (Qt.Key_CapsLock)
                if event.key() == Qt.Key_CapsLock and event.type() == QEvent.KeyPress:
                    # Caps Lock被按下，延迟检查状态（因为状态变化有延迟）
                    QTimer.singleShot(50, self.check_caps_lock_status_once)
        except Exception as e:
            print(f"事件过滤器错误: {e}")
        return super().eventFilter(obj, event)
    
    def check_caps_lock_status_once(self):
        """检查一次Caps Lock状态"""
        try:
            current_status = self.is_caps_lock_on()
            # 只有状态改变时才更新
            if not hasattr(self, '_last_caps_status') or self._last_caps_status != current_status:
                self._last_caps_status = current_status
                self.on_caps_lock_changed(current_status)
        except Exception as e:
            print(f"检查Caps Lock状态时出错: {e}")

    def set_caps_lock_status_style(self, is_caps_on):
        """设置Caps Lock状态标签的样式"""
        if is_caps_on:
            # Caps Lock打开 - 黑色，无图标
            self.input_method_text_label.setText("大写锁定已开启")
            self.input_method_text_label.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(0, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)
            # 清除图标
            self.input_method_icon_label.setPixmap(QtGui.QPixmap())
        else:
            # Caps Lock关闭 - 红色警告，添加Qt警告图标
            self.input_method_text_label.setText("大写锁定未开启")
            self.input_method_text_label.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(255, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)
            # 添加Qt警告图标
            warning_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            warning_pixmap = warning_icon.pixmap(32, 32)  # 先获取标准尺寸
            # 强制缩放到80x80像素
            scaled_pixmap = warning_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.input_method_icon_label.setPixmap(scaled_pixmap)

    def on_caps_lock_changed(self, is_caps_on):
        """Caps Lock状态改变的处理函数"""
        try:
            self.set_caps_lock_status_style(is_caps_on)
            
            # 控制Caps Lock提醒标签的显示/隐藏
            if hasattr(self.ui, 'label_input_method_reminder'):
                if is_caps_on:
                    # Caps Lock开启时隐藏提醒
                    self.ui.label_input_method_reminder.hide()
                else:
                    # Caps Lock关闭时显示提醒
                    self.ui.label_input_method_reminder.show()
            
            print(f"Caps Lock状态变更: {'开启' if is_caps_on else '关闭'}")
        except Exception as e:
            print(f"处理Caps Lock状态变更时出错: {e}")

    def find_ch340_port(self):
        """查找USB-SERIAL CH340设备"""
        try:
            ch340_port = None
            ports = serial.tools.list_ports.comports()

            for port in ports:
                # 检查设备描述中是否包含CH340相关信息
                port_description = port.description.upper()
                if any(keyword in port_description for keyword in ['CH340', 'USB-SERIAL CH340']):
                    ch340_port = port.device
                    break

            return ch340_port
        except Exception as e:
            print(f"查找CH340设备时出错: {e}")
            return None

    def get_all_com_ports(self):
        """获取所有COM口，但排除蓝牙设备"""
        try:
            com_ports = []
            ports = serial.tools.list_ports.comports()

            for port in ports:
                port_description = port.description.upper()
                # 排除蓝牙相关设备
                bluetooth_keywords = ['BLUETOOTH', '蓝牙', 'BT', 'WIRELESS']
                is_bluetooth = any(keyword in port_description for keyword in bluetooth_keywords)

                if not is_bluetooth:
                    com_ports.append(port.device)

            return com_ports
        except Exception as e:
            print(f"获取COM口时出错: {e}")
            return []

    def showEvent(self, event):
        """重写 showEvent，在窗口显示时更新用户信息。"""
        super().showEvent(event)
        self.update_user_button_text()

    def update_user_button_text(self):
        """获取登录用户标识并更新按钮文本。"""
        try:
            user1 = getattr(shared_data, 'user1_mark', None)
            user2 = getattr(shared_data, 'user2_mark', None)
            user3 = getattr(shared_data, 'user3_mark', None)

            # 更新顶部用户信息按钮
            if user1 and user2 and user3:
                user_text = f"| 被测：{user1} | 辅助：{user2} 和 {user3} "
                self.ui.pushButton.setText(user_text)
            else:
                self.ui.pushButton.setText("用户")

            # 更新练习按钮文本
            self.update_practice_button_texts(user1, user2, user3)
            
            # 更新介绍内容中的用户信息
            self.update_intro_content(user1, user2, user3)
        except Exception as e:
            print(f"更新用户按钮时出错: {e}")
            self.ui.pushButton.setText("用户")

    def update_practice_button_texts(self, user1, user2, user3):
        """更新练习按钮的文本。"""
        try:
            # 保持按钮原有的固定文字，不根据用户名动态修改
            self.ui.pushButton_4.setText("单独绘图")
            self.ui.pushButton_9.setText("合作绘图")
        except Exception as e:
            print(f"更新练习按钮文本时出错: {e}")
    
    def update_intro_content(self, user1, user2, user3):
        """更新介绍内容中的用户信息。"""
        try:
            # 使用获取到的用户信息，如果为空则使用默认值
            u1 = user1 or '01'
            u2 = user2 or '02'
            u3 = user3 or '03'
            
            # 构建介绍内容
            intro_html = f"""<html><head/><body style='line-height: 1.8;'>
                            <div style='text-align: center; margin-bottom: 30px;'>
                            </div>
                            <div style='text-align: left; margin-bottom: 30px; padding: 20px;'>
                            <p style='font-size: 37pt; margin: 10px 0; color: #000000; line-height: 1.6; text-indent: 60pt;'>
                            1、本实验绘图任务分为三部分：{u1}单独绘图、{u1}与{u2}合作绘图、{u1}与{u3}合作绘图。
                            </p>
                            <p style='font-size: 37pt; margin: 10px 0; color: #000000; line-height: 1.6; text-indent: 60pt;'>
                            2、练习试次阶段，共设置3张绘图任务，可随时退出。
                            </p>
                            <p style='font-size: 37pt; margin: 10px 0; color: #000000; line-height: 1.6; text-indent: 60pt;'>
                            3、正式实验阶段，被测{u1}需独立完成8张绘图任务，随后分别与辅助{u2}，{u3}各完成8张合作绘图任务。
                            </p>
                            <p style='font-size: 37pt; margin: 10px 0; color: #000000; line-height: 1.6; text-indent: 60pt;'>
                            4、正式实验阶段，不得中途退出实验以免导致实验数据不完整。
                            </p>
                            </div>
                            </body></html>"""
            
            self.ui.label_intro_content.setText(intro_html)
            print(f"更新介绍内容: user1={u1}, user2={u2}, user3={u3}")
        except Exception as e:
            print(f"更新介绍内容时出错: {e}")

    def setup_connections(self):
        """设置所有UI控件的信号和槽连接。"""
        self.ui.pushButton_exercise.clicked.connect(self.go_exercise)
        self.ui.pushButton_main.clicked.connect(self.go_main_and_show_page)
        self.ui.pushButton_highestscore.clicked.connect(self.go_highestscore)
        self.ui.pushButton_data.clicked.connect(self.go_data_and_open_folder)
        # self.ui.pushButton_setting.clicked.connect(self.go_setting)  # 端口设置
        self.ui.pushButton_relogin.clicked.connect(self.relogin)
        self.ui.pushButton_4.clicked.connect(self.start_practice_1)
        self.ui.pushButton_9.clicked.connect(self.start_practice_4)

        # 连接宏观指导语按钮
        self.ui.pushButton_macro_guidance.clicked.connect(self.go_home)

    def setup_button_cursors(self):
        """为所有按钮设置手型光标"""
        # 导航按钮
        self.ui.pushButton_macro_guidance.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_exercise.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_main.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_highestscore.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_data.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 功能按钮
        self.ui.pushButton_relogin.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_auto_connect.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_4.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.pushButton_9.setCursor(QCursor(Qt.PointingHandCursor))
        
        # 窗口控制按钮
        self.ui.pushButton_2.setCursor(QCursor(Qt.PointingHandCursor))  # 关闭按钮
        self.ui.pushButton_3.setCursor(QCursor(Qt.PointingHandCursor))  # 最小化按钮
        
        # 其他按钮（这些按钮已在页面简化中移除）
        # if hasattr(self.ui, 'run_main_test'):
        #     self.ui.run_main_test.setCursor(QCursor(Qt.PointingHandCursor))
        # if hasattr(self.ui, 'data_check'):
        #     self.ui.data_check.setCursor(QCursor(Qt.PointingHandCursor))

    def start_practice_1(self):
        """启动1的练习模块。"""
        print(f"[练习启动] 开始启动练习模块1")
        
        # 检查Caps Lock状态
        if not self.is_caps_lock_on():
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "大写锁定警告", 
                                    "未检测到大写锁定开启。\n\n请开启后重新点击单独绘图。")
            return
        
        # 检查是否有游戏正在运行
        if self.is_game_running:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "提示", 
                                    "有练习正在进行中，请等待当前练习结束后再开始新的练习。")
            return
            
        try:
            user1_mark = getattr(shared_data, 'user1_mark', '01')
            print(f"[练习启动] 获取用户1标记: {user1_mark}")

            def extract_number(mark):
                if mark and isinstance(mark, str):
                    if '-' in mark:
                        return mark.split('-')[-1]
                    import re
                    match = re.search(r'\d+$', mark)
                    if match:
                        return match.group()
                return mark

            user1 = extract_number(user1_mark)

            print(f"[练习启动] 正在启动{user1}绘图练习模块...")
            game_function = Atest.Game
            print(f"[练习启动] 获取的游戏函数: {game_function}")
            if game_function:
                self.start_game_thread(game_function)
            else:
                print(f"[练习启动] 错误：游戏函数为空")
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_2(self):
        """启动人员2的练习模块。"""
        print(f"[练习启动] 开始启动练习模块2")
        try:
            user2_mark = getattr(shared_data, 'user2_mark', '02')
            print(f"[练习启动] 获取用户2标记: {user2_mark}")

            def extract_number(mark):
                if mark and isinstance(mark, str):
                    if '-' in mark:
                        return mark.split('-')[-1]
                    import re
                    match = re.search(r'\d+$', mark)
                    if match:
                        return match.group()
                return mark

            user2 = extract_number(user2_mark)

            print(f"[练习启动] 正在启动{user2}绘图练习模块...")
            game_function = Btest.Game
            print(f"[练习启动] 获取的游戏函数: {game_function}")
            if game_function:
                self.start_game_thread(game_function)
            else:
                print(f"[练习启动] 错误：游戏函数为空")
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_3(self):
        """启动合作的练习模块。"""
        try:
            user3_mark = getattr(shared_data, 'user3_mark', '03')

            def extract_number(mark):
                if mark and isinstance(mark, str):
                    if '-' in mark:
                        return mark.split('-')[-1]
                    import re
                    match = re.search(r'\d+$', mark)
                    if match:
                        return match.group()
                return mark

            user3 = extract_number(user3_mark)

            print(f"正在启动{user3}绘图练习模块...")
            game_function = Ctest.Game
            if game_function:
                self.start_game_thread(game_function)
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_4(self):
        """启动人员①&人员②的练习模块。"""
        # 检查Caps Lock状态
        if not self.is_caps_lock_on():
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "大写锁定警告", 
                                    "未检测到大写锁定开启。\n\n请开启后重新点击合作绘图。")
            return
            
        # 检查是否有游戏正在运行
        if self.is_game_running:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "提示", 
                                    "有练习正在进行中，请等待当前练习结束后再开始新的练习。")
            return
            
        try:
            user1_mark = getattr(shared_data, 'user1_mark', '01')
            user2_mark = getattr(shared_data, 'user2_mark', '02')

            def extract_number(mark):
                if mark and isinstance(mark, str):
                    if '-' in mark:
                        return mark.split('-')[-1]
                    import re
                    match = re.search(r'\d+$', mark)
                    if match:
                        return match.group()
                return mark

            user1 = extract_number(user1_mark)
            user2 = extract_number(user2_mark)

            print(f"正在启动{user1}&{user2}绘图练习模块...")
            game_function = ABtest.Game
            if game_function:
                self.start_game_thread(game_function)
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_5(self):
        """启动人员①&人员③的练习模块。"""
        # 检查是否有游戏正在运行
        if self.is_game_running:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "提示", 
                                    "有练习正在进行中，请等待当前练习结束后再开始新的练习。")
            return
            
        try:
            user1_mark = getattr(shared_data, 'user1_mark', '01')
            user3_mark = getattr(shared_data, 'user3_mark', '03')

            def extract_number(mark):
                if mark and isinstance(mark, str):
                    if '-' in mark:
                        return mark.split('-')[-1]
                    import re
                    match = re.search(r'\d+$', mark)
                    if match:
                        return match.group()
                return mark

            user1 = extract_number(user1_mark)
            user3 = extract_number(user3_mark)

            print(f"正在启动{user1}&{user3}绘图练习模块...")
            game_function = ACtest.Game
            if game_function:
                self.start_game_thread(game_function)
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def go_main(self):
        """开始主实验。"""
        # 检查Caps Lock状态
        if not self.is_caps_lock_on():
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "大写锁定警告", 
                                    "未检测到大写锁定开启。\n\n请开启重新点击正式实验。")
            return
            
        # 检查是否有游戏正在运行
        if self.is_game_running:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "提示", 
                                    "有实验正在进行中，请等待当前实验结束后再开始新的实验。")
            return
            
        game_function = None

        # 检查端口连接状态
        if shared_data.global_flag is None:
            # 没有设置端口，询问是否仿真模式
            reply = CustomDialog.ask_question(self, QStyle.SP_MessageBoxQuestion, "运行模式",
                                              "未检测到端口连接。\n\n您想在仿真模式下运行吗？")
            if reply == QDialog.Accepted:
                game_function = main_simulation.Game
            else:
                return
        else:
            # 已设置端口，但需要验证端口是否仍然连接
            current_port = shared_data.global_port

            # 1. 检查设备是否仍在端口列表中
            ch340_port = self.find_ch340_port()
            if ch340_port != current_port:
                # 设备端口发生变化或设备被拔出
                reply = CustomDialog.ask_question(self, QStyle.SP_MessageBoxQuestion, "设备连接异常",
                                                  f"检测到端口状态异常！\n\n"
                                                  f"原端口: {current_port}\n"
                                                  f"当前检测: {'未检测到设备' if ch340_port is None else ch340_port}\n\n"
                                                  f"设备可能已被拔出或端口发生变化。\n"
                                                  f"是否在仿真模式下继续运行？")
                if reply == QDialog.Accepted:
                    game_function = main_simulation.Game
                else:
                    return
            else:
                # 2. 设备仍在相同端口，检查连接状态
                from src.hardware.check_serial_connection import check_serial_connection
                if not check_serial_connection(current_port):
                    # 端口无法连接
                    reply = CustomDialog.ask_question(self, QStyle.SP_MessageBoxQuestion, "端口连接失败",
                                                      f"无法连接到端口 {current_port}！\n\n"
                                                      f"设备可能被拔出或被其他程序占用。\n"
                                                      f"是否在仿真模式下继续运行？")
                    if reply == QDialog.Accepted:
                        game_function = main_simulation.Game
                    else:
                        return
                else:
                    # 端口连接正常，使用正常模式
                    game_function = main.Game

        if game_function:
            # 在实验开始前检查串口状态
            self.check_serial_before_experiment()
            
            # 设置游戏运行状态
            self.is_game_running = True
            
            def run_experiment():
                try:
                    game_function().run()
                finally:
                    # 实验结束后清除运行状态
                    self.is_game_running = False
                    print("[正式实验] 实验结束，清除运行状态")
            
            threading.Thread(target=run_experiment, daemon=True).start()

    def setup_optimized_serial_monitoring(self):
        """设置优化的串口监控（Win7 SP1优化）"""
        self.serial_timer = None
        self.is_serial_connected = False
        
        print("[串口监控] 启动优化监控方案")
        
        # 创建优化的轮询定时器
        self.serial_timer = QTimer()
        self.serial_timer.timeout.connect(self.optimized_serial_check)
        
        # 立即检查一次，然后开始监控
        QTimer.singleShot(500, self.initial_serial_check)
    
    def start_optimized_monitoring(self):
        """启动优化监控（根据连接状态调整频率）"""
        if self.is_serial_connected:
            # 已连接：每5秒检查一次（低频率）
            interval = 5000
            print("[串口监控] 串口已连接，设置低频率: 5秒")
        else:
            # 未连接：每3秒检查一次（高频率）
            interval = 3000
            print("[串口监控] 串口未连接，设置高频率: 3秒")
            
        self.serial_timer.start(interval)
    
    def optimized_serial_check(self):
        """优化的串口检查"""
        try:
            # 执行检测
            self.auto_detect_and_connect()
            
            # 检查状态是否发生变化
            from src.utils import shared_data
            current_status = (shared_data.global_flag == 1 and shared_data.global_port is not None)
            
            if current_status != self.is_serial_connected:
                # 状态发生变化，调整监控频率
                self.is_serial_connected = current_status
                print(f"[串口监控] 状态变化: {'已连接' if current_status else '未连接'}")
                
                # 重新设置监控频率
                self.serial_timer.stop()
                self.start_optimized_monitoring()
                
        except Exception as e:
            print(f"[串口监控] 检查错误: {e}")
    
    def initial_serial_check(self):
        """初始串口检查"""
        print("[串口监控] 开始初始检查...")
        self.optimized_serial_check()
        # 启动持续监控
        self.start_optimized_monitoring()
        print("[串口监控] 初始检查完成")
    
    def check_serial_before_experiment(self):
        """在实验开始前检查串口状态"""
        print("[串口监控] 实验前检查串口状态...")
        self.optimized_serial_check()
        print("[串口监控] 实验前检查完成")
    
    def auto_detect_and_connect(self):
        """自动检测端口并连接"""
        try:
            # 如果已经连接，就不再重复检测
            if shared_data.global_flag == 1 and shared_data.global_port:
                # 验证端口是否仍然可用
                if check_serial_connection(shared_data.global_port):
                    return
                else:
                    # 端口失连，重置状态
                    self.reset_connection_status()

            # 查找CH340端口
            ch340_port = self.find_ch340_port()

            if ch340_port:
                # 检查端口是否可连接
                if check_serial_connection(ch340_port):
                    # 自动连接成功
                    self.set_connected_status(ch340_port)
                else:
                    # 检测到端口但无法连接
                    self.set_detected_but_not_connected_status(ch340_port)
            else:
                # 没有检测到端口
                self.set_no_port_detected_status()

        except Exception as e:
            print(f"自动检测端口时出错: {e}")

    def manual_connect_port(self):
        """手动连接端口（当自动检测失败时）"""
        try:
            ch340_port = self.find_ch340_port()

            if ch340_port:
                if check_serial_connection(ch340_port):
                    self.set_connected_status(ch340_port)
                    # 发送确认信号
                    self.send_marker8(ch340_port)
                    CustomDialog.show_message(self, QStyle.SP_MessageBoxInformation, "连接成功",
                                              f"已成功连接到端口 {ch340_port}")
                else:
                    CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "连接失败",
                                              f"检测到CH340设备 {ch340_port}，但无法连接。请检查设备状态。")
            else:
                CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "未检测到设备",
                                          "未检测到设备，请检查设备连接。")
        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "连接失败",
                                      f"连接端口时出错：{str(e)}")

    def send_marker8(self, port):
        """发送marker8确认连接"""
        try:
            # 初始化端口
            if initialize_serial():
                try:
                    # 发送marker8
                    marker_data = bytes([8])
                    serial_marker(marker_data)
                finally:
                    # 发送完成后关闭串口，释放资源
                    close_serial()
            else:
                print(f"无法初始化端口 {port}")
        except Exception as e:
            # 出现异常时也要确保关闭串口
            close_serial()
            print(f"发送确认信号时出错：{str(e)}")

    def set_connected_status(self, port):
        """设置连接成功状态"""
        # 更新UI显示
        self.ui.label_current_port.setText(port)
        self.ui.label_current_port.setStyleSheet("""
            QLabel {
                font: bold 24pt "微软雅黑";
                color: rgb(46, 204, 113);
                border: 2px solid rgb(46, 204, 113);
                border-radius: 10px;
                background-color: rgb(248, 248, 248);
                padding: 10px;
            }
        """)

        # 更新状态灯为绿色
        self.ui.label_connection_status.setStyleSheet("""
            QLabel {
                border: 3px solid rgb(46, 204, 113);
                border-radius: 70px;
                background-color: rgb(46, 204, 113);
            }
        """)
        self.ui.label_status_text.setText("已自动连接")
        self.ui.label_status_text.setStyleSheet("""
            QLabel {
                border: none;
                color: rgb(0, 0, 0);
                font: 24pt "微软雅黑";
            }
        """)

        # 更新COM状态标签
        if hasattr(self, 'com_status_text_label'):
            self.com_status_text_label.setText(f"{port}已连接")
            self.com_status_text_label.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(0, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)
            # 清除警告图标
            self.com_status_icon_label.setPixmap(QtGui.QPixmap())

        # 禁用连接按钮
        self.ui.pushButton_auto_connect.setEnabled(False)
        self.ui.pushButton_auto_connect.setText("已连接")

        # 设置共享数据
        shared_data.global_flag = 1
        shared_data.global_port = port
        # 强制重新加载配置文件以获取最新的波特率设置
        serial_config.load_config()
        shared_data.global_baudrate = serial_config.get_baudrate()
        
        # 自动发送marker8确认连接
        self.send_marker8(port)

    def set_detected_but_not_connected_status(self, port):
        """设置检测到但无法连接状态"""
        self.ui.label_current_port.setText(f"{port} (无法连接)")
        self.ui.label_current_port.setStyleSheet("""
            QLabel {
                font: bold 24pt "微软雅黑";
                color: rgb(255, 140, 0);
                border: 2px solid rgb(255, 140, 0);
                border-radius: 10px;
                background-color: rgb(248, 248, 248);
                padding: 10px;
            }
        """)

        # 更新状态灯为橙色
        self.ui.label_connection_status.setStyleSheet("""
            QLabel {
                border: 3px solid rgb(255, 140, 0);
                border-radius: 70px;
                background-color: rgb(255, 140, 0);
            }
        """)
        self.ui.label_status_text.setText("检测到设备")
        self.ui.label_status_text.setStyleSheet("""
            QLabel {
                border: none;
                color: rgb(0, 0, 0);
                font: 24pt "微软雅黑";
            }
        """)

        # 启用连接按钮，允许手动重试
        self.ui.pushButton_auto_connect.setEnabled(True)
        self.ui.pushButton_auto_connect.setText("重试连接")

    def set_no_port_detected_status(self):
        """设置未检测到端口状态"""
        self.ui.label_current_port.setText("未检测")
        self.ui.label_current_port.setStyleSheet("""
            QLabel {
                font: bold 24pt "微软雅黑";
                color: rgb(255, 0, 0);
                border: 2px solid rgb(200, 200, 200);
                border-radius: 10px;
                background-color: rgb(248, 248, 248);
                padding: 10px;
            }
        """)

        # 更新状态灯为灰色
        self.ui.label_connection_status.setStyleSheet("""
            QLabel {
                border: 3px solid rgb(100, 100, 100);
                border-radius: 70px;
                background-color: rgb(144, 144, 144);
            }
        """)
        self.ui.label_status_text.setText("端口未连接")
        self.ui.label_status_text.setStyleSheet("""
            QLabel {
                border: none;
                color: rgb(0, 0, 0);
                font: 24pt "微软雅黑";
            }
        """)

        # 更新COM状态标签
        if hasattr(self, 'com_status_text_label'):
            self.com_status_text_label.setText("COM未连接")
            self.com_status_text_label.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(255, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)
            # 添加Qt警告图标
            warning_icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
            warning_pixmap = warning_icon.pixmap(32, 32)  # 先获取标准尺寸
            # 强制缩放到80x80像素
            scaled_pixmap = warning_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.com_status_icon_label.setPixmap(scaled_pixmap)

        # 启用连接按钮
        self.ui.pushButton_auto_connect.setEnabled(True)
        self.ui.pushButton_auto_connect.setText("连接端口")

    def reset_connection_status(self):
        """重置连接状态"""
        shared_data.global_flag = None
        shared_data.global_port = None
        shared_data.global_baudrate = None
        self.set_no_port_detected_status()

    def relogin(self):
        """关闭主界面并返回到登录窗口。"""
        # 先显示重新登录确认对话框
        reply = CustomDialog.ask_question(
            self,
            QStyle.SP_MessageBoxQuestion,
            "确认重新登录",
            "您确定要重新登录吗？"
        )

        # 如果用户确认重新登录
        if reply == QDialog.Accepted:

            try:
                from src.ui.LoginWindow import LoginWindow
                self.login_window_instance = LoginWindow()
                self.login_window_instance.show()
                # 设置标志，表示这是重新登录而不是正常退出
                self.is_relogin = True
                self.close()
            except ImportError:
                QMessageBox.critical(self, "导入错误", "无法从 'login.py' 导入 LoginWindow 类。")

    def confirm_close(self):
        """带确认的关闭方法"""
        # 正常退出时显示确认对话框
        reply = CustomDialog.ask_question(
            self,
            QStyle.SP_MessageBoxQuestion,  # 使用问号图标
            "确认退出",
            "您确定要退出程序吗？"
        )

        # 根据用户的选择决定是否关闭
        if reply == QDialog.Accepted:
            # 清理资源
            self.cleanup_resources()
            # 如果用户点击"是"，直接强制退出整个程序
            print("程序已退出。")
            import os
            os._exit(0)  # 强制终止整个进程，包括所有线程和子进程

    def closeEvent(self, event):
        """重写关闭事件，确保定时器被停止"""
        # 检查是否已经确认关闭（避免重复弹窗）
        if hasattr(self, 'confirmed_close') and self.confirmed_close:
            # 已经确认关闭，直接接受事件
            event.accept()
            return

        # 检查是否是重新登录操作
        if hasattr(self, 'is_relogin') and self.is_relogin:
            # 如果是重新登录，直接关闭窗口，不显示退出确认
            print("重新登录，关闭当前界面。")
            # 清理资源
            self.stop_current_game()
            self.cleanup_resources()
            thread_manager.stop_all_threads()
            event.accept()
            return

        # 正常退出时显示确认对话框
        reply = CustomDialog.ask_question(
            self,
            QStyle.SP_MessageBoxQuestion,  # 使用问号图标
            "确认退出",
            "您确定要退出程序吗？"
        )

        # 根据用户的选择决定是否关闭
        if reply == QDialog.Accepted:
            # 清理资源
            self.cleanup_resources()
            # 如果用户点击"是"，直接强制退出整个程序
            print("程序已退出。")
            import os
            os._exit(0)  # 强制终止整个进程，包括所有线程和子进程
        else:
            # 如果用户点击"否"，则忽略该事件，窗口不会关闭
            event.ignore()

    def go_highestscore(self):
        """切换到最高分页面并加载数据。"""
        self.ui.stackedWidget.setCurrentIndex(3)
        self.load_leaderboard_data()

    def go_data(self):
        """切换到数据显示页面。"""
        self.ui.stackedWidget.setCurrentIndex(4)

    def go_exercise(self):
        """切换到练习页面。"""
        self.ui.stackedWidget.setCurrentIndex(1)

    def go_main_test(self):
        """切换到主实验页面。"""
        self.ui.stackedWidget.setCurrentIndex(2)

    def go_setting(self):
        """切换到端口设置页面。"""
        self.ui.stackedWidget.setCurrentIndex(5)

    def go_home(self):
        """切换到首页。"""
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def go_main_and_show_page(self):
        """切换到正式实验页面并启动实验。"""
        self.ui.stackedWidget.setCurrentIndex(2)
        # 启动实验
        self.go_main()
    
    def go_data_and_open_folder(self):
        """切换到数据查看页面并打开文件夹。"""
        self.ui.stackedWidget.setCurrentIndex(4)
        # 打开文件夹
        self.open_behavioral_data()

    def open_behavioral_data(self):
        """打开Behavioral_data文件夹。"""
        try:
            # 获取程序运行的根目录
            import sys
            
            # 优化路径获取逻辑
            if hasattr(sys, '_MEIPASS'):
                # 打包后的路径，优先检查可执行文件目录，然后检查工作目录
                executable_dir = os.path.dirname(sys.executable)
                current_dir = os.getcwd()
                
                # 尝试多个可能的位置
                possible_paths = [
                    os.path.join(executable_dir, "Behavioral_data"),
                    os.path.join(current_dir, "Behavioral_data"),
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Behavioral_data")
                ]
                
                base_path = None
                behavioral_data_path = None
                
                # 查找存在的路径
                for path in possible_paths:
                    if os.path.exists(path):
                        behavioral_data_path = os.path.abspath(path)
                        base_path = os.path.dirname(behavioral_data_path)
                        break
                
                # 如果都不存在，使用可执行文件目录作为基础路径
                if behavioral_data_path is None:
                    base_path = executable_dir
                    behavioral_data_path = os.path.join(base_path, "Behavioral_data")
            else:
                # 开发环境的路径
                base_path = os.getcwd()
                behavioral_data_path = os.path.join(base_path, "Behavioral_data")
            
            print(f"尝试访问路径：{behavioral_data_path}")
            
            # 检查文件夹是否存在，如果不存在则创建
            if not os.path.exists(behavioral_data_path):
                try:
                    os.makedirs(behavioral_data_path, exist_ok=True)
                    print(f"已创建文件夹：{behavioral_data_path}")
                    CustomDialog.show_message(self, QStyle.SP_MessageBoxInformation, "文件夹已创建", 
                                            f"Behavioral_data文件夹已自动创建：\n{behavioral_data_path}")
                except PermissionError:
                    CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "权限不足", 
                                            f"没有权限在此位置创建文件夹：\n{behavioral_data_path}\n请以管理员身份运行程序或选择其他位置。")
                    return
                except Exception as create_error:
                    CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "创建失败", 
                                            f"无法创建Behavioral_data文件夹：\n{behavioral_data_path}\n错误：{str(create_error)}")
                    return
            
            # 检查是否有访问权限
            if not os.access(behavioral_data_path, os.R_OK):
                CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "访问权限不足", 
                                        f"没有权限访问文件夹：\n{behavioral_data_path}")
                return
            
            # 使用Windows资源管理器打开文件夹
            try:
                # 确保路径正确格式化
                behavioral_data_path = os.path.normpath(behavioral_data_path)
                print(f"正在打开文件夹：{behavioral_data_path}")
                
                # 不使用check=True，因为explorer经常返回非零退出码但仍能正常工作
                result = subprocess.run(["explorer", behavioral_data_path], timeout=10)
                print(f"已打开文件夹：{behavioral_data_path} (退出码: {result.returncode})")
                
            except subprocess.TimeoutExpired:
                print("打开文件夹超时，但可能已成功打开")
            except FileNotFoundError:
                CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "系统错误", 
                                        "无法找到Windows资源管理器程序。")
            except Exception as explorer_error:
                print(f"使用资源管理器打开文件夹时出错: {explorer_error}")
                CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "打开失败", 
                                        f"无法使用资源管理器打开文件夹：\n{str(explorer_error)}\n\n文件夹路径：{behavioral_data_path}")
            
        except Exception as e:
            print(f"打开文件夹时出错: {e}")
            import traceback
            traceback.print_exc()
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", 
                                    f"打开文件夹时发生错误：{str(e)}")



    def load_leaderboard_data(self):
        """加载排行榜数据"""
        try:
            print("开始加载排行榜数据...")
            # 获取所有用户的数据
            leaderboard_data = self.calculate_leaderboard_data()
            print(f"找到 {len(leaderboard_data)} 条数据")

            # 按准确度排序，取前三名
            sorted_data = sorted(leaderboard_data, key=lambda x: x['accuracy'], reverse=True)[:3]
            print(f"排序后取前 {len(sorted_data)} 名")

            # 更新UI显示
            self.update_leaderboard_ui(sorted_data)
            print("UI更新完成")

        except Exception as e:
            print(f"加载排行榜数据时出错: {e}")
            import traceback
            traceback.print_exc()
            # 显示默认数据
            self.show_default_leaderboard()

    def calculate_leaderboard_data(self):
        """计算排行榜数据"""
        leaderboard_data = []

        # 遍历所有实验数据文件夹
        data_folders = glob.glob("Behavioral_data/*/")

        for folder in data_folders:
            try:
                # 读取用户信息
                subject_info_file = os.path.join(folder, "subject_info.txt")
                if not os.path.exists(subject_info_file):
                    continue

                # 解析用户信息
                user_info = self.parse_subject_info(subject_info_file)

                # 计算个人阶段(subA)的数据
                suba_data_file = os.path.join(folder, "subA", "data", "数据.txt")
                if os.path.exists(suba_data_file):
                    stats = self.parse_experiment_data(suba_data_file)
                    if stats:
                        # 获取文件修改时间作为实验日期
                        import time
                        timestamp = os.path.getmtime(suba_data_file)
                        date_str = time.strftime("%Y-%m-%d", time.localtime(timestamp))

                        leaderboard_data.append({
                            'user_id': user_info['main_user_id'],
                            'accuracy': stats['avg_accuracy'],
                            'total_time': stats['total_time'],
                            'avg_deviation': stats['avg_deviation'],
                            'date': date_str
                        })

            except Exception as e:
                print(f"处理文件夹 {folder} 时出错: {e}")
                continue

        return leaderboard_data

    def parse_subject_info(self, file_path):
        """解析用户信息文件"""
        user_info = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取主受试者标识
            main_user_match = re.search(r'标识:\s*(\S+)', content)
            if main_user_match:
                user_info['main_user_id'] = main_user_match.group(1)
            else:
                user_info['main_user_id'] = "未知用户"

        except Exception as e:
            print(f"解析用户信息文件时出错: {e}")
            user_info['main_user_id'] = "未知用户"

        return user_info

    def parse_experiment_data(self, file_path):
        """解析实验数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if len(lines) < 16:
                return None

            # 解析前8行的准确度数据
            accuracies = []
            times = []

            for i in range(8):
                line = lines[i].strip()
                # 解析百分比
                accuracy_match = re.search(r'百分比：([\d.]+)%', line)
                if accuracy_match:
                    accuracies.append(float(accuracy_match.group(1)))

                # 解析绘图时长
                time_match = re.search(r'绘图时长：([\d.]+)', line)
                if time_match:
                    times.append(float(time_match.group(1)))

            # 解析后8行的偏差数据
            deviations = []
            for i in range(8, 16):
                line = lines[i].strip()
                deviation_match = re.search(r'偏差像素个数\s*:\s*(\d+)', line)
                if deviation_match:
                    deviations.append(int(deviation_match.group(1)))

            # 计算平均值
            avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
            total_time = sum(times) if times else 0
            avg_deviation = sum(deviations) / len(deviations) if deviations else 0

            return {
                'avg_accuracy': avg_accuracy,
                'total_time': total_time,
                'avg_deviation': avg_deviation
            }

        except Exception as e:
            print(f"解析实验数据文件时出错: {e}")
            return None

    def update_leaderboard_ui(self, sorted_data):
        """更新排行榜UI显示"""
        print(f"开始更新UI，数据: {sorted_data}")
        # 清空所有排行榜显示
        self.clear_leaderboard_display()

        # 更新前三名数据
        for i, data in enumerate(sorted_data):
            print(f"更新第{i + 1}名: {data}")
            if i == 0:  # 第一名
                self.ui.first_user_label.setText(f"{data['user_id']}")
                self.ui.first_accuracy_label.setText(f"{data['accuracy']:.2f}%")
                self.ui.first_time_label.setText(f"{data['total_time']:.1f}s")
                self.ui.first_deviation_label.setText(f"{data['avg_deviation']:.0f}")
                self.ui.first_date_label.setText(f"{data.get('date', '-')}")
                print(f"第一名UI更新完成")
            elif i == 1:  # 第二名
                self.ui.second_user_label.setText(f"{data['user_id']}")
                self.ui.second_accuracy_label.setText(f"{data['accuracy']:.2f}%")
                self.ui.second_time_label.setText(f"{data['total_time']:.1f}s")
                self.ui.second_deviation_label.setText(f"{data['avg_deviation']:.0f}")
                self.ui.second_date_label.setText(f"{data.get('date', '-')}")
                print(f"第二名UI更新完成")
            elif i == 2:  # 第三名
                self.ui.third_user_label.setText(f"{data['user_id']}")
                self.ui.third_accuracy_label.setText(f"{data['accuracy']:.2f}%")
                self.ui.third_time_label.setText(f"{data['total_time']:.1f}s")
                self.ui.third_deviation_label.setText(f"{data['avg_deviation']:.0f}")
                self.ui.third_date_label.setText(f"{data.get('date', '-')}")
                print(f"第三名UI更新完成")

    def clear_leaderboard_display(self):
        """清空排行榜显示"""
        # 第一名
        self.ui.first_user_label.setText("-")
        self.ui.first_accuracy_label.setText("-")
        self.ui.first_time_label.setText("-")
        self.ui.first_deviation_label.setText("-")
        self.ui.first_date_label.setText("-")

        # 第二名
        self.ui.second_user_label.setText("-")
        self.ui.second_accuracy_label.setText("-")
        self.ui.second_time_label.setText("-")
        self.ui.second_deviation_label.setText("-")
        self.ui.second_date_label.setText("-")

        # 第三名
        self.ui.third_user_label.setText("-")
        self.ui.third_accuracy_label.setText("-")
        self.ui.third_time_label.setText("-")
        self.ui.third_deviation_label.setText("-")
        self.ui.third_date_label.setText("-")

    def show_default_leaderboard(self):
        """显示默认排行榜信息"""
        self.clear_leaderboard_display()
        self.ui.first_user_label.setText("暂无数据")
        self.ui.second_user_label.setText("暂无数据")
        self.ui.third_user_label.setText("暂无数据")

    def stop_current_game(self):
        """停止当前运行的游戏线程"""
        if self.current_stop_event:
            self.current_stop_event.set()
        if self.current_game_thread and self.current_game_thread.is_alive():
            self.current_game_thread.join(timeout=3)
            if self.current_game_thread.is_alive():
                print("警告：游戏线程未能在3秒内停止")
        
        # 清除游戏运行状态
        self.is_game_running = False

    def cleanup_resources(self):
        """清理所有资源"""
        try:
            # 停止Caps Lock监控
            # 取消事件过滤器
            try:
                QApplication.instance().removeEventFilter(self)
            except:
                pass
                print("Caps Lock监控已停止")
            
            # 停止自动检测定时器
            # 关闭串口监控
            if hasattr(self, 'serial_timer') and self.serial_timer:
                self.serial_timer.stop()
                print("[串口监控] 优化监控已停止")
                
        except Exception as e:
            print(f"清理资源时出错: {e}")

    def start_game_thread(self, game_class):
        """安全启动游戏线程"""
        print(f"[游戏启动] 开始启动游戏线程，游戏类: {game_class}")

        # 先停止当前游戏
        print(f"[游戏启动] 停止当前游戏")
        self.stop_current_game()

        # 设置游戏运行状态
        self.is_game_running = True

        # 检查游戏类的构造函数是否支持stop_event参数
        import inspect
        sig = inspect.signature(game_class.__init__)
        print(f"[游戏启动] 游戏类构造函数签名: {sig}")

        if 'stop_event' in sig.parameters:
            # 支持stop_event参数的游戏类（如main.py中的Game类）
            print(f"[游戏启动] 游戏类支持stop_event参数")
            original_target = lambda: game_class(stop_event=None).run()
        else:
            # 不支持stop_event参数的游戏类（如测试文件中的Game类）
            print(f"[游戏启动] 游戏类不支持stop_event参数")
            original_target = lambda: game_class().run()

        # 包装target函数以在结束后清除游戏运行状态
        def wrapped_target():
            try:
                original_target()
            finally:
                # 游戏结束后清除运行状态
                self.is_game_running = False
                print(f"[游戏启动] 游戏结束，清除运行状态")

        print(f"[游戏启动] 目标函数准备完成")

        # 启动新游戏
        print(f"[游戏启动] 调用线程管理器启动线程")
        thread, stop_event = thread_manager.start_thread(
            target=wrapped_target,
            timeout=60
        )

        self.current_game_thread = thread
        self.current_stop_event = stop_event

        print(f"[游戏启动] 游戏线程启动完成: {thread.name}")
        return thread, stop_event


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = Interfacewindow()
    main_window.show()
    sys.exit(app.exec_())