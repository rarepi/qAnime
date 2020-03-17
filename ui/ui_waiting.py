# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_waiting.ui'
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


class Ui_waiting(object):
    def setupUi(self, waiting):
        if waiting.objectName():
            waiting.setObjectName(u"waiting")
        waiting.setWindowModality(Qt.ApplicationModal)
        waiting.resize(600, 150)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(waiting.sizePolicy().hasHeightForWidth())
        waiting.setSizePolicy(sizePolicy)
        waiting.setMinimumSize(QSize(600, 150))
        waiting.setMaximumSize(QSize(600, 16777215))
        waiting.setModal(True)
        self.container_icon = QWidget(waiting)
        self.container_icon.setObjectName(u"container_icon")
        self.container_icon.setGeometry(QRect(0, 0, 150, 150))
        sizePolicy.setHeightForWidth(self.container_icon.sizePolicy().hasHeightForWidth())
        self.container_icon.setSizePolicy(sizePolicy)
        self.container_icon.setMinimumSize(QSize(150, 150))
        self.container_icon.setMaximumSize(QSize(150, 16777215))
        self.container_messages = QWidget(waiting)
        self.container_messages.setObjectName(u"container_messages")
        self.container_messages.setGeometry(QRect(150, 0, 600, 150))
        sizePolicy.setHeightForWidth(self.container_messages.sizePolicy().hasHeightForWidth())
        self.container_messages.setSizePolicy(sizePolicy)
        self.container_messages.setMinimumSize(QSize(600, 150))
        self.container_messages.setMaximumSize(QSize(600, 16777215))

        self.retranslateUi(waiting)

        QMetaObject.connectSlotsByName(waiting)
    # setupUi

    def retranslateUi(self, waiting):
        waiting.setWindowTitle(QCoreApplication.translate("waiting", u"Busy", None))
    # retranslateUi

