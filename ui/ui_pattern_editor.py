# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_pattern_editor.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

from QLineTextEdit import QLineTextEdit


class Ui_pattern_editor(object):
    def setupUi(self, pattern_editor):
        if pattern_editor.objectName():
            pattern_editor.setObjectName(u"pattern_editor")
        pattern_editor.resize(892, 113)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(pattern_editor.sizePolicy().hasHeightForWidth())
        pattern_editor.setSizePolicy(sizePolicy)
        pattern_editor.setSizeGripEnabled(False)
        self.verticalLayout = QVBoxLayout(pattern_editor)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.text_edit_regex = QLineTextEdit(pattern_editor)
        self.text_edit_regex.setObjectName(u"text_edit_regex")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.text_edit_regex.sizePolicy().hasHeightForWidth())
        self.text_edit_regex.setSizePolicy(sizePolicy1)
        self.text_edit_regex.setMinimumSize(QSize(0, 30))
        self.text_edit_regex.setMaximumSize(QSize(16777215, 30))
        self.text_edit_regex.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_regex.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_regex.setTabChangesFocus(True)
        self.text_edit_regex.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit_regex.setAcceptRichText(False)

        self.verticalLayout.addWidget(self.text_edit_regex)

        self.text_edit_target = QTextEdit(pattern_editor)
        self.text_edit_target.setObjectName(u"text_edit_target")
        sizePolicy1.setHeightForWidth(self.text_edit_target.sizePolicy().hasHeightForWidth())
        self.text_edit_target.setSizePolicy(sizePolicy1)
        self.text_edit_target.setMinimumSize(QSize(0, 30))
        self.text_edit_target.setMaximumSize(QSize(16777215, 30))
        self.text_edit_target.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_target.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_target.setTabChangesFocus(True)
        self.text_edit_target.setLineWrapMode(QTextEdit.NoWrap)
        self.text_edit_target.setAcceptRichText(False)

        self.verticalLayout.addWidget(self.text_edit_target)

        self.button_confirm = QPushButton(pattern_editor)
        self.button_confirm.setObjectName(u"button_confirm")

        self.verticalLayout.addWidget(self.button_confirm)


        self.retranslateUi(pattern_editor)

        QMetaObject.connectSlotsByName(pattern_editor)
    # setupUi

    def retranslateUi(self, pattern_editor):
        pattern_editor.setWindowTitle(QCoreApplication.translate("pattern_editor", u"Mark for Regex", None))
        self.text_edit_regex.setPlaceholderText("")
        self.button_confirm.setText(QCoreApplication.translate("pattern_editor", u"Confirm", None))
    # retranslateUi

