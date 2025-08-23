#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import sys
import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QFont, QPixmap, QCursor, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QLabel, QFrame, QGridLayout, QDialog, QStyle)
import sqlite3
import time
from src.utils import shared_data
from src.data.export_txt import export_to_txt
from src.ui.InterfaceWindow import Interfacewindow
from src.data.login_info_handler import LoginInfoHandler, create_experiment_structure
from src.ui import InterfaceUI  # 确保导入了主窗口UI

class CustomDialog(QDialog):
    """
    完全自定义的对话框，用于替代QMessageBox，以实现更好的布局控制和样式。
    """

    def __init__(self, parent, icon_type, title, text, font_size=22, width=750, height=400, button_type='ok'):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, width, height)
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 20px;
                border: 2px solid #555;
            }}
        """)

        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        main_layout.addStretch(1)

        # 简化布局 - 不再需要复杂的网格布局
        # 文字标签
        text_label = QLabel(text, self)
        text_label.setFont(QFont("Microsoft YaHei", int(font_size * 1.8)))
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        text_label.setStyleSheet("border: none; color: black; padding: 5px;")
        text_label.setMinimumWidth(600)
        text_label.setMinimumHeight(100)
        
        main_layout.addWidget(text_label)
        main_layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if button_type == 'yes_no':
            # 创建"是"按钮和其容器
            yes_container = QVBoxLayout()
            yes_button = QPushButton("确定", self)
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
        else:
            # 创建"确定"按钮和其容器，风格与yes_no一致
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
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().geometry()
            parent_center = parent_rect.center()
            x = parent_center.x() - self.width() // 2
            y = parent_center.y() - self.height() // 2
            self.move(x, y)

    @staticmethod
    def show_message(parent, icon_type, title, text, font_size=22):
        dialog = CustomDialog(parent, icon_type, title, text, font_size, button_type='ok')
        return dialog.exec_()

    @staticmethod
    def ask_question(parent, icon_type, title, text, font_size=22):
        dialog = CustomDialog(parent, icon_type, title, text, font_size, button_type='yes_no')
        return dialog.exec_()

    @staticmethod
    def show_login_success1(parent, title, text, font_size=28, callback=None, single_button=False):
        """显示登录成功确认对话框"""
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(900, 600)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setAttribute(Qt.WA_TranslucentBackground)

        main_frame = QFrame(dialog)
        main_frame.setGeometry(0, 0, 900, 600)
        main_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: 2px solid #555;
            }
        """)

        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        main_layout.addStretch(1)

        # 分离标题和详细信息
        lines = text.split('\n')
        if lines and "登录成功" in lines[0]:
            # 标题标签 - 物理向右移动
            title_label = QLabel("登录成功！")
            title_label.setFont(QFont("Microsoft YaHei", int(font_size * 1.8), QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("border: none; color: black; padding: 10px 10px 10px 50px;")  # 左边多加40px
            title_label.setMinimumHeight(60)
            main_layout.addWidget(title_label)
            
            # 详细信息标签 - 物理向右移动的两端对齐
            details_lines = [line for line in lines[1:] if line.strip()]  # 跳过空行
            if details_lines:
                details_text = '\n'.join(details_lines)
                details_label = QLabel(details_text)
                details_label.setFont(QFont("Microsoft YaHei", int(font_size * 1.4)))
                details_label.setWordWrap(True)
                details_label.setAlignment(Qt.AlignJustify)  # 两端对齐
                details_label.setStyleSheet("border: none; color: black; padding: 20px 20px 20px 180px;")  # 左边再多加20px
                details_label.setMinimumHeight(120)
                main_layout.addWidget(details_label)
        else:
            # 普通文本 - 居中显示
            text_label = QLabel(text)
            text_label.setFont(QFont("Microsoft YaHei", int(font_size * 1.6)))
            text_label.setWordWrap(True)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("border: none; color: black; padding: 10px;")
            text_label.setMinimumWidth(800)
            text_label.setMinimumHeight(180)
            main_layout.addWidget(text_label)
        main_layout.addStretch(1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 创建"进入主界面"按钮和其容器
        enter_container = QVBoxLayout()
        enter_button = QPushButton("确定")
        enter_button.setCursor(QCursor(Qt.PointingHandCursor))
        enter_button.setFixedSize(220, 65)
        enter_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
        enter_button.setStyleSheet("""
                QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                QPushButton:hover { background-color: #1f4788; color: white; border: 2px solid #1f4788; }
                QPushButton:pressed { background-color: #1f4788; color: white; }
        """)
        enter_button.clicked.connect(dialog.accept)
        
        enter_hint = QLabel("按Y键")
        enter_hint.setAlignment(Qt.AlignCenter)
        enter_hint.setFont(QFont("Microsoft YaHei", 25))
        enter_hint.setStyleSheet("color: #000000; border: none;")
        
        enter_container.addWidget(enter_button)
        enter_container.addWidget(enter_hint)
        enter_container.setSpacing(5)
        
        enter_widget = QWidget()
        enter_widget.setLayout(enter_container)
        button_layout.addWidget(enter_widget)

        # 只有不是单按钮模式时才创建取消按钮
        if not single_button:
            # 创建"取消"按钮和其容器
            cancel_container = QVBoxLayout()
            cancel_button = QPushButton("取消")
            cancel_button.setCursor(QCursor(Qt.PointingHandCursor))
            cancel_button.setFixedSize(220, 65)
            cancel_button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            cancel_button.setStyleSheet("""
                    QPushButton { background-color: white; color: black; border: 2px solid #cccccc; border-radius: 25px; }
                    QPushButton:hover { background-color: #1f4788; color: white; border: 2px solid #1f4788; }
                    QPushButton:pressed { background-color: #1f4788; color: white; }
            """)
            cancel_button.clicked.connect(dialog.reject)
            
            cancel_hint = QLabel("按N键")
            cancel_hint.setAlignment(Qt.AlignCenter)
            cancel_hint.setFont(QFont("Microsoft YaHei", 25))
            cancel_hint.setStyleSheet("color: #000000; border: none;")
            
            cancel_container.addWidget(cancel_button)
            cancel_container.addWidget(cancel_hint)
            cancel_container.setSpacing(5)
            
            cancel_widget = QWidget()
            cancel_widget.setLayout(cancel_container)
            button_layout.addWidget(cancel_widget)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch(1)

        # 添加键盘事件处理
        def keyPressEvent(event):
            try:
                if event.key() == Qt.Key_Y:
                    dialog.accept()
                elif event.key() == Qt.Key_N and not single_button:
                    dialog.reject()
                else:
                    QDialog.keyPressEvent(dialog, event)
            except Exception as e:
                print(f"KeyPressEvent error in show_login_success1: {e}")
                QDialog.keyPressEvent(dialog, event)
        
        dialog.keyPressEvent = keyPressEvent

        # 居中显示
        if parent:
            dialog.adjustSize() # 自适应大小
            parent_rect = parent.geometry()
            parent_center = parent_rect.center()
            x = parent_center.x() - dialog.width() // 2
            y = parent_center.y() - dialog.height() // 2
            dialog.move(x, y)

        result = dialog.exec_()

        if result == QDialog.Accepted and callback:
            callback()

class EllipseUserButton(QPushButton):
    """自定义椭圆形用户按钮"""

    def __init__(self, user_id, gender, hand_preference, mark, subject_type="A", parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.gender = gender
        self.hand_preference = hand_preference
        self.mark = mark
        self.subject_type = subject_type
        self.selected = False
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedSize(160, 80)
        self.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
        self.update_style()
        self.clicked.connect(self.toggle_selection)

    def update_style(self):
        if self.selected:
            bg_color = "#1f4788"  # <-- 选中时的背景色 (深蓝色)
            border_color = "#0d2540"  # <-- 选中时的边框色 (更深蓝色)
            hover_color = "#2a5ba0"  # <-- 选中时悬停的颜色 (亮蓝色)
            text_color = "white"  # <-- 选中时的文字颜色 (白色)

        else:
            bg_color = "#f8f9fa"
            text_color = "#333"
            border_color = "#e1e5e9"
            hover_color = "#e67e22" if self.subject_type == "C" else (
                "#4c63d2" if self.subject_type == "A" else "#f093fb")
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg_color}; color: {text_color}; border: 2px solid {border_color};
                border-radius: 25px; font-weight: bold; padding: 5px;
            }}
            QPushButton:hover {{ border: 2px solid {hover_color}; }}
        """)
        # 显示处理过的标识
        display_text = self.mark if hasattr(self, 'original_mark') else self.mark
        self.setText(f"{display_text}")

    def toggle_selection(self):
        self.selected = not self.selected
        self.update_style()
        if hasattr(self.parent(), 'on_user_selected'):
            self.parent().on_user_selected(self)


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from src.ui.login import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 添加全屏显示并动态调整组件大小
        self.showFullScreen()
        self.adjust_components_for_fullscreen()
        self.interface_win = Interfacewindow()
        self.interface_win.hide()  # 确保创建后不显示，直到登录完成
        self.login_handler = LoginInfoHandler()
        self.selected_subject_a = None
        self.selected_subject_b = None
        self.selected_subject_c = None
        self.subject_a_buttons = []
        self.subject_b_buttons = []
        self.subject_c_buttons = []
        self.selected_task = None
        self.task_buttons = []
        self.setup_connections()
        self.create_task_buttons()
        self.load_users_and_create_buttons()
        self.setup_button_cursors()
        self._closing = False  # 添加关闭标志
        self._transitioning = False  # 添加正常切换标志

    def set_window_icon(self):
        """设置窗口图标，包含错误处理"""
        icon_paths = [
            'icons/EEG_paint.ico',
            'icons/EEG_paint.jpg',
            '../icons/EEG_paint.ico',
            '../../icons/EEG_paint.ico'
        ]
        
        for icon_path in icon_paths:
            try:
                if os.path.exists(icon_path):
                    self.setWindowIcon(QIcon(icon_path))
                    print(f"LoginWindow: 成功设置窗口图标: {icon_path}")
                    return True
            except Exception as e:
                print(f"LoginWindow: 设置图标 {icon_path} 失败: {e}")
                continue
        
        print("LoginWindow: 警告: 未找到可用的图标文件，使用默认图标")
        return False

    def adjust_components_for_fullscreen(self):
        """动态调整组件大小以适应全屏显示"""
        # 获取屏幕尺寸
        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # 计算缩放比例
        original_width = 1400
        original_height = 900
        scale_x = screen_width / original_width
        scale_y = screen_height / original_height

        # 调整主容器大小和位置
        container_width = int(1200 * scale_x)
        container_height = int(700 * scale_y)
        container_x = int((screen_width - container_width) / 2)
        container_y = int((screen_height - container_height) / 2)

        self.ui.main_container.setGeometry(QtCore.QRect(container_x, container_y, container_width, container_height))

        # 调整左面板
        left_panel_width = int(600 * scale_x * 0.85)  # 稍微调整比例
        left_panel_height = container_height
        self.ui.left_panel.setGeometry(QtCore.QRect(0, 0, left_panel_width, left_panel_height))
        self.ui.left_overlay.setGeometry(QtCore.QRect(0, 0, left_panel_width, left_panel_height))

        # 调整右面板
        right_panel_width = container_width - left_panel_width
        right_panel_height = container_height
        self.ui.right_panel.setGeometry(QtCore.QRect(left_panel_width, 0, right_panel_width, right_panel_height))

        # 调整右面板内的组件
        # 任务选择卡片
        card_width = int(481 * scale_x * 0.9)
        card_height = int(160 * scale_y)
        card_x = int((right_panel_width - card_width) / 2)
        
        # 标题 - 自适应大小，移除固定尺寸限制
        title_y = int(40 * scale_y)  # 往上移更多避免重叠
        title_width = int(right_panel_width * 0.95)  # 使用右面板95%宽度
        title_height = int(140 * scale_y)  # 增加高度确保文字显示完整
        title_x = int((right_panel_width - title_width) / 2)  # 居中对齐
        self.ui.login_title.setGeometry(QtCore.QRect(title_x, title_y, title_width, title_height))
        card_y = int(180 * scale_y)  # 恢复原来位置
        self.ui.task_selection_card.setGeometry(QtCore.QRect(card_x, card_y, card_width, card_height))

        # 调整任务选择卡片内部组件
        self.ui.task_selection_title.setGeometry(QtCore.QRect(20, 20, int(350 * scale_x * 0.9), int(40 * scale_y)))
        self.ui.task_button_container.setGeometry(QtCore.QRect(20, int(65 * scale_y), int(441 * scale_x * 0.9), int(85 * scale_y)))

        # 被试选择卡片
        subject_card_y = int(360 * scale_y)
        self.ui.subject_a_card.setGeometry(QtCore.QRect(card_x, subject_card_y, card_width, card_height))

        # 调整被试卡片内部组件
        self.ui.subject_a_icon.setGeometry(QtCore.QRect(-100, 20, int(80 * scale_x), int(40 * scale_y)))
        self.ui.subject_a_title.setGeometry(QtCore.QRect(20, 20, int(350 * scale_x * 0.9), int(40 * scale_y)))
        self.ui.subject_a_ellipse_container.setGeometry(QtCore.QRect(20, int(65 * scale_y), int(441 * scale_x * 0.9), int(85 * scale_y)))

        # 登录按钮
        button_width = int(300 * scale_x)
        button_height = int(60 * scale_y)
        button_x = int((right_panel_width - button_width) / 2)
        button_y = int(580 * scale_y)
        self.ui.final_login_button.setGeometry(QtCore.QRect(button_x, button_y, button_width, button_height))

        # 调整右上角按钮框架
        frame_width = int(112 * scale_x)
        frame_height = int(78 * scale_y)
        frame_x = right_panel_width - frame_width
        self.ui.frame_5.setGeometry(QtCore.QRect(frame_x, 0, frame_width, frame_height))

        # 更新字体大小
        self.update_font_sizes(scale_x, scale_y)

    def update_font_sizes(self, scale_x, scale_y):
        """根据缩放比例更新字体大小"""
        # 获取平均缩放比例
        avg_scale = (scale_x + scale_y) / 2
        
        # 更新标题字体 - 调整为45pt
        title_font = self.ui.login_title.font()
        title_font.setPointSize(int(45 * avg_scale))  # 改为45pt
        title_font.setBold(True)  # 加粗
        title_font.setWeight(75)
        self.ui.login_title.setFont(title_font)
        
        # 更新任务选择标题字体
        task_title_font = self.ui.task_selection_title.font()
        task_title_font.setPointSize(int(20 * avg_scale))
        self.ui.task_selection_title.setFont(task_title_font)
        
        # 更新被试标题字体
        subject_title_font = self.ui.subject_a_title.font()
        subject_title_font.setPointSize(int(20 * avg_scale))
        self.ui.subject_a_title.setFont(subject_title_font)
        
        # 更新登录按钮字体
        button_font = self.ui.final_login_button.font()
        button_font.setPointSize(int(30 * avg_scale))
        self.ui.final_login_button.setFont(button_font)

    def setup_button_cursors(self):
        """为所有按钮设置手型光标"""
        # 登录相关按钮
        self.ui.final_login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.close_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.minimize_button.setCursor(QCursor(Qt.PointingHandCursor))

    def setup_connections(self):
        self.ui.final_login_button.clicked.connect(self.final_login)
        # 连接关闭和缩小按钮
        self.ui.close_button.clicked.connect(self.close_application)
        self.ui.minimize_button.clicked.connect(self.minimize_window)

    def create_task_buttons(self):
        """创建任务编号选择按钮"""
        layout = QHBoxLayout(self.ui.task_button_container)
        layout.setSpacing(8)
        # 将边距设为0，让布局完全控制空间
        layout.setContentsMargins(0, 0, 0, 0)

        tasks = ["SZ-21", "SZ-22", "SZ-23"]

        # 在最开始添加一个弹性空间
        layout.addStretch()

        for task in tasks:
            button = QPushButton(task)
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setFixedSize(160, 80)
            button.setFont(QFont("Microsoft YaHei", 30, QFont.Bold))
            # 3. & 4. 修改样式表，包括圆角和选中时的颜色
            button.setStyleSheet("""
                            QPushButton {
                                background-color: #f8f9fa;
                                color: #333;
                                border: 2px solid #e1e5e9; /* 边框改为2px以匹配用户按钮 */
                                border-radius: 30px;     /* 圆角改为30px以形成药丸形状 */
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                border: 2px solid #4c63d2; /* 悬停颜色可以统一为A类型的蓝色 */
                            }
                            QPushButton:checked {
                                /* --- 选中时使用深绿色高亮 --- */
                                background-color: #1f4788; /* <-- 选中时的背景色 (深蓝色) */
                                color: white;             /* <-- 选中时的文字颜色 (白色) */
                                border: 2px solid #0d2540; /* <-- 选中时的边框色 (更深蓝色) */
                            }
                        """)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, task_name=task: self.on_task_selected(task_name))
            self.task_buttons.append(button)

            # 添加按钮
            layout.addWidget(button)
            # 每添加一个按钮后，都添加一个弹性空间
            layout.addStretch()

    def on_task_selected(self, task_name):
        """处理任务选择"""
        for button in self.task_buttons:
            if button.text() == task_name:
                button.setChecked(True)
                self.selected_task = task_name
            else:
                button.setChecked(False)

    def load_users_and_create_buttons(self):
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'user_account', 'Experimenter.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, 性别, 惯用手, 标识 FROM user")
            users = cursor.fetchall()
            # 只为主航天员创建按钮，副航天员根据选择自动确定
            self.create_ellipse_buttons_for_subject(users, "A")

        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", f"加载用户数据失败: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def create_ellipse_buttons_for_subject(self, users, subject_type):
        if subject_type == "A":
            container = self.ui.subject_a_ellipse_container
            button_list = self.subject_a_buttons

        layout = QHBoxLayout(container)
        layout.setSpacing(8)
        # 将边距设为0，让布局完全控制空间
        layout.setContentsMargins(0, 0, 0, 0)

        astronaut_users = [user for user in users if user[3] in ['SZ21-01', 'SZ21-02', 'SZ21-03']]

        # 在最开始添加一个弹性空间
        layout.addStretch()

        for user_id, gender, hand_preference, mark in astronaut_users:
            display_mark = mark.replace('SZ21-', '')
            button = EllipseUserButton(user_id, gender, hand_preference, display_mark, subject_type, container)
            button.original_mark = mark
            button_list.append(button)

            # 添加按钮
            layout.addWidget(button)
            # 每添加一个按钮后，都添加一个弹性空间
            layout.addStretch()

            button.clicked.connect(lambda checked, btn=button, st=subject_type: self.on_user_selected(btn, st))

    def on_user_selected(self, selected_button, subject_type):
        if subject_type == "A":
            button_list = self.subject_a_buttons
        elif subject_type == "B":
            button_list = self.subject_b_buttons
        else:  # subject_type == "C"
            button_list = self.subject_c_buttons
        for button in button_list:
            if button != selected_button:
                button.selected = False
                button.update_style()
        if selected_button.selected:
            user_info = {'id': selected_button.user_id, 'gender': selected_button.gender,
                         'hand_preference': selected_button.hand_preference, 'mark': selected_button.original_mark}
            if subject_type == "A":
                self.selected_subject_a = user_info
                # 自动选择副航天员
                self.auto_select_assistants(selected_button.original_mark)
            elif subject_type == "B":
                self.selected_subject_b = user_info
            else:  # subject_type == "C"
                self.selected_subject_c = user_info
        else:
            if subject_type == "A":
                self.selected_subject_a = None
                self.selected_subject_b = None
                self.selected_subject_c = None
            elif subject_type == "B":
                self.selected_subject_b = None
            else:  # subject_type == "C"
                self.selected_subject_c = None

    def auto_select_assistants(self, primary_mark):
        """根据主航天员自动选择副航天员"""
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'user_account', 'Experimenter.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, 性别, 惯用手, 标识 FROM user")
            users = cursor.fetchall()

            # 获取所有航天员
            astronauts = [user for user in users if user[3] in ['SZ21-01', 'SZ21-02', 'SZ21-03']]

            # 找到副航天员（除了主航天员之外的两个）
            assistants = [user for user in astronauts if user[3] != primary_mark]

            if len(assistants) >= 2:
                # 选择第一个作为副航天员②
                self.selected_subject_b = {
                    'id': assistants[0][0],
                    'gender': assistants[0][1],
                    'hand_preference': assistants[0][2],
                    'mark': assistants[0][3]
                }
                # 选择第二个作为副航天员③
                self.selected_subject_c = {
                    'id': assistants[1][0],
                    'gender': assistants[1][1],
                    'hand_preference': assistants[1][2],
                    'mark': assistants[1][3]
                }
        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", f"自动选择副航天员失败: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def final_login(self):
        if not self.selected_task:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "请选择任务代号")
            return
        if not self.selected_subject_a:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "请选择被测航天员")
            return
        if not self.selected_subject_b:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "系统错误：副航天员未自动选择")
            return
        if not self.selected_subject_c:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "系统错误：副航天员未自动选择")
            return
        # 检查三个人员不能是同一人
        selected_marks = [self.selected_subject_a['mark'], self.selected_subject_b['mark'],
                          self.selected_subject_c['mark']]
        if len(set(selected_marks)) != 3:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "三个人员不能是同一人")
            return

        if self.validate_user(self.selected_subject_a) and self.validate_user(
                self.selected_subject_b) and self.validate_user(self.selected_subject_c):
            self.save_subjects_info()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            create_experiment_structure(
                task_code=self.selected_task,
                subject1_id=self.selected_subject_a['id'], subject2_id=self.selected_subject_b['id'],
                subject1_gender=self.selected_subject_a['gender'], subject2_gender=self.selected_subject_b['gender'],
                subject1_hand=self.selected_subject_a['hand_preference'],
                subject2_hand=self.selected_subject_b['hand_preference'],
                subject1_mark=self.selected_subject_a['mark'], subject2_mark=self.selected_subject_b['mark'],
                login_time=timestamp,
                subject3_id=self.selected_subject_c['id'], subject3_gender=self.selected_subject_c['gender'],
                subject3_hand=self.selected_subject_c['hand_preference'], subject3_mark=self.selected_subject_c['mark']
            )
            import os
            output_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'output_data', 'output_subInfo.db')
            output_txt_path = os.path.join(os.path.dirname(__file__), '..', '..', 'output_data', 'output_subInfo.txt')
            export_to_txt(output_db_path, "data", output_txt_path)

            success_text = (f"登录成功！\n\n"
                            f"任务代号   ：{self.selected_task}\n"
                            f"被测代号   ：{self.selected_subject_a['mark'].replace('SZ21-', '')} \n"
                            f"辅助代号   ：{self.selected_subject_b['mark'].replace('SZ21-', '')} 和 {self.selected_subject_c['mark'].replace('SZ21-', '')}\n"
                            )

            # 显示登录成功确认对话框
            CustomDialog.show_login_success1(self,  "登录成功", success_text,
                                            font_size=25, callback=self.transition_to_main_interface)

    def transition_to_main_interface(self):
        """切换到主实验界面"""
        self._transitioning = True  # 标记为正常切换
        self.close()
        # 强制设置全屏显示
        self.interface_win.showFullScreen()
        self.interface_win.setWindowState(Qt.WindowFullScreen)

    def close_application(self):
        """处理关闭按钮点击事件"""
        if self._closing:
            return
        self._closing = True

        reply = CustomDialog.ask_question(
            self,
            QStyle.SP_MessageBoxQuestion,
            "确认退出",
            "确定要退出软件吗？"
        )

        if reply == QDialog.Accepted:
            print("登录界面已退出。")
            QApplication.quit()  # 直接退出应用程序
        else:
            self._closing = False

    def minimize_window(self):
        """处理缩小按钮点击事件"""
        self.showMinimized()

    def closeEvent(self, event):
        """重写关闭事件，添加二次确认"""
        # 如果是正常切换或已经在关闭过程中，直接接受
        if self._transitioning or self._closing:
            event.accept()
            return

        self._closing = True
        reply = CustomDialog.ask_question(
            self,
            QStyle.SP_MessageBoxQuestion,
            "确认退出",
            "您确定要退出登录界面吗？"
        )

        if reply == QDialog.Accepted:
            print("登录界面已退出。")
            event.accept()
        else:
            self._closing = False
            event.ignore()

    def validate_user(self, user_info):
        try:
            import os
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'user_account', 'Experimenter.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM user WHERE id = ? AND 性别 = ? AND 惯用手 = ? AND 标识 = ?',
                           (user_info['id'], user_info['gender'], user_info['hand_preference'], user_info['mark']))
            if cursor.fetchone():
                return True
            else:
                CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告",
                                          f"用户信息不匹配或不存在: {user_info['id']}")
                return False
        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", f"数据库查询失败: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def save_subjects_info(self):
        try:
            self.login_handler.set_subject1_info(self.selected_subject_a['id'], self.selected_subject_a['gender'],
                                                 self.selected_subject_a['hand_preference'],
                                                 self.selected_subject_a['mark'])
            self.login_handler.set_subject2_info(self.selected_subject_b['id'], self.selected_subject_b['gender'],
                                                 self.selected_subject_b['hand_preference'],
                                                 self.selected_subject_b['mark'])
            # 增加人员③的信息设置
            if hasattr(self.login_handler, 'set_subject3_info'):
                self.login_handler.set_subject3_info(self.selected_subject_c['id'], self.selected_subject_c['gender'],
                                                     self.selected_subject_c['hand_preference'],
                                                     self.selected_subject_c['mark'])
            shared_data.user1_id, shared_data.user1_gender, shared_data.user1_hand = self.selected_subject_a['id'], \
            self.selected_subject_a['gender'], self.selected_subject_a['hand_preference']
            shared_data.user1_mark = self.selected_subject_a['mark'].replace('SZ21-', '')
            shared_data.user2_id, shared_data.user2_gender, shared_data.user2_hand = self.selected_subject_b['id'], \
            self.selected_subject_b['gender'], self.selected_subject_b['hand_preference']
            shared_data.user2_mark = self.selected_subject_b['mark'].replace('SZ21-', '')
            # 增加人员③的共享数据
            if hasattr(shared_data, 'user3_id'):
                shared_data.user3_id, shared_data.user3_gender, shared_data.user3_hand = self.selected_subject_c['id'], \
                self.selected_subject_c['gender'], self.selected_subject_c['hand_preference']
                shared_data.user3_mark = self.selected_subject_c['mark'].replace('SZ21-', '')
            timestamp = time.strftime('%m-%d %H:%M')
            self.save_to_database(self.selected_subject_a, timestamp)
            self.save_to_database(self.selected_subject_b, timestamp)
            self.save_to_database(self.selected_subject_c, timestamp)
        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", f"保存被试信息失败: {e}")

    def save_to_database(self, user_info, timestamp):
        try:
            import os
            output_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'output_data', 'output_subInfo.db')
            conn_output = sqlite3.connect(output_db_path)
            cursor_output = conn_output.cursor()
            cursor_output.execute('''CREATE TABLE IF NOT EXISTS data (
                登录时间 timestamp TEXT NOT NULL, 被试编号 FLOAT NOT NULL, 性别 TEXT NOT NULL, 
                惯用手 TEXT NOT NULL, 标识 TEXT NOT NULL)''')
            cursor_output.execute('INSERT INTO data(登录时间, 被试编号, 性别, 惯用手, 标识) VALUES(?,?,?,?,?)',
                                  (timestamp, user_info['id'], user_info['gender'], user_info['hand_preference'],
                                   user_info['mark']))
            conn_output.commit()
        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", f"保存数据失败: {e}")
        finally:
            if 'conn_output' in locals():
                conn_output.close()



if __name__ == '__main__':
    import os
    import sys

    # 添加项目根目录到Python路径
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    sys.path.insert(0, project_root)

    ti = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    # 确保能找到配置文件路径
    from src.config.config_manager import get_name_file_path
    with open(get_name_file_path(), "w") as file:
        file.write(ti)
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())