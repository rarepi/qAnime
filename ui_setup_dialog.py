# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_setup_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_setup_dialog(object):
    def setupUi(self, setup_dialog):
        if setup_dialog.objectName():
            setup_dialog.setObjectName(u"setup_dialog")
        setup_dialog.resize(800, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(setup_dialog.sizePolicy().hasHeightForWidth())
        setup_dialog.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(setup_dialog);
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.v_layout_absolute_path = QVBoxLayout();
        self.v_layout_absolute_path.setObjectName(u"v_layout_absolute_path")
        self.label_absolute_path = QLabel(setup_dialog)
        self.label_absolute_path.setObjectName(u"label_absolute_path")

        self.v_layout_absolute_path.addWidget(self.label_absolute_path);

        self.ledit_absolute_path = QLineEdit(setup_dialog)
        self.ledit_absolute_path.setObjectName(u"ledit_absolute_path")

        self.v_layout_absolute_path.addWidget(self.ledit_absolute_path);


        self.verticalLayout_3.addLayout(self.v_layout_absolute_path);

        self.v_layout_qbt_url = QVBoxLayout();
        self.v_layout_qbt_url.setObjectName(u"v_layout_qbt_url")
        self.label_qbt_url = QLabel(setup_dialog)
        self.label_qbt_url.setObjectName(u"label_qbt_url")

        self.v_layout_qbt_url.addWidget(self.label_qbt_url);

        self.ledit_qbt_url = QLineEdit(setup_dialog)
        self.ledit_qbt_url.setObjectName(u"ledit_qbt_url")

        self.v_layout_qbt_url.addWidget(self.ledit_qbt_url);


        self.verticalLayout_3.addLayout(self.v_layout_qbt_url);

        self.v_layout_qbt_login = QVBoxLayout();
        self.v_layout_qbt_login.setObjectName(u"v_layout_qbt_login")
        self.label_qbt_login = QLabel(setup_dialog)
        self.label_qbt_login.setObjectName(u"label_qbt_login")

        self.v_layout_qbt_login.addWidget(self.label_qbt_login);

        self.h_layout_qbt_login = QHBoxLayout();
        self.h_layout_qbt_login.setObjectName(u"h_layout_qbt_login")
        self.ledit_qbt_user = QLineEdit(setup_dialog)
        self.ledit_qbt_user.setObjectName(u"ledit_qbt_user")

        self.h_layout_qbt_login.addWidget(self.ledit_qbt_user);

        self.ledit_qbt_password = QLineEdit(setup_dialog)
        self.ledit_qbt_password.setObjectName(u"ledit_qbt_password")

        self.h_layout_qbt_login.addWidget(self.ledit_qbt_password);


        self.v_layout_qbt_login.addLayout(self.h_layout_qbt_login);


        self.verticalLayout_3.addLayout(self.v_layout_qbt_login);

        self.v_layout_tvdb_url = QVBoxLayout();
        self.v_layout_tvdb_url.setObjectName(u"v_layout_tvdb_url")
        self.label_tvdb_url = QLabel(setup_dialog)
        self.label_tvdb_url.setObjectName(u"label_tvdb_url")

        self.v_layout_tvdb_url.addWidget(self.label_tvdb_url);

        self.ledit_tvdb_url = QLineEdit(setup_dialog)
        self.ledit_tvdb_url.setObjectName(u"ledit_tvdb_url")

        self.v_layout_tvdb_url.addWidget(self.ledit_tvdb_url);


        self.verticalLayout_3.addLayout(self.v_layout_tvdb_url);

        self.v_layout_tvdb_key = QVBoxLayout();
        self.v_layout_tvdb_key.setObjectName(u"v_layout_tvdb_key")
        self.label_tvdb_key = QLabel(setup_dialog)
        self.label_tvdb_key.setObjectName(u"label_tvdb_key")

        self.v_layout_tvdb_key.addWidget(self.label_tvdb_key);

        self.ledit_tvdb_key = QLineEdit(setup_dialog)
        self.ledit_tvdb_key.setObjectName(u"ledit_tvdb_key")

        self.v_layout_tvdb_key.addWidget(self.ledit_tvdb_key);


        self.verticalLayout_3.addLayout(self.v_layout_tvdb_key);

        self.btn_confirm = QPushButton(setup_dialog)
        self.btn_confirm.setObjectName(u"btn_confirm")

        self.verticalLayout_3.addWidget(self.btn_confirm);


        self.retranslateUi(setup_dialog)

        QMetaObject.connectSlotsByName(setup_dialog)
    # setupUi

    def retranslateUi(self, setup_dialog):
        setup_dialog.setWindowTitle(QCoreApplication.translate("setup_dialog", u"Dialog", None))
        self.label_absolute_path.setText(QCoreApplication.translate("setup_dialog", u"Absolute path for the QBittorrent executable.", None))
        self.label_qbt_url.setText(QCoreApplication.translate("setup_dialog", u"URL to your QBittorrent Web API", None))
        self.ledit_qbt_url.setText(QCoreApplication.translate("setup_dialog", u"http://localhost:8080/api/v2", None))
        self.label_qbt_login.setText(QCoreApplication.translate("setup_dialog", u"QBittorrent Web UI Login", None))
        self.label_tvdb_url.setText(QCoreApplication.translate("setup_dialog", u"URL to the TheTVDB.com API", None))
        self.ledit_tvdb_url.setText(QCoreApplication.translate("setup_dialog", u"https://api.thetvdb.com", None))
        self.label_tvdb_key.setText(QCoreApplication.translate("setup_dialog", u"TheTVDB.com API Key", None))
        self.ledit_tvdb_key.setText(QCoreApplication.translate("setup_dialog", u"2323B61F3A9DA8C8", None))
        self.btn_confirm.setText(QCoreApplication.translate("setup_dialog", u"OK", None))
    # retranslateUi

