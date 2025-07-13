#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QFont, QPixmap
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
    def __init__(self, parent, icon_type, title, text, font_size=22, width=600, height=300, auto_close_ms=None,
                 callback=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建主容器框架，用于实现明显的边框
        main_frame = QFrame(self)
        main_frame.setGeometry(0, 0, width, height)
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 20px;
                border: 3px solid #000000;  /* 黑色边框 */
            }}
        """)

        # 在主框架内创建布局
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        main_layout.addStretch(1)  # 添加顶部伸缩

        # 内容区域（图标 + 文字）
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 图标
        icon_label = QLabel(self)
        icon_pixmap = self.style().standardIcon(icon_type).pixmap(64, 64)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(64, 64)
        icon_label.setStyleSheet("border: none;")
        # 关键改动：将图标也设置为垂直居中对齐
        content_layout.addWidget(icon_label, alignment=Qt.AlignVCenter)

        # 文字
        text_label = QLabel(text, self)
        text_label.setFont(QFont("Microsoft YaHei", font_size))
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignVCenter)  # 文本在Label内垂直居中
        text_label.setStyleSheet("border: none; color: black;")  # 黑色文字配白色背景
        content_layout.addWidget(text_label, 1)  # 添加伸缩因子

        main_layout.addLayout(content_layout)

        main_layout.addStretch(1)  # 添加中部伸缩

        # 如果不是自动关闭，则添加按钮
        if not auto_close_ms:
            button_layout = QHBoxLayout()
            ok_button = QPushButton("确定", self)
            ok_button.setCursor(Qt.PointingHandCursor)
            ok_button.setFixedSize(140, 50)
            ok_button.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db; color: white; border: none; border-radius: 25px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #2471a3;
                }
            """)
            ok_button.clicked.connect(self.accept)
            button_layout.addStretch()
            button_layout.addWidget(ok_button)
            button_layout.addStretch()
            main_layout.addLayout(button_layout)
        else:
            # 如果是自动关闭，则启动定时器
            self.callback = callback
            QTimer.singleShot(auto_close_ms, self.auto_close_and_callback)

        main_layout.addStretch(1)  # 添加底部伸缩

    def auto_close_and_callback(self):
        self.accept()  # 关闭对话框
        if self.callback:
            self.callback()

    @staticmethod
    def show_message(parent, icon_type, title, text, font_size=22):
        dialog = CustomDialog(parent, icon_type, title, text, font_size)
        return dialog.exec_()

    @staticmethod
    def show_timed_message(parent, icon_type, title, text, font_size=22, duration=3000, callback=None):
        dialog = CustomDialog(parent, icon_type, title, text, font_size, auto_close_ms=duration, callback=callback)
        dialog.show()

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
        self.setFixedSize(130, 60)
        self.setFont(QFont("Arial", 20, QFont.Bold))
        self.update_style()
        self.clicked.connect(self.toggle_selection)

    def update_style(self):
        if self.selected:
            if self.subject_type == "A":
                bg_color = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(102, 126, 234, 255), stop:1 rgba(118, 75, 162, 255))"
                border_color = "#4c63d2"
                hover_color = "#4c63d2"
            elif self.subject_type == "B":
                bg_color = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(240, 147, 251, 255), stop:1 rgba(245, 87, 108, 255))"
                border_color = "#f093fb"
                hover_color = "#f093fb"
            else:  # subject_type == "C"
                bg_color = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(230, 126, 34, 255), stop:1 rgba(211, 84, 0, 255))"
                border_color = "#e67e22"
                hover_color = "#e67e22"
            text_color = "white"
        else:
            bg_color = "#f8f9fa"
            text_color = "#333"
            border_color = "#e1e5e9"
            hover_color = "#e67e22" if self.subject_type == "C" else ("#4c63d2" if self.subject_type == "A" else "#f093fb")
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

from .mainwindow import MainWindow
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        from .login import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.interface_win = Interfacewindow()
        self.interface_win = MainWindow()
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
        self.m_flag = False
        self.m_Position = QtCore.QPoint()

    def setup_connections(self):
        self.ui.final_login_button.clicked.connect(self.final_login)
    
    def create_task_buttons(self):
        """创建任务编号选择按钮"""
        layout = QHBoxLayout(self.ui.task_button_container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        tasks = ["SZ-21", "SZ-22", "SZ-23"]
        for task in tasks:
            button = QPushButton(task)
            button.setFixedSize(130, 40)
            button.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #333;
                    border: 3px solid #e1e5e9;
                    border-radius: 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    border: 3px solid #2ecc71;
                    background-color: #e8f5e8;
                }
                QPushButton:checked {
                    background-color: #2ecc71;
                    color: white;
                    border: 3px solid #27ae60;
                }
            """)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, task_name=task: self.on_task_selected(task_name))
            self.task_buttons.append(button)
            layout.addWidget(button)
        
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
            conn = sqlite3.connect("./user_account/Experimenter.db")
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

        layout = QGridLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(5, 5, 5, 5)
        buttons_per_row = 4
        
        # 只显示航天员编号：01, 02, 03
        astronaut_users = [user for user in users if user[3] in ['SZ21-01', 'SZ21-02', 'SZ21-03']]
        
        for i, (user_id, gender, hand_preference, mark) in enumerate(astronaut_users):
            # 只显示编号部分，去掉SZ21-前缀
            display_mark = mark.replace('SZ21-', '')
            button = EllipseUserButton(user_id, gender, hand_preference, display_mark, subject_type, container)
            button.original_mark = mark  # 保存原始标识
            button_list.append(button)
            row, col = i // buttons_per_row, i % buttons_per_row
            layout.addWidget(button, row, col)
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
            conn = sqlite3.connect("./user_account/Experimenter.db")
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
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "请选择任务编号")
            return
        if not self.selected_subject_a:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "请选择佩戴脑电帽的航天员")
            return
        if not self.selected_subject_b:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "系统错误：副航天员未自动选择")
            return
        if not self.selected_subject_c:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "系统错误：副航天员未自动选择")
            return
        # 检查三个人员不能是同一人
        selected_marks = [self.selected_subject_a['mark'], self.selected_subject_b['mark'], self.selected_subject_c['mark']]
        if len(set(selected_marks)) != 3:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxWarning, "警告", "三个人员不能是同一人")
            return

        if self.validate_user(self.selected_subject_a) and self.validate_user(self.selected_subject_b) and self.validate_user(self.selected_subject_c):
            self.save_subjects_info()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            create_experiment_structure(
                subject1_id=self.selected_subject_a['id'], subject2_id=self.selected_subject_b['id'],
                subject1_gender=self.selected_subject_a['gender'], subject2_gender=self.selected_subject_b['gender'],
                subject1_hand=self.selected_subject_a['hand_preference'],
                subject2_hand=self.selected_subject_b['hand_preference'],
                subject1_mark=self.selected_subject_a['mark'], subject2_mark=self.selected_subject_b['mark'],
                login_time=timestamp,
                subject3_id=self.selected_subject_c['id'], subject3_gender=self.selected_subject_c['gender'],
                subject3_hand=self.selected_subject_c['hand_preference'], subject3_mark=self.selected_subject_c['mark']
            )
            export_to_txt("./output_data/output_subInfo.db", "data", "./output_data/output_subInfo.txt")

            success_text = (f"登录成功！\n\n"
                            f"任务编号: {self.selected_task}\n"
                            f"被测航天员: {self.selected_subject_a['mark'].replace('SZ21-', '')} \n"
                            f"辅助航天员: {self.selected_subject_b['mark'].replace('SZ21-', '')} 和 {self.selected_subject_c['mark'].replace('SZ21-', '')}\n"
                            f"即将进入主界面...")

            # 显示自动关闭的提示框，并在结束后切换窗口
            CustomDialog.show_timed_message(self, QStyle.SP_MessageBoxInformation, "登录成功", success_text,
                                            font_size=18, duration=2000, callback=self.transition_to_main_interface)

    def transition_to_main_interface(self):
        """切换到主实验界面"""
        self.close()
        self.interface_win.show()

    def validate_user(self, user_info):
        try:
            conn = sqlite3.connect("./user_account/Experimenter.db")
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
            shared_data.user1_id, shared_data.user1_gender, shared_data.user1_hand = self.selected_subject_a['id'], self.selected_subject_a['gender'], self.selected_subject_a['hand_preference']
            shared_data.user1_mark = self.selected_subject_a['mark'].replace('SZ21-', '')
            shared_data.user2_id, shared_data.user2_gender, shared_data.user2_hand = self.selected_subject_b['id'], self.selected_subject_b['gender'], self.selected_subject_b['hand_preference']
            shared_data.user2_mark = self.selected_subject_b['mark'].replace('SZ21-', '')
            # 增加人员③的共享数据
            if hasattr(shared_data, 'user3_id'):
                shared_data.user3_id, shared_data.user3_gender, shared_data.user3_hand = self.selected_subject_c['id'], self.selected_subject_c['gender'], self.selected_subject_c['hand_preference']
                shared_data.user3_mark = self.selected_subject_c['mark'].replace('SZ21-', '')
            timestamp = time.strftime('%m-%d %H:%M')
            self.save_to_database(self.selected_subject_a, timestamp)
            self.save_to_database(self.selected_subject_b, timestamp)
            self.save_to_database(self.selected_subject_c, timestamp)
        except Exception as e:
            CustomDialog.show_message(self, QStyle.SP_MessageBoxCritical, "错误", f"保存被试信息失败: {e}")

    def save_to_database(self, user_info, timestamp):
        try:
            conn_output = sqlite3.connect("./output_data/output_subInfo.db")
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.move(event.globalPos() - self.m_Position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_flag = False


if __name__ == '__main__':
    ti = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    with open(f"./Behavioral_data/name.txt", "w") as file:
        file.write(ti)
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    sys.exit(app.exec_())