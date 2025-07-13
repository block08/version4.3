from PyQt5 import Qt, QtCore,QtWidgets
from PyQt5.QtCore import qDebug, QUrl, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItem, QDesktopServices
from PyQt5.QtWidgets import QWidget

from .ui.ui_datawidget import Ui_DataWidget
import os
class DataWidget(QWidget):
    def __init__(self, parent=None):
        super(DataWidget, self).__init__(parent)
        self.ui = Ui_DataWidget()
        self.ui.setupUi(self)
        # 数据模型
        self.data_model = Qt.QStandardItemModel(self)
        self.header=['被试航天员', '辅助航天员1',"辅助航天员2",'日期时间',"操作"]
        self.data_model.setHorizontalHeaderLabels(self.header)
        self.ui.tableView.setModel(self.data_model)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(Qt.QHeaderView.Stretch)
        self.readBehavioralData()
        self.ui.tableView.setEditTriggers(QtWidgets.QTableView.NoEditTriggers)
        self.ui.tableView.clicked.connect(self.openData)

        #搜索
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.data_model)
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.ui.tableView.setModel(self.proxy_model)

        self.ui.pushButton.clicked.connect(self.search)
    def readBehavioralData(self):
        # 获取当前目录下所有文件夹名称
        folder_names =[]
        for dir in  os.listdir('Behavioral_data'):
            if os.path.isdir("Behavioral_data/"+dir):
                folder_names.append(dir)
        self.folder_names=folder_names
        for name in folder_names:
            row_data=name.split("_")
            col1=row_data[4]
            col2=row_data[6]
            col3=row_data[8]
            col4=row_data[0]+"_"+row_data[1]+"  "+row_data[2]+"_"+row_data[3]
            row = []
            item=QStandardItem(col1)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            row.append(item)
            item = QStandardItem(col2)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            row.append(item)
            item = QStandardItem(col3)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            row.append(item)
            item = QStandardItem(col4)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            row.append(item)
            item = QStandardItem("查看")
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            row.append(item)
            self.data_model.appendRow(row)
    def openData(self,index):
        if index.column()==4:
            row=index.row()
            path="Behavioral_data/"+self.folder_names[row]
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    def search(self):
        self.proxy_model.setFilterFixedString(self.ui.lineEdit.text())

