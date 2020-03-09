# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_series_data_editor.ui'
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


class Ui_series_data_editor(object):
    def setupUi(self, series_data_editor):
        if series_data_editor.objectName():
            series_data_editor.setObjectName(u"series_data_editor")
        series_data_editor.resize(1426, 477)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(series_data_editor.sizePolicy().hasHeightForWidth())
        series_data_editor.setSizePolicy(sizePolicy)
        series_data_editor.setSizeGripEnabled(False)
        self.verticalLayout = QVBoxLayout(series_data_editor)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.layout_main = QVBoxLayout()
        self.layout_main.setObjectName(u"layout_main")
        self.tree_patterns = QTreeWidget(series_data_editor)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"Regex Pattern");
        self.tree_patterns.setHeaderItem(__qtreewidgetitem)
        self.tree_patterns.setObjectName(u"tree_patterns")
        self.tree_patterns.setEnabled(True)
        self.tree_patterns.setMidLineWidth(0)
        self.tree_patterns.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tree_patterns.setTabKeyNavigation(False)
        self.tree_patterns.setProperty("showDropIndicator", False)
        self.tree_patterns.setDragDropOverwriteMode(False)
        self.tree_patterns.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree_patterns.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree_patterns.setAllColumnsShowFocus(True)
        self.tree_patterns.header().setVisible(False)
        self.tree_patterns.header().setHighlightSections(False)
        self.tree_patterns.header().setStretchLastSection(False)

        self.layout_main.addWidget(self.tree_patterns)

        self.layout_form = QFormLayout()
        self.layout_form.setObjectName(u"layout_form")
        self.line_tvdb_id = QLineEdit(series_data_editor)
        self.line_tvdb_id.setObjectName(u"line_tvdb_id")

        self.layout_form.setWidget(0, QFormLayout.FieldRole, self.line_tvdb_id)

        self.label_tvdb_id = QLabel(series_data_editor)
        self.label_tvdb_id.setObjectName(u"label_tvdb_id")

        self.layout_form.setWidget(0, QFormLayout.LabelRole, self.label_tvdb_id)

        self.label_season = QLabel(series_data_editor)
        self.label_season.setObjectName(u"label_season")

        self.layout_form.setWidget(1, QFormLayout.LabelRole, self.label_season)

        self.line_season = QLineEdit(series_data_editor)
        self.line_season.setObjectName(u"line_season")

        self.layout_form.setWidget(1, QFormLayout.FieldRole, self.line_season)

        self.line_regex = QLineEdit(series_data_editor)
        self.line_regex.setObjectName(u"line_regex")

        self.layout_form.setWidget(2, QFormLayout.FieldRole, self.line_regex)

        self.label_regex = QLabel(series_data_editor)
        self.label_regex.setObjectName(u"label_regex")

        self.layout_form.setWidget(2, QFormLayout.LabelRole, self.label_regex)

        self.label_target = QLabel(series_data_editor)
        self.label_target.setObjectName(u"label_target")

        self.layout_form.setWidget(3, QFormLayout.LabelRole, self.label_target)

        self.line_target = QLineEdit(series_data_editor)
        self.line_target.setObjectName(u"line_target")

        self.layout_form.setWidget(3, QFormLayout.FieldRole, self.line_target)


        self.layout_main.addLayout(self.layout_form)

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.setObjectName(u"layout_buttons")
        self.hspacer_buttons = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.layout_buttons.addItem(self.hspacer_buttons)

        self.button_revert = QPushButton(series_data_editor)
        self.button_revert.setObjectName(u"button_revert")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.button_revert.sizePolicy().hasHeightForWidth())
        self.button_revert.setSizePolicy(sizePolicy1)
        self.button_revert.setMinimumSize(QSize(100, 0))
        self.button_revert.setFocusPolicy(Qt.NoFocus)

        self.layout_buttons.addWidget(self.button_revert)

        self.button_save = QPushButton(series_data_editor)
        self.button_save.setObjectName(u"button_save")
        sizePolicy1.setHeightForWidth(self.button_save.sizePolicy().hasHeightForWidth())
        self.button_save.setSizePolicy(sizePolicy1)
        self.button_save.setMinimumSize(QSize(100, 0))
        self.button_save.setFocusPolicy(Qt.NoFocus)

        self.layout_buttons.addWidget(self.button_save)

        self.button_cancel = QPushButton(series_data_editor)
        self.button_cancel.setObjectName(u"button_cancel")
        sizePolicy1.setHeightForWidth(self.button_cancel.sizePolicy().hasHeightForWidth())
        self.button_cancel.setSizePolicy(sizePolicy1)
        self.button_cancel.setMinimumSize(QSize(100, 0))
        self.button_cancel.setFocusPolicy(Qt.NoFocus)

        self.layout_buttons.addWidget(self.button_cancel)


        self.layout_main.addLayout(self.layout_buttons)


        self.verticalLayout.addLayout(self.layout_main)


        self.retranslateUi(series_data_editor)

        QMetaObject.connectSlotsByName(series_data_editor)
    # setupUi

    def retranslateUi(self, series_data_editor):
        series_data_editor.setWindowTitle("")
        ___qtreewidgetitem = self.tree_patterns.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("series_data_editor", u"Target Pattern", None));
        self.label_tvdb_id.setText(QCoreApplication.translate("series_data_editor", u"TVDB ID", None))
        self.label_season.setText(QCoreApplication.translate("series_data_editor", u"Season", None))
        self.label_regex.setText(QCoreApplication.translate("series_data_editor", u"Regex Pattern", None))
        self.label_target.setText(QCoreApplication.translate("series_data_editor", u"Target Pattern", None))
        self.button_revert.setText(QCoreApplication.translate("series_data_editor", u"Revert", None))
        self.button_save.setText(QCoreApplication.translate("series_data_editor", u"Save", None))
        self.button_cancel.setText(QCoreApplication.translate("series_data_editor", u"Cancel", None))
    # retranslateUi

