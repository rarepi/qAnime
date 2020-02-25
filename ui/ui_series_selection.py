# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_series_selection.ui'
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


class Ui_series_selection(object):
    def setupUi(self, series_selection):
        if series_selection.objectName():
            series_selection.setObjectName(u"series_selection")
        series_selection.resize(859, 361)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(series_selection.sizePolicy().hasHeightForWidth())
        series_selection.setSizePolicy(sizePolicy)
        series_selection.setSizeGripEnabled(False)
        self.verticalLayout = QVBoxLayout(series_selection)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(series_selection)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label)

        self.input_name = QLineEdit(series_selection)
        self.input_name.setObjectName(u"input_name")

        self.verticalLayout.addWidget(self.input_name)

        self.table_search_results = QTableWidget(series_selection)
        if (self.table_search_results.columnCount() < 4):
            self.table_search_results.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_search_results.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table_search_results.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table_search_results.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.table_search_results.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.table_search_results.setObjectName(u"table_search_results")
        self.table_search_results.setEnabled(True)
        self.table_search_results.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_search_results.setTabKeyNavigation(False)
        self.table_search_results.setProperty("showDropIndicator", False)
        self.table_search_results.setDragDropOverwriteMode(False)
        self.table_search_results.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_search_results.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_search_results.setSortingEnabled(True)
        self.table_search_results.horizontalHeader().setProperty("showSortIndicator", True)
        self.table_search_results.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.table_search_results)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.formLayout.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.formLayout.setHorizontalSpacing(6)
        self.formLayout.setVerticalSpacing(6)
        self.formLayout.setContentsMargins(6, -1, 6, -1)
        self.label_s_or_a = QLabel(series_selection)
        self.label_s_or_a.setObjectName(u"label_s_or_a")

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.label_s_or_a)

        self.radio_a = QRadioButton(series_selection)
        self.radio_a.setObjectName(u"radio_a")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.radio_a.sizePolicy().hasHeightForWidth())
        self.radio_a.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(2, QFormLayout.SpanningRole, self.radio_a)

        self.radio_s = QRadioButton(series_selection)
        self.radio_s.setObjectName(u"radio_s")
        sizePolicy2.setHeightForWidth(self.radio_s.sizePolicy().hasHeightForWidth())
        self.radio_s.setSizePolicy(sizePolicy2)
        self.radio_s.setChecked(True)

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.radio_s)

        self.input_season = QLineEdit(series_selection)
        self.input_season.setObjectName(u"input_season")
        sizePolicy.setHeightForWidth(self.input_season.sizePolicy().hasHeightForWidth())
        self.input_season.setSizePolicy(sizePolicy)
        self.input_season.setMaximumSize(QSize(75, 16777215))

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.input_season)


        self.verticalLayout.addLayout(self.formLayout)

        self.button_confirm = QPushButton(series_selection)
        self.button_confirm.setObjectName(u"button_confirm")

        self.verticalLayout.addWidget(self.button_confirm)


        self.retranslateUi(series_selection)

        QMetaObject.connectSlotsByName(series_selection)
    # setupUi

    def retranslateUi(self, series_selection):
        series_selection.setWindowTitle("")
        self.label.setText(QCoreApplication.translate("series_selection", u"Name of series?", None))
        ___qtablewidgetitem = self.table_search_results.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("series_selection", u"TVDB ID", None));
        ___qtablewidgetitem1 = self.table_search_results.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("series_selection", u"Series Name", None));
        ___qtablewidgetitem2 = self.table_search_results.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("series_selection", u"Year", None));
        ___qtablewidgetitem3 = self.table_search_results.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("series_selection", u"Network", None));
        self.label_s_or_a.setText(QCoreApplication.translate("series_selection", u"Are episode numbers given in seasonal or absolute numbers?", None))
        self.radio_a.setText(QCoreApplication.translate("series_selection", u"Absolute", None))
        self.radio_s.setText(QCoreApplication.translate("series_selection", u"Seasonal", None))
        self.input_season.setPlaceholderText(QCoreApplication.translate("series_selection", u"Season", None))
        self.button_confirm.setText(QCoreApplication.translate("series_selection", u"Confirm", None))
    # retranslateUi

