from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QLabel, QVBoxLayout

from ui.ui_waiting import Ui_waiting, QDialog
from waitingspinnerwidget import QtWaitingSpinner


class QWaitingDialog(QDialog):
    def __init__(self):
        super(QWaitingDialog, self).__init__()
        self.ui = Ui_waiting()
        self.ui.setupUi(self)
        # self.window().setFixedSize(self.window().size())
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)

        self.layout_messages = QVBoxLayout(self.ui.container_messages)
        # self.layout_messages.setGeometry(self.ui.container_messages.geometry())
        self.layout_messages.setAlignment(Qt.AlignVCenter)

        spinner = QtWaitingSpinner(self.ui.container_icon)
        spinner.setRoundness(10.0)
        spinner.setMinimumTrailOpacity(0.0)
        spinner.setTrailFadePercentage(70.0)
        spinner.setNumberOfLines(15)
        spinner.setLineLength(3)
        spinner.setLineWidth(10)
        spinner.setInnerRadius(25)
        spinner.setRevolutionsPerSecond(1)
        spinner.setColor(QColor(25, 126, 62))   # tvdb green
        spinner.start()

        self.active_conditions = 0

    @Slot(int, str)
    def add_waiting_condition(self, index:int, msg:str):
        label = QLabel(msg)
        self.ui.container_messages.layout().addWidget(label)
        label.setObjectName("label_" + str(index))
        self.active_conditions += 1
        print(index, msg)

    @Slot(int)
    def succeed_waiting_condition(self, index:int):
        print(index)
        label = self.ui.container_messages.findChild(QLabel, "label_" + str(index))
        if label is None:
            return
        label.setText(label.text() + " - DONE")
        self.active_conditions -= 1
        self.finish()

    @Slot(int)
    def fail_waiting_condition(self, index:int):
        label = self.ui.container_messages.findChild(QLabel, "label_" + str(index))
        label.setText(label.text() + " - FAILED")
        self.active_conditions -= 1
        self.finish()

    def clear(self):
        for child in self.ui.container_messages.findChildren(QLabel).reverse():
            self.ui.container_messages.layout().removeWidget(child)

    def finish(self):
        if self.active_conditions <= 0:
            # self.clear()
            self.accept()
