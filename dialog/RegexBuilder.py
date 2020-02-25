from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QTextCharFormat, QBrush, QColor, QFont, QFontMetrics
from PySide2.QtWidgets import QDialog, QTextEdit

import qa2_util
from dialog.RegexIndices import RegexIndices
from ui.ui_regex_builder import Ui_regex_builder


class RegexBuilder(QDialog):
    done = Signal(str)

    def __init__(self):
        super(RegexBuilder, self).__init__()
        self.ui = Ui_regex_builder()
        self.ui.setupUi(self)

        self.regex_indices = RegexIndices()

        self.ui.button_static.clicked.connect(self.mark_for_regex)
        self.ui.button_dynamic.clicked.connect(self.mark_for_regex)
        self.ui.button_ep.clicked.connect(self.mark_for_regex)
        self.ui.button_confirm.clicked.connect(self.make_regex)

        self.ui.group_buttons.parent().layout().setAlignment(self.ui.group_buttons, Qt.AlignHCenter)
        self.ui.text_edit.setText("Hunter.x.Hunter.2011.S02E24.720p-Hi10p.BluRay.AAC2.0.x264-CTR.[F880ACB6].mkv")
        font = QFont("Verdana", 14)
        self.ui.text_edit.setFont(font)
        fm = QFontMetrics(font)
        text_height = fm.lineSpacing() + 10
        self.ui.text_edit.setMinimumHeight(text_height)
        self.modes = {
            "static": QTextCharFormat(),
            "dynamic": QTextCharFormat(),
            "ep": QTextCharFormat()
        }
        self.color_static = "#FFFFFF"
        self.color_dynamic = "#55AAFF"
        self.color_ep = "#99CC00"
        self.modes["static"].setBackground(QBrush(QColor(self.color_static)))
        self.modes["dynamic"].setBackground(QBrush(QColor(self.color_dynamic)))
        self.modes["ep"].setBackground(QBrush(QColor(self.color_ep)))
        self.ui.button_static.setStyleSheet("background-color: " + self.color_static)
        self.ui.button_dynamic.setStyleSheet("background-color: " + self.color_dynamic)
        self.ui.button_ep.setStyleSheet("background-color: " + self.color_ep)

    @Slot()
    def mark_for_regex(self):
        self.ui.text_edit.blockSignals(True)
        cursor = self.ui.text_edit.textCursor()
        if cursor.hasSelection():
            idx0 = cursor.selectionStart()
            idx1 = cursor.selectionEnd()
            if self.sender() == self.ui.button_static:
                cursor.setCharFormat(self.modes["static"])
                self.regex_indices.insert(idx0, idx1, "s")
            if self.sender() == self.ui.button_dynamic:
                cursor.setCharFormat(self.modes["dynamic"])
                self.regex_indices.insert(idx0, idx1, "d")
            if self.sender() == self.ui.button_ep:
                cursor.setCharFormat(self.modes["ep"])
                self.regex_indices.insert(idx0, idx1, "e")
            cursor.clearSelection()
            self.ui.text_edit.setTextCursor(cursor)
        self.ui.text_edit.blockSignals(False)

    @Slot()
    def make_regex(self):
        dyn_regex = ".*"
        ep_regex = "\\d"
        text = self.ui.text_edit.toPlainText()

        previous = len(text)
        for x, y in self.regex_indices.data[::-1]:  # iterate list in reverse, so our indices stay correct while modifying the string
            if y is 'd':
                text = text[:x] + dyn_regex + text[previous:]
                previous = x
            elif y is 'e':
                ep_digits = previous-x
                text = text[:x] + '(' + ep_regex*ep_digits + ')' + text[previous:]
                previous = x
            elif y is 's':
                escaped_text_segment = text[x:previous]
                for c in qa2_util.CHARSET_REGEX_ESCAPES:
                    if c in escaped_text_segment:
                        escaped_text_segment = escaped_text_segment.replace(c, "\\" + c)
                text = text[:x] + escaped_text_segment + text[previous:]
                previous = x
            qa2_util.debug(text, level=1)

        # noinspection PyUnresolvedReferences
        self.done.emit(text)