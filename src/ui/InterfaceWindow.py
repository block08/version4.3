#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import threading
import time
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
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton)

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


# 为了让此文件独立运行，我们在此处进行前向声明。
# 在您的实际项目中，这个类应该从定义它的文件中导入。
class LoginWindow(QMainWindow):
    pass


class CustomDialog(QDialog):
    """
    完全自定义的对话框，用于替代QMessageBox，以实现更好的布局控制和样式。
    """

    def __init__(self, parent, icon_type, title, text, font_size=22, width=600, height=300, button_type='ok'):
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

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        icon_label = QLabel(self)
        icon_pixmap = self.style().standardIcon(icon_type).pixmap(64, 64)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(64, 64)
        icon_label.setStyleSheet("border: none;")
        content_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)

        text_label = QLabel(text, self)
        text_label.setFont(QFont("Microsoft YaHei", font_size))
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignVCenter)
        text_label.setStyleSheet("border: none; color: black;")
        content_layout.addWidget(text_label, 1)

        main_layout.addLayout(content_layout)
        main_layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if button_type == 'yes_no':
            yes_button = QPushButton("是", self)
            yes_button.setCursor(QCursor(Qt.PointingHandCursor))
            yes_button.setFixedSize(140, 50)
            yes_button.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
            yes_button.setStyleSheet("""
                QPushButton { background-color: #2ecc71; color: white; border: none; border-radius: 25px; }
                QPushButton:hover { background-color: #27ae60; }
                QPushButton:pressed { background-color: #1e8449; }
            """)
            yes_button.clicked.connect(self.accept)
            button_layout.addWidget(yes_button)

            no_button = QPushButton("否", self)
            no_button.setCursor(QCursor(Qt.PointingHandCursor))
            no_button.setFixedSize(140, 50)
            no_button.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
            no_button.setStyleSheet("""
                QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 25px; }
                QPushButton:hover { background-color: #c0392b; }
                QPushButton:pressed { background-color: #a93226; }
            """)
            no_button.clicked.connect(self.reject)
            button_layout.addWidget(no_button)
        else:  # 默认为 'ok'
            ok_button = QPushButton("确定", self)
            ok_button.setCursor(QCursor(Qt.PointingHandCursor))
            ok_button.setFixedSize(140, 50)
            ok_button.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
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

    def showEvent(self, event):
        """重写 showEvent 以在显示时调整窗口位置到父窗口正中心偏上。"""
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().geometry()
            parent_center = parent_rect.center()
            x = parent_center.x() - self.width() // 2 + 180
            y = parent_center.y() - self.height() // 2 - 100  # 向上偏移50像素
            self.move(x, y)

    @staticmethod
    def show_message(parent, icon_type, title, text, font_size=22):
        dialog = CustomDialog(parent, icon_type, title, text, font_size, button_type='ok')
        return dialog.exec_()

    @staticmethod
    def ask_question(parent, icon_type, title, text, font_size=22):
        dialog = CustomDialog(parent, icon_type, title, text, font_size, button_type='yes_no')
        return dialog.exec_()


class Interfacewindow(QMainWindow):
    """
    应用程序的主窗口类。
    """

    def __init__(self):
        super().__init__()
        self.ui = InterfaceUI.Ui_MainWindow()
        self.ui.setupUi(self)

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

        # 串口监控相关变量
        self.current_connected_port = None
        self.available_ports = []
        self.last_port_check_time = 0
        self.port_check_interval = 1.0  # 检查间隔（秒）

        # 设置定时器进行实时串口监控
        self.serial_monitor_timer = QTimer()
        self.serial_monitor_timer.timeout.connect(self.check_serial_status)
        self.serial_monitor_timer.start(1000)  # 每秒检查一次

        # 初始化串口状态
        self.initialize_serial_status()
        
        # 延迟创建测试按钮，确保UI完全加载
        QTimer.singleShot(100, self.add_test_send_button)

    def init_navigation_system(self):
        """初始化导航按钮状态管理系统"""
        # 定义页面索引到按钮的映射关系
        self.nav_buttons = {
            0: self.ui.pushButton_exercise,  # page_home 对应 练习按钮
            1: self.ui.pushButton_exercise,  # page_exercise 对应 练习按钮
            2: self.ui.pushButton_main,  # page_main 对应 正式实验按钮
            3: self.ui.pushButton_highestscore,  # page_highestscore 对应 最高纪录按钮
            4: self.ui.pushButton_data,  # page_data 对应 数据查看按钮
            5: self.ui.pushButton_setting  # page_serial 对应 串口设置按钮
        }

        # 定义按钮的正常状态样式
        self.normal_button_style = """
            QPushButton{
                border:none;
                color: rgb(255, 255, 255);
                font: 50pt "微软雅黑";
            }
            QPushButton:hover{
                color: rgb(17, 48, 53);
            }
            QPushButton:pressed{
                padding-left:5px;
                padding-top:5px;
            }
        """

        # 定义按钮的激活状态样式
        self.active_button_style = """
            QPushButton{
                border:none;
                color: rgb(17, 48, 53);
                font: 50pt "微软雅黑";
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
            }
            QPushButton:hover{
                color: rgb(17, 48, 53);
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed{
                padding-left:5px;
                padding-top:5px;
                background-color: rgba(255, 255, 255, 0.1);
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

    def add_test_send_button(self):
        """动态添加测试发送指令按钮"""
        try:
            from PyQt5.QtWidgets import QPushButton
            from PyQt5.QtGui import QFont
            from PyQt5.QtCore import Qt
            

            # 检查是否已经创建过按钮 - 如果已存在则删除重建
            if hasattr(self, 'test_send_button') and self.test_send_button is not None:
                print("删除已存在的按钮，重新创建")
                self.test_send_button.deleteLater()
                self.test_send_button = None
            
            # 创建测试发送指令按钮 - 确认按钮在(930, 640, 161, 71)，测试按钮放在左边
            self.test_send_button = QPushButton(self.ui.page_serial)
            self.test_send_button.setGeometry(480, 640, 440, 71)  # 向左延长，增加宽度以完全显示文字
            
            # 设置字体 - 与确认按钮保持一致
            font = QFont()
            font.setFamily("微软雅黑")
            font.setPointSize(50)  # 与确认按钮字体大小一致
            font.setBold(False)
            font.setItalic(False)
            font.setWeight(50)
            self.test_send_button.setFont(font)
            
            # 设置样式 - 与确认按钮保持一致的颜色
            self.test_send_button.setStyleSheet("""
                QPushButton{
                    background-color: rgb(34, 92, 102);
                    border:none;
                    color: rgb(255, 255, 255);
                    font: 50pt "微软雅黑";
                }
                QPushButton:hover{
                    color: rgb(17, 48, 53);
                }
                QPushButton:pressed{
                    padding-left:5px;
                    padding-top:5px;
                }
            """)
            
            # 设置按钮文本
            self.test_send_button.setText("测试发送指令")
            
            # 连接信号
            self.test_send_button.clicked.connect(self.test_send_command)
            
            # 设置按钮可见并提升到前台
            self.test_send_button.setVisible(True)
            self.test_send_button.raise_()
            self.test_send_button.show()
            

            
        except Exception as e:
            print(f"创建测试按钮时出错: {e}")
            import traceback
            traceback.print_exc()

    def initialize_serial_status(self):
        """初始化串口状态显示"""
        # 首次检查串口状态
        self.update_available_ports()
        self.check_serial_status()

    def find_ch340_port(self):
        """查找USB-SERIAL CH340设备"""
        try:
            ch340_port = None
            ports = serial.tools.list_ports.comports()

            for port in ports:
                # 检查设备描述中是否包含CH340相关信息
                port_description = port.description.upper()
                if any(keyword in port_description for keyword in ['CH340', 'USB-SERIAL', 'USB SERIAL']):
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

    def update_available_ports(self):
        """更新可用串口列表，显示所有COM口但排除蓝牙"""
        current_time = time.time()
        # 每隔一定时间才重新扫描端口，避免频繁扫描
        if current_time - self.last_port_check_time > self.port_check_interval:
            try:
                # 获取所有非蓝牙COM口
                all_com_ports = self.get_all_com_ports()

                # 如果端口列表有变化，更新下拉框
                if all_com_ports != self.available_ports:
                    self.available_ports = all_com_ports
                    self.update_port_combobox()

                self.last_port_check_time = current_time
            except Exception as e:
                print(f"扫描端口时出错: {e}")

    def update_port_combobox(self):
        """更新端口下拉框选项，显示所有COM口"""
        try:
            current_selection = self.ui.comboBox_com.currentText()
            self.ui.comboBox_com.clear()

            if self.available_ports:
                # 按端口号排序显示
                sorted_ports = sorted(self.available_ports, key=lambda x: int(''.join(filter(str.isdigit, x))) if any(
                    c.isdigit() for c in x) else 999)

                for port in sorted_ports:
                    self.ui.comboBox_com.addItem(port)

                # 尝试保持之前的选择
                if current_selection in self.available_ports:
                    index = self.ui.comboBox_com.findText(current_selection)
                    if index >= 0:
                        self.ui.comboBox_com.setCurrentIndex(index)
            else:
                # 如果没有可用端口，添加默认选项
                for i in range(1, 7):
                    self.ui.comboBox_com.addItem(f"COM{i}")

        except Exception as e:
            print(f"更新端口下拉框时出错: {e}")

    def check_serial_status(self):
        """只监控CH340设备连接状态，但不影响用户的端口选择"""
        try:
            # 更新可用端口列表（显示所有非蓝牙COM口）
            self.update_available_ports()

            # 专门查找并检查CH340设备状态
            ch340_port = self.find_ch340_port()
            ch340_connected = False

            if ch340_port:
                # 检查CH340设备是否可以连接
                if check_serial_connection(ch340_port):
                    ch340_connected = True
                    print(f"CH340设备连接正常: {ch340_port}")
                else:
                    print(f"CH340设备连接失败: {ch340_port}")
            else:
                print("未找到CH340设备")

            # 更新CH340连接状态显示（不影响用户当前选择的端口）
            if ch340_connected != (self.current_connected_port is not None):
                self.current_connected_port = ch340_port if ch340_connected else None
                self.update_connection_ui(ch340_connected, ch340_port)

        except Exception as e:
            print(f"检查端口状态时出错: {e}")
            self.update_connection_ui(False, None)

    def update_connection_ui(self, ch340_connected, ch340_port):
        """更新CH340连接状态的UI显示"""
        try:
            if ch340_connected and ch340_port:
                # CH340设备连接成功 - 绿灯
                self.ui.label_connection_status.setStyleSheet("""
                    QLabel {
                        border: 3px solid rgb(46, 204, 113);
                        border-radius: 100px;
                        background-color: rgb(46, 204, 113);
                    }
                """)
                self.ui.label_status_text.setText(f"端口已连接")
                self.ui.label_status_text.setStyleSheet("""
                    QLabel {
                        border: none;
                        color: rgb(46, 204, 113);
                        font: 30pt "微软雅黑";
                    }
                """)

            elif ch340_port and not ch340_connected:
                # 找到CH340设备但连接失败 - 黄灯
                self.ui.label_connection_status.setStyleSheet("""
                    QLabel {
                        border: 3px solid rgb(255, 193, 7);
                        border-radius: 100px;
                        background-color: rgb(255, 193, 7);
                    }
                """)
                self.ui.label_status_text.setText("端口检测到")
                self.ui.label_status_text.setStyleSheet("""
                    QLabel {
                        border: none;
                        color: rgb(255, 193, 7);
                        font: 30pt "微软雅黑";
                    }
                """)

            else:
                # 未找到CH340设备 - 红灯
                self.ui.label_connection_status.setStyleSheet("""
                    QLabel {
                        border: 3px solid rgb(231, 76, 60);
                        border-radius: 100px;
                        background-color: rgb(231, 76, 60);
                    }
                """)
                self.ui.label_status_text.setText("未找到端口")
                self.ui.label_status_text.setStyleSheet("""
                    QLabel {
                        border: none;
                        color: rgb(231, 76, 60);
                        font: 30pt "微软雅黑";
                    }
                """)

        except Exception as e:
            print(f"更新连接UI时出错: {e}")

    def showEvent(self, event):
        """重写 showEvent，在窗口显示时更新用户信息。"""
        super().showEvent(event)
        self.update_user_button_text()
        # 确保测试按钮被创建
        if not hasattr(self, 'test_send_button'):
            self.add_test_send_button()

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
            if user1:
                self.ui.pushButton_4.setText(f"{user1}绘图练习模块")
            else:
                self.ui.pushButton_4.setText("人员①绘图练习模块")
                
            if user2:
                self.ui.pushButton_5.setText(f"{user2}绘图练习模块")
            else:
                self.ui.pushButton_5.setText("人员绘图练习模块")
                
            if user3:
                self.ui.pushButton_6.setText(f"{user3}绘图练习模块")
            else:
                self.ui.pushButton_6.setText("人员③绘图练习模块")
                
            if user1 and user2:
                self.ui.pushButton_9.setText(f"{user1}和{user2}绘图练习模块")
            else:
                self.ui.pushButton_9.setText("人员①&人员②绘图练习模块")
                
            if user1 and user3:
                self.ui.pushButton_10.setText(f"{user1}和{user3}绘图练习模块")
            else:
                self.ui.pushButton_10.setText("人员①&人员③绘图练习模块")
        except Exception as e:
            print(f"更新练习按钮文本时出错: {e}")

    def setup_connections(self):
        """设置所有UI控件的信号和槽连接。"""
        self.ui.pushButton_exercise.clicked.connect(self.go_exercise)
        self.ui.pushButton_main.clicked.connect(self.go_main_test)
        self.ui.pushButton_highestscore.clicked.connect(self.go_highestscore)
        self.ui.pushButton_data.clicked.connect(self.go_data)
        self.ui.pushButton_setting.clicked.connect(self.go_setting)
        self.ui.run_main_test.clicked.connect(self.go_main)
        self.ui.pushButton_quereng.clicked.connect(self.confirm_settings)
        self.ui.pushButton_relogin.clicked.connect(self.relogin)
        self.ui.data_check.clicked.connect(self.open_data_folder)
        self.ui.pushButton_4.clicked.connect(self.start_practice_1)
        self.ui.pushButton_5.clicked.connect(self.start_practice_2)
        self.ui.pushButton_6.clicked.connect(self.start_practice_3)
        self.ui.pushButton_9.clicked.connect(self.start_practice_4)
        self.ui.pushButton_10.clicked.connect(self.start_practice_5)

    def start_practice_1(self):
        """启动1的练习模块。"""
        try:
            user1_mark = getattr(shared_data, 'user1_mark', '01')
            
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
            
            print(f"正在启动{user1}绘图练习模块...")
            game_function = Atest.Game
            if game_function:
                threading.Thread(target=lambda: game_function().run(), daemon=True).start()
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_2(self):
        """启动人员2的练习模块。"""
        try:
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
            
            user2 = extract_number(user2_mark)
            
            print(f"正在启动{user2}绘图练习模块...")
            game_function = Btest.Game
            if game_function:
                threading.Thread(target=lambda: game_function().run(), daemon=True).start()
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
                threading.Thread(target=lambda: game_function().run(), daemon=True).start()
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_4(self):
        """启动人员①&人员②的练习模块。"""
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
                threading.Thread(target=lambda: game_function().run(), daemon=True).start()
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def start_practice_5(self):
        """启动人员①&人员③的练习模块。"""
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
                threading.Thread(target=lambda: game_function().run(), daemon=True).start()
        except Exception as e:
            print(f"启动练习模块时出错: {e}")

    def go_main(self):
        """开始主实验/游戏。"""
        game_function = None
        if shared_data.global_flag is None:
            reply = CustomDialog.ask_question(self, QStyle.SP_MessageBoxQuestion, "运行模式",
                                              "未检测到端口连接。\n\n您想在仿真模式下运行（仅记录行为数据）吗？")
            if reply == QDialog.Accepted:
                game_function = main_simulation.Game
            else:
                return
        else:
            game_function = main.Game

        if game_function:
            threading.Thread(target=lambda: game_function().run(), daemon=True).start()

    def confirm_settings(self):
        """手动确认端口设置，共享数据使用用户选择的端口"""
        port = self.ui.comboBox_com.currentText()

        # 检查用户选择的端口是否可连接
        if check_serial_connection(port):
            baudrate = self.ui.comboBox_bote.currentText()
            # 共享数据使用用户选择的端口，不一定是CH340
            shared_data.global_flag = 1
            shared_data.global_port = port
            shared_data.global_baudrate = int(baudrate)

            # 检查是否为CH340设备
            ch340_port = self.find_ch340_port()
            is_ch340_device = (port == ch340_port)
            device_type = "CH340设备" if is_ch340_device else "端口设备"

            CustomDialog.show_message(self, QStyle.SP_MessageBoxInformation, "成功",
                                      f"{device_type} {port} 已成功连接并设置！\n注意：状态灯仅显示CH340设备状态")
        else:
            # 清除共享数据
            shared_data.global_flag = None
            shared_data.global_port = None
            shared_data.global_baudrate = None

            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "连接失败",
                                      f"无法连接到端口 {port}。\n请检查设备是否正确连接或端口是否被占用。")

    def test_send_command(self):
        """测试发送指令按钮的处理函数，发送数字8"""
        try:
            # 检查是否有端口设置
            if shared_data.global_flag is None or shared_data.global_port is None:
                CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "未设置端口",
                                          "请先确认端口设置后再进行测试！")
                return
            
            # 初始化端口
            if initialize_serial():
                try:
                    # 发送数字8的指令
                    test_data = bytes([8])
                    serial_marker(test_data)
                    CustomDialog.show_message(self, QStyle.SP_MessageBoxInformation, "测试成功",
                                              f"已成功向端口 {shared_data.global_port} 发送测试指令：8")
                finally:
                    # 测试完成后关闭串口，释放资源
                    close_serial()
            else:
                CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "端口初始化失败",
                                          f"无法初始化端口 {shared_data.global_port}，请检查端口设置。")
        except Exception as e:
            # 出现异常时也要确保关闭串口
            close_serial()
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "测试失败",
                                      f"发送测试指令时出错：{str(e)}")

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
            # 停止端口监控定时器
            if hasattr(self, 'serial_monitor_timer'):
                self.serial_monitor_timer.stop()

            try:
                from src.ui.LoginWindow import LoginWindow
                self.login_window_instance = LoginWindow()
                self.login_window_instance.show()
                # 设置标志，表示这是重新登录而不是正常退出
                self.is_relogin = True
                self.close()
            except ImportError:
                QMessageBox.critical(self, "导入错误", "无法从 'login.py' 导入 LoginWindow 类。")

    def closeEvent(self, event):
        """重写关闭事件，确保定时器被停止"""
        # 检查是否是重新登录操作
        if hasattr(self, 'is_relogin') and self.is_relogin:
            # 如果是重新登录，直接关闭窗口，不显示退出确认
            if hasattr(self, 'serial_monitor_timer'):
                self.serial_monitor_timer.stop()
            print("重新登录，关闭当前界面。")
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
            # 如果用户点击“是”，则停止定时器并接受关闭事件，关闭窗口
            if hasattr(self, 'serial_monitor_timer'):
                self.serial_monitor_timer.stop()
            print("程序已退出。")
            event.accept()
        else:
            # 如果用户点击“否”，则忽略该事件，窗口不会关闭
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
        # 确保测试按钮在端口设置页面被创建
        if not hasattr(self, 'test_send_button'):
            QTimer.singleShot(50, self.add_test_send_button)

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
                        leaderboard_data.append({
                            'user_id': user_info['main_user_id'],
                            'accuracy': stats['avg_accuracy'],
                            'total_time': stats['total_time'],
                            'avg_deviation': stats['avg_deviation']
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
            print(f"更新第{i+1}名: {data}")
            if i == 0:  # 第一名
                self.ui.first_user_label.setText(f"用户: {data['user_id']}")
                self.ui.first_accuracy_label.setText(f"准确度: {data['accuracy']:.2f}%")
                self.ui.first_time_label.setText(f"用时: {data['total_time']:.2f}s")
                self.ui.first_deviation_label.setText(f"偏差: {data['avg_deviation']:.0f}")
                print(f"第一名UI更新完成")
            elif i == 1:  # 第二名
                self.ui.second_user_label.setText(f"用户: {data['user_id']}")
                self.ui.second_accuracy_label.setText(f"准确度: {data['accuracy']:.2f}%")
                self.ui.second_time_label.setText(f"用时: {data['total_time']:.2f}s")
                self.ui.second_deviation_label.setText(f"偏差: {data['avg_deviation']:.0f}")
                print(f"第二名UI更新完成")
            elif i == 2:  # 第三名
                self.ui.third_user_label.setText(f"用户: {data['user_id']}")
                self.ui.third_accuracy_label.setText(f"准确度: {data['accuracy']:.2f}%")
                self.ui.third_time_label.setText(f"用时: {data['total_time']:.2f}s")
                self.ui.third_deviation_label.setText(f"偏差: {data['avg_deviation']:.0f}")
                print(f"第三名UI更新完成")

    def clear_leaderboard_display(self):
        """清空排行榜显示"""
        # 第一名
        self.ui.first_user_label.setText("用户: -")
        self.ui.first_accuracy_label.setText("准确度: -")
        self.ui.first_time_label.setText("用时: -")
        self.ui.first_deviation_label.setText("偏差: -")
        
        # 第二名
        self.ui.second_user_label.setText("用户: -")
        self.ui.second_accuracy_label.setText("准确度: -")
        self.ui.second_time_label.setText("用时: -")
        self.ui.second_deviation_label.setText("偏差: -")
        
        # 第三名
        self.ui.third_user_label.setText("用户: -")
        self.ui.third_accuracy_label.setText("准确度: -")
        self.ui.third_time_label.setText("用时: -")
        self.ui.third_deviation_label.setText("偏差: -")

    def show_default_leaderboard(self):
        """显示默认排行榜信息"""
        self.clear_leaderboard_display()
        self.ui.first_user_label.setText("暂无数据")
        self.ui.second_user_label.setText("暂无数据")
        self.ui.third_user_label.setText("暂无数据")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = Interfacewindow()
    main_window.show()
    sys.exit(app.exec_())