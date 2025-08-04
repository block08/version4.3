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
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
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
        text_label.setStyleSheet("border: none; color: black; padding: 10px;")
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
            yes_button = QPushButton("是", self)
            yes_button.setCursor(QCursor(Qt.PointingHandCursor))
            yes_button.setFixedSize(220, 65)
            yes_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            yes_button.setStyleSheet("""
                QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                QPushButton:hover { background-color: #f0f0f0; border: 2px solid #999999; }
                QPushButton:pressed { background-color: #e0e0e0; }
            """)
            yes_button.clicked.connect(self.accept)
            
            yes_hint = QLabel("按Y键", self)
            yes_hint.setAlignment(Qt.AlignCenter)
            yes_hint.setFont(QFont("Microsoft YaHei", 25))
            yes_hint.setStyleSheet("color: #888888; border: none;")
            
            yes_container.addWidget(yes_button)
            yes_container.addWidget(yes_hint)
            yes_container.setSpacing(5)
            
            yes_widget = QWidget()
            yes_widget.setLayout(yes_container)
            button_layout.addWidget(yes_widget)

            # 创建"否"按钮和其容器
            no_container = QVBoxLayout()
            no_button = QPushButton("否", self)
            no_button.setCursor(QCursor(Qt.PointingHandCursor))
            no_button.setFixedSize(220, 65)
            no_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            no_button.setStyleSheet("""
                QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                QPushButton:hover { background-color: #f0f0f0; border: 2px solid #999999; }
                QPushButton:pressed { background-color: #e0e0e0; }
            """)
            no_button.clicked.connect(self.reject)
            
            no_hint = QLabel("按N键", self)
            no_hint.setAlignment(Qt.AlignCenter)
            no_hint.setFont(QFont("Microsoft YaHei", 25))
            no_hint.setStyleSheet("color: #888888; border: none;")
            
            no_container.addWidget(no_button)
            no_container.addWidget(no_hint)
            no_container.setSpacing(5)
            
            no_widget = QWidget()
            no_widget.setLayout(no_container)
            button_layout.addWidget(no_widget)
        else:  # 默认为 'ok'
            ok_button = QPushButton("确定", self)
            ok_button.setCursor(QCursor(Qt.PointingHandCursor))
            ok_button.setFixedSize(220, 65)
            ok_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            ok_button.setStyleSheet("""
                QPushButton { background-color: #3498db; color: white; border: none; border-radius: 25px; }
                QPushButton:hover { background-color: #2980b9; }
                QPushButton:pressed { background-color: #2471a3; }
            """)
            ok_button.clicked.connect(self.accept)
            button_layout.addWidget(ok_button)

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

        # 用于自定义窗口拖动
        self.m_flag = False
        self.m_Position = None

        # 用于在重新登录时创建新的登录窗口实例
        self.login_window_instance = None

        # 重新登录标志，用于区分重新登录和正常退出
        self.is_relogin = False

        # 串口检测相关变量
        self.current_detected_port = None

        # 初始化串口状态显示
        self.initialize_serial_ui()

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
                background-color: rgb(210, 225, 255);
                padding-left:3px;
                padding-top:3px;
            }
        """

        # 定义按钮的激活状态样式 - 类似微信的深灰色
        self.active_button_style = """
            QPushButton{
                background-color: rgb(79, 79, 79);
                border: 2px solid rgb(79, 79, 79);
                color: rgb(255, 255, 255);
                font: 50pt "微软雅黑";
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover{
                background-color: rgb(95, 95, 95);
                border: 2px solid rgb(95, 95, 95);
                color: rgb(255, 255, 255);
            }
            QPushButton:pressed{
                background-color: rgb(65, 65, 65);
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

    def open_data_folder_with_state(self):
        """打开数据文件夹"""
        # 直接执行功能，不更新按钮状态（因为不切换页面）
        self.open_data_folder()

    def initialize_serial_ui(self):
        """初始化串口UI状态"""
        # 设置初始状态
        self.ui.label_current_port.setText("未检测")
        self.ui.label_status_text.setText("端口未连接")
        
        # 动态创建COM状态标签
        self.create_com_status_label()

        # 启动自动检测定时器
        self.auto_detect_timer = QTimer()
        self.auto_detect_timer.timeout.connect(self.auto_detect_and_connect)
        self.auto_detect_timer.start(2000)  # 每2秒检测一次

    def create_com_status_label(self):
        """动态创建COM状态标签"""
        try:
            # 创建COM状态标签
            self.label_com_status = QLabel("COM未连接")
            self.label_com_status.setMinimumSize(200, 50)
            self.label_com_status.setFont(QFont("微软雅黑", 36, QFont.Bold))
            self.label_com_status.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(0, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)
            self.label_com_status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
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
                    # 在重新登录按钮前插入COM状态标签
                    parent_layout.insertWidget(button_index, self.label_com_status)
                    print("COM状态标签已成功添加到界面")
                else:
                    print("未找到重新登录按钮的位置")
            else:
                print("未找到重新登录按钮的父布局")
                
        except Exception as e:
            print(f"创建COM状态标签时出错: {e}")

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
                user_text = f"| 被测航天员:{user1} | 辅助航天员:{user2} 和 {user3} "
                self.ui.pushButton.setText(user_text)
            else:
                self.ui.pushButton.setText("用户")

            # 更新练习按钮文本
            self.update_practice_button_texts(user1, user2, user3)
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

    def setup_connections(self):
        """设置所有UI控件的信号和槽连接。"""
        self.ui.pushButton_exercise.clicked.connect(self.go_exercise)
        self.ui.pushButton_main.clicked.connect(self.go_main_with_state)
        self.ui.pushButton_highestscore.clicked.connect(self.go_highestscore)
        self.ui.pushButton_data.clicked.connect(self.open_data_folder_with_state)
        # self.ui.pushButton_setting.clicked.connect(self.go_setting)  # 端口设置按钮已注释
        self.ui.run_main_test.clicked.connect(self.go_main)
        self.ui.pushButton_auto_connect.clicked.connect(self.manual_connect_port)
        self.ui.pushButton_relogin.clicked.connect(self.relogin)
        self.ui.data_check.clicked.connect(self.open_data_folder)
        self.ui.pushButton_4.clicked.connect(self.start_practice_1)
        self.ui.pushButton_9.clicked.connect(self.start_practice_4)

        # 连接宏观指导语按钮
        self.ui.pushButton_macro_guidance.clicked.connect(self.go_home)

    def start_practice_1(self):
        """启动1的练习模块。"""
        print(f"[练习启动] 开始启动练习模块1")
        
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
        if hasattr(self, 'label_com_status'):
            self.label_com_status.setText(f"{port}已连接")
            self.label_com_status.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(0, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)

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
        if hasattr(self, 'label_com_status'):
            self.label_com_status.setText("COM未连接")
            self.label_com_status.setStyleSheet("""
                QLabel{
                    border: none;
                    color: rgb(0, 0, 0);
                    font: bold 36pt "微软雅黑";
                    padding-right: 10px;
                }
            """)

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
            # 如果用户点击"是"，则直接退出，跳过closeEvent的确认
            print("程序已退出。")
            # 清理资源
            self.stop_current_game()
            thread_manager.stop_all_threads()
            # 标记为确认关闭，避免重复弹窗
            self.confirmed_close = True
            self.close()

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
            # 如果用户点击"是"，则接受关闭事件，关闭窗口
            print("程序已退出。")
            # 清理资源
            self.stop_current_game()
            thread_manager.stop_all_threads()
            event.accept()
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.isMaximized():
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if self.m_flag and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.m_Position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def open_data_folder(self):
        """
        检查并打开根目录下的 Behavioral_data 文件夹。
        如果文件夹不存在，则提示用户创建。
        """
        try:
            # 构建 'Behavioral_data' 文件夹的绝对路径
            data_path = os.path.abspath('Behavioral_data')

            # 检查文件夹是否存在
            if os.path.isdir(data_path):
                # 根据不同操作系统执行不同的命令来打开文件夹
                if sys.platform == 'win32':
                    os.startfile(data_path)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.call(['open', data_path])
                else:  # Linux
                    subprocess.call(['xdg-open', data_path])
            else:
                # 如果文件夹不存在，询问用户是否创建
                reply = CustomDialog.ask_question(
                    self,
                    QStyle.SP_MessageBoxQuestion,
                    "文件夹不存在",
                    f"数据文件夹 'Behavioral_data' 尚未创建。\n您想现在创建它吗？"
                )
                if reply == QDialog.Accepted:
                    try:
                        os.makedirs(data_path)
                        CustomDialog.show_message(
                            self,
                            QStyle.SP_MessageBoxInformation,
                            "创建成功",
                            f"文件夹 '{data_path}' 已成功创建。"
                        )
                        # 创建后再次尝试打开
                        self.open_data_folder()
                    except OSError as e:
                        CustomDialog.show_message(
                            self,
                            QStyle.SP_MessageBoxCritical,
                            "创建失败",
                            f"无法创建文件夹：\n{e}"
                        )
        except Exception as e:
            # 捕获其他未知错误
            CustomDialog.show_message(
                self,
                QStyle.SP_MessageBoxCritical,
                "操作失败",
                f"打开数据文件夹时发生错误：\n{e}"
            )

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