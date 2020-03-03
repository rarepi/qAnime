from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import QDialog, QTextEdit, QTableWidgetItem, QHeaderView, QTreeWidgetItem, QTreeView

import qa2_util
from qa2_tvdb import TVDBHandler
from ui.ui_pattern_selector import Ui_pattern_selector


class PatternSelector(QDialog):
    def __init__(self, settings, series_data):
        super(PatternSelector, self).__init__()
        self.ui = Ui_pattern_selector()
        self.ui.setupUi(self)

        self.settings = settings
        self.series_data = series_data
        self.tvdb_handler = None

        self.tvdb_id = None
        self.season = None
        self.pattern_regex = None
        self.pattern_target = None

        self.ui.tree_patterns.header().setStretchLastSection(False)
        self.ui.tree_patterns.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.tree_patterns.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.tree_patterns.setStyleSheet("QTreeView::item {padding: 0 15px;}")

        self.ui.tree_patterns.itemSelectionChanged.connect(self.confirm_button_toggle)
        self.ui.button_confirm.clicked.connect(self.confirm)

        self.ui.button_confirm.setEnabled(False)

    def load(self):
        self.tvdb_handler = TVDBHandler(self.settings)
        for tvdb_id, data in self.series_data.items():
            item_tvdb_id = QTreeWidgetItem()
            item_tvdb_id.setData(0, 300, tvdb_id)
            item_tvdb_id.setText(0, self.tvdb_handler.get_series_name(tvdb_id))     # TODO implement caching
            for season, patterns in data.items():
                item_season = QTreeWidgetItem(item_tvdb_id)
                item_season.setData(0, 300, season)
                if season == "-1":
                    item_season.setText(0, "No Season Order (Absolute Numbering)")
                else:
                    item_season.setText(0, "Season " + season)
                for rgx, tar in patterns.items():
                    item_patterns = QTreeWidgetItem(item_season)
                    item_patterns.setFlags(item_patterns.flags() | Qt.ItemNeverHasChildren)
                    item_patterns.setText(0, rgx)
                    item_patterns.setText(1, tar)
            self.ui.tree_patterns.addTopLevelItem(item_tvdb_id)

    def confirm(self):
        if len(self.ui.tree_patterns.selectedItems()) != 1:     # expecting 1 row
            return  # TODO ERROR
        selected_widget = self.ui.tree_patterns.selectedItems()[0]
        self.tvdb_id = selected_widget.parent().parent().data(0, 300)
        self.season = selected_widget.parent().data(0, 300)
        self.pattern_regex = selected_widget.text(0)
        self.pattern_target = selected_widget.text(1)
        qa2_util.debug(self.tvdb_id, self.season, '\n', self.pattern_regex, self.pattern_target, level=1)
        self.accept()

    @Slot()
    def confirm_button_toggle(self):
        if len(self.ui.tree_patterns.selectedItems()) == 1 \
                and self.ui.tree_patterns.selectedItems()[0].flags() & Qt.ItemNeverHasChildren:
            self.ui.button_confirm.setEnabled(True)
        else:
            self.ui.button_confirm.setEnabled(False)