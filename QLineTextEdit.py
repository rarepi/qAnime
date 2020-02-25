from PySide2.QtCore import QMimeData
from PySide2.QtGui import QKeyEvent, Qt
from PySide2.QtWidgets import QTextEdit


class QLineTextEdit(QTextEdit):
    def __init__(self, parent):
        super(QLineTextEdit, self).__init__(parent)

    def keyPressEvent(self, e:QKeyEvent):
        # print(e.key())
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            print("Multiline input blocked.")
        else:
            super().keyPressEvent(e)

    def insertFromMimeData(self, source:QMimeData):
        print("User tries to insert MimeData:", source.formats())
        if not source.hasText():
            return  # plain text only

        plain_source = QMimeData()
        plain_source.setText(''.join(source.text().split()))    # removes any kind of whitespace

        super(QLineTextEdit, self).insertFromMimeData(plain_source)