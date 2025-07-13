from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton, QVBoxLayout
from .ui.ui_exercisewidget import Ui_ExerciseWidget
class ExerciseWidget(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(ExerciseWidget, self).__init__(parent)

        self.ui = Ui_ExerciseWidget()
        self.ui.setupUi(self)

        self.buttongroup = QtWidgets.QButtonGroup()
        #初始化按钮组
        self.buttongroup.addButton(self.ui.button0,0)
        self.buttongroup.addButton(self.ui.button1,1)
        self.buttongroup.addButton(self.ui.button2,2)
        self.buttongroup.addButton(self.ui.button3,3)
        self.buttongroup.addButton(self.ui.button4,4)
        self.buttongroup.buttonClicked[int].connect(self.on_button_id_clicked)


    def on_button_id_clicked(self, id):
        print(id)