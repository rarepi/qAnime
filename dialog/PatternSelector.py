from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import QDialog, QTextEdit, QTableWidgetItem, QHeaderView

import qa2_util
from qa2_tvdb import TVDBHandler
from ui.ui_pattern_selector import Ui_pattern_selector


class PatternSelector(QDialog):
    def __init__(self, settings):
        super(PatternSelector, self).__init__()
        self.ui = Ui_pattern_selector()
        self.ui.setupUi(self)

    def fill_tree(self):
        pass
