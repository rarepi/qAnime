# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main_window.ui'
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


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1520, 580)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(1520, 580))
        MainWindow.setMaximumSize(QSize(1520, 580))
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName(u"central_widget")
        self.horizontalLayout = QHBoxLayout(self.central_widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.vlayout_buttons = QVBoxLayout()
        self.vlayout_buttons.setObjectName(u"vlayout_buttons")
        self.button_scan = QPushButton(self.central_widget)
        self.button_scan.setObjectName(u"button_scan")

        self.vlayout_buttons.addWidget(self.button_scan)

        self.button_add = QPushButton(self.central_widget)
        self.button_add.setObjectName(u"button_add")

        self.vlayout_buttons.addWidget(self.button_add)

        self.button_edit = QPushButton(self.central_widget)
        self.button_edit.setObjectName(u"button_edit")

        self.vlayout_buttons.addWidget(self.button_edit)

        self.vlayout_spacer = QVBoxLayout()
        self.vlayout_spacer.setObjectName(u"vlayout_spacer")
        self.vlayout_spacer.setSizeConstraint(QLayout.SetDefaultConstraint)

        self.vlayout_buttons.addLayout(self.vlayout_spacer)


        self.horizontalLayout.addLayout(self.vlayout_buttons)

        self.vlayout_table = QVBoxLayout()
        self.vlayout_table.setObjectName(u"vlayout_table")
        self.tree_torrents = QTreeWidget(self.central_widget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_torrents.setHeaderItem(__qtreewidgetitem)
        self.tree_torrents.setObjectName(u"tree_torrents")

        self.vlayout_table.addWidget(self.tree_torrents)

        self.button_confirm_rename = QPushButton(self.central_widget)
        self.button_confirm_rename.setObjectName(u"button_confirm_rename")

        self.vlayout_table.addWidget(self.button_confirm_rename)


        self.horizontalLayout.addLayout(self.vlayout_table)

        MainWindow.setCentralWidget(self.central_widget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1520, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"qAnime2", None))
        self.button_scan.setText(QCoreApplication.translate("MainWindow", u"Scan", None))
        self.button_add.setText(QCoreApplication.translate("MainWindow", u"Add", None))
        self.button_edit.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.button_confirm_rename.setText(QCoreApplication.translate("MainWindow", u"Confirm rename", None))
    # retranslateUi

