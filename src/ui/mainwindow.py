from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction
from PyQt5.QtCore import Qt

from .ui.res import  res
from .ui.ui_mainwindow import Ui_MainWindow
from .exercisewidget import ExerciseWidget
from .datawidget import DataWidget
class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.user_menu=QtWidgets.QMenu()

        self.task_id=QAction("任务代号:")
        self.rest_astronaut=QAction("被测航天员:")
        self.assist_astronauts = QAction("辅助航天员:")
        self.exit=QAction("退出")
        self.ui.user.setMenu(self.user_menu)


        #设置用户按钮
        self.ui.user.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.ui.user.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        #设置列表
        self.ui.listWidget.itemClicked.connect(self.itemClicked)
        self.stack_widget=QtWidgets.QStackedWidget()
        self.ui.horizontalLayout_3.addWidget(self.stack_widget)
        self.ui.horizontalLayout_3.setStretch(0, 1)
        self.ui.horizontalLayout_3.setStretch(1, 3)
        self.ui.listWidget.setFixedWidth(200)
        #设置窗口
        self.stack_widget.addWidget(ExerciseWidget())
        self.stack_widget.addWidget(QtWidgets.QWidget())
        self.stack_widget.addWidget(QtWidgets.QWidget())
        self.stack_widget.addWidget(DataWidget())
        self.stack_widget.addWidget(QtWidgets.QWidget())



    def itemClicked(self,item):
        #当前选中的导航栏索引
        index=self.ui.listWidget.currentIndex().row()
        self.stack_widget.setCurrentIndex(index)





