# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_boolean_dialog.ui'
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


class Ui_bool_dialog(object):
    def setupUi(self, bool_dialog):
        if bool_dialog.objectName():
            bool_dialog.setObjectName(u"bool_dialog")
        bool_dialog.resize(400, 118)
        self.verticalLayout = QVBoxLayout(bool_dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(bool_dialog)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.label)

        self.button_box = QDialogButtonBox(bool_dialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.No|QDialogButtonBox.Yes)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(bool_dialog)
        self.button_box.accepted.connect(bool_dialog.accept)
        self.button_box.rejected.connect(bool_dialog.reject)

        QMetaObject.connectSlotsByName(bool_dialog)
    # setupUi

    def retranslateUi(self, bool_dialog):
        bool_dialog.setWindowTitle(QCoreApplication.translate("bool_dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("bool_dialog", u"Question", None))
    # retranslateUi

