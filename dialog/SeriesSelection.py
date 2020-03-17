from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import QDialog, QTextEdit, QTableWidgetItem, QHeaderView

import qa2_util
from qa2_tvdb import TVDBHandler
from ui.ui_series_selection import Ui_series_selection


class SeriesSelection(QDialog):
    def __init__(self, settings):
        super(SeriesSelection, self).__init__()
        self.ui = Ui_series_selection()
        self.ui.setupUi(self)
        self.selected_tvdb_id = None
        self.selected_season = None

        self.tvdb_handler = TVDBHandler(settings)
        self.tvdb_handler.auth()  # TODO

        self.ui.table_search_results.setEnabled(False)
        self.ui.button_confirm.setEnabled(False)
        self.ui.table_search_results.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.table_search_results.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.table_search_results.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.table_search_results.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.ui.input_name.returnPressed.connect(self.search_series)
        self.tvdb_handler.series_results_collected.connect(self.list_search_results)
        self.ui.table_search_results.itemSelectionChanged.connect(self.confirm_button_toggle)
        self.ui.radio_a.toggled.connect(self.input_season_sync)
        self.ui.radio_a.toggled.connect(self.confirm_button_toggle)
        self.ui.input_season.textChanged.connect(self.confirm_button_toggle)
        self.ui.button_confirm.clicked.connect(self.confirm)

    @Slot()
    def search_series(self):
        self.tvdb_handler.get_series(self.ui.input_name.text())

    @Slot(list)
    def list_search_results(self, results:list):
        print(results)
        self.ui.table_search_results.setEnabled(True)
        row = self.ui.table_search_results.rowCount()
        self.ui.table_search_results.setRowCount(self.ui.table_search_results.rowCount()+len(results))
        for tvdb_id, name, year, network in results:
            self.ui.table_search_results.setItem(row, 0, QTableWidgetItem(str(tvdb_id)))
            self.ui.table_search_results.setItem(row, 1, QTableWidgetItem(name))
            self.ui.table_search_results.setItem(row, 2, QTableWidgetItem(year))
            self.ui.table_search_results.setItem(row, 3, QTableWidgetItem(network))
            row += 1

    @Slot()
    def confirm_button_toggle(self):
        if len(self.ui.table_search_results.selectionModel().selectedRows()) == 1\
                and (self.ui.radio_a.isChecked()
                     or self.ui.radio_s.isChecked() and self.ui.input_season.text().isnumeric()):
            self.ui.button_confirm.setEnabled(True)
        else:
            self.ui.button_confirm.setEnabled(False)

    @Slot()
    def input_season_sync(self):
        self.ui.input_season.setEnabled(self.ui.radio_s.isChecked())

    @Slot()
    def confirm(self):
        if len(self.ui.table_search_results.selectedItems()) != self.ui.table_search_results.columnCount():     # expecting 1 row
            return  # TODO ERROR
        self.selected_tvdb_id = int(self.ui.table_search_results.selectedItems()[0].text())
        if self.ui.radio_s.isChecked():
            self.selected_season = int(self.ui.input_season.text())
        else:
            self.selected_season = -1
        self.accept()
