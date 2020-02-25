from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import QDialog, QTextEdit

from ui.ui_pattern_editor import Ui_pattern_editor


class PatternEditor(QDialog):
    done = Signal(str, str)

    def __init__(self):
        super(PatternEditor, self).__init__()
        self.ui = Ui_pattern_editor()
        self.ui.setupUi(self)

        self.ui.button_confirm.clicked.connect(self.finalize_regex)

        font = QFont("Verdana", 14)
        fm = QFontMetrics(font)
        text_height = fm.lineSpacing() + 10
        self.ui.text_edit_regex.setFont(font)
        self.ui.text_edit_target.setFont(font)
        self.ui.text_edit_regex.setMinimumHeight(text_height)
        self.ui.text_edit_target.setMinimumHeight(text_height)

    def setText(self, text):
        self.ui.text_edit_regex.setText(text)

    @Slot()
    def finalize_regex(self):
        # noinspection PyUnresolvedReferences
        self.done.emit(self.ui.text_edit_regex.toPlainText(), self.ui.text_edit_target.toPlainText())
