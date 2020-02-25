# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_regex_builder.ui'
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


class Ui_regex_builder(object):
    def setupUi(self, regex_builder):
        if regex_builder.objectName():
            regex_builder.setObjectName(u"regex_builder")
        regex_builder.resize(892, 158)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(regex_builder.sizePolicy().hasHeightForWidth())
        regex_builder.setSizePolicy(sizePolicy)
        regex_builder.setSizeGripEnabled(False)
        self.verticalLayout = QVBoxLayout(regex_builder)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.text_edit = QLineTextEdit(regex_builder)
        self.text_edit.setObjectName(u"text_edit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.text_edit.sizePolicy().hasHeightForWidth())
        self.text_edit.setSizePolicy(sizePolicy1)
        self.text_edit.setMinimumSize(QSize(0, 30))
        self.text_edit.setMaximumSize(QSize(16777215, 30))
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit.setTabChangesFocus(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        self.verticalLayout.addWidget(self.text_edit)

        self.group_buttons = QWidget(regex_builder)
        self.group_buttons.setObjectName(u"group_buttons")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.group_buttons.sizePolicy().hasHeightForWidth())
        self.group_buttons.setSizePolicy(sizePolicy2)
        self.group_buttons.setMinimumSize(QSize(235, 75))
        self.horizontalLayout_2 = QHBoxLayout(self.group_buttons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.button_static = QPushButton(self.group_buttons)
        self.button_static.setObjectName(u"button_static")
        sizePolicy2.setHeightForWidth(self.button_static.sizePolicy().hasHeightForWidth())
        self.button_static.setSizePolicy(sizePolicy2)
        self.button_static.setMinimumSize(QSize(75, 75))

        self.horizontalLayout_2.addWidget(self.button_static)

        self.button_dynamic = QPushButton(self.group_buttons)
        self.button_dynamic.setObjectName(u"button_dynamic")
        sizePolicy2.setHeightForWidth(self.button_dynamic.sizePolicy().hasHeightForWidth())
        self.button_dynamic.setSizePolicy(sizePolicy2)
        self.button_dynamic.setMinimumSize(QSize(75, 75))

        self.horizontalLayout_2.addWidget(self.button_dynamic)

        self.button_ep = QPushButton(self.group_buttons)
        self.button_ep.setObjectName(u"button_ep")
        sizePolicy2.setHeightForWidth(self.button_ep.sizePolicy().hasHeightForWidth())
        self.button_ep.setSizePolicy(sizePolicy2)
        self.button_ep.setMinimumSize(QSize(75, 75))
        self.button_ep.setMaximumSize(QSize(75, 75))

        self.horizontalLayout_2.addWidget(self.button_ep)


        self.verticalLayout.addWidget(self.group_buttons)

        self.button_confirm = QPushButton(regex_builder)
        self.button_confirm.setObjectName(u"button_confirm")

        self.verticalLayout.addWidget(self.button_confirm)


        self.retranslateUi(regex_builder)

        QMetaObject.connectSlotsByName(regex_builder)
    # setupUi

    def retranslateUi(self, regex_builder):
        regex_builder.setWindowTitle(QCoreApplication.translate("regex_builder", u"Mark for Regex", None))
        self.text_edit.setPlaceholderText(QCoreApplication.translate("regex_builder", u"<Insert a representative filename here>", None))
        self.button_static.setText(QCoreApplication.translate("regex_builder", u"Static", None))
        self.button_dynamic.setText(QCoreApplication.translate("regex_builder", u"Dynamic", None))
        self.button_ep.setText(QCoreApplication.translate("regex_builder", u"Episode\n"
"Number", None))
        self.button_confirm.setText(QCoreApplication.translate("regex_builder", u"Confirm", None))
    # retranslateUi

