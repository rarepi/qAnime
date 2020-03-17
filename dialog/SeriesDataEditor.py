import copy
from enum import Enum, IntEnum
from typing import Union

from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import QDialog, QTextEdit, QTableWidgetItem, QHeaderView, QTreeWidgetItem, QTreeView

import qa2_util
from SeriesDataHandler import SeriesDataHandler
from qa2_tvdb import TVDBHandler
from ui.ui_series_data_editor import Ui_series_data_editor


def create_tvdb_id_item(tvdb_id, name) -> QTreeWidgetItem:
    item_tvdb_id = QTreeWidgetItem()
    item_tvdb_id.setData(0, PatternSelector.ItemDataRole.DATA_NAME, PatternSelector.ItemType.SERIES)
    item_tvdb_id.setData(0, PatternSelector.ItemDataRole.DATA, tvdb_id)
    item_tvdb_id.setText(0, name)
    return item_tvdb_id


def create_season_item(parent:QTreeWidgetItem, season) -> QTreeWidgetItem:
    item_season = QTreeWidgetItem(parent)
    item_season.setData(0, PatternSelector.ItemDataRole.DATA_NAME, PatternSelector.ItemType.SEASON)
    item_season.setData(0, PatternSelector.ItemDataRole.DATA, season)
    item_season.setText(0, format_season_text(season))
    return item_season


def create_pattern_item(parent:QTreeWidgetItem, regex, target):
    item_patterns = QTreeWidgetItem(parent)
    item_patterns.setFlags(item_patterns.flags() | Qt.ItemNeverHasChildren)
    item_patterns.setData(0, PatternSelector.ItemDataRole.DATA_NAME, PatternSelector.ItemType.PATTERN_SET)
    item_patterns.setData(0, PatternSelector.ItemDataRole.DATA, regex)
    item_patterns.setText(0, item_patterns.data(0, PatternSelector.ItemDataRole.DATA))
    item_patterns.setData(1, PatternSelector.ItemDataRole.DATA, target)
    item_patterns.setText(1, item_patterns.data(1, PatternSelector.ItemDataRole.DATA))
    return item_patterns


def format_season_text(season:Union[str, int]):
    season = str(season)
    if season == "-1":
        return "No Season Order (Absolute Numbering)"
    else:
        return "Season " + season


class PatternSelector(QDialog):
    class ItemType(IntEnum):
        SERIES = 0
        SEASON = 1
        PATTERN_SET = 2

    class ItemDataRole(IntEnum):
        DATA_NAME = 300
        DATA = 301

    def __init__(self, settings:dict):
        super(PatternSelector, self).__init__()
        self.ui = Ui_series_data_editor()
        self.ui.setupUi(self)

        self.settings = settings
        self.series_data_handler = SeriesDataHandler()  # series data remains None till we read()
        self.tvdb_handler = None    # to avoid unneeded authentication traffic, don't initialize till we need it

        self.ui.tree_patterns.header().setStretchLastSection(False)
        self.ui.tree_patterns.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.ui.tree_patterns.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui.tree_patterns.setStyleSheet("QTreeView::item {padding: 0 15px;}")

        self.ui.button_save.setEnabled(False)
        self.ui.button_cancel.setEnabled(True)
        self.ui.button_revert.setEnabled(False)

        # TODO: Report conflicting pattern sets appearing during any update_data_* function
        #  Currently any preexisting patterns are simply overwritten by the moved ones
        self.ui.tree_patterns.itemSelectionChanged.connect(self.display_selected_item)
        self.ui.line_tvdb_id.editingFinished.connect(self.update_data_tvdb_id)
        self.ui.line_season.editingFinished.connect(self.update_data_season)
        self.ui.line_regex.editingFinished.connect(self.update_data_pattern_set)
        self.ui.line_target.editingFinished.connect(self.update_data_pattern_set)

        self.ui.button_revert.clicked.connect(self.revert)
        self.ui.button_cancel.clicked.connect(self.reject)  # QDialog.reject()
        self.ui.button_save.clicked.connect(self.save)

    def load(self):
        self.ui.tree_patterns.clear()
        self.series_data_handler.read()
        self.tvdb_handler = TVDBHandler(self.settings)
        self.tvdb_handler.auth()    # TODO
        for tvdb_id, data in self.series_data_handler.series_data.items():
            item_tvdb_id = create_tvdb_id_item(tvdb_id, self.tvdb_handler.get_series_name(tvdb_id))
            for season, patterns in data.items():
                item_season = create_season_item(item_tvdb_id, season)
                for rgx, tar in patterns.items():
                    create_pattern_item(item_season, rgx, tar)
            self.ui.tree_patterns.addTopLevelItem(item_tvdb_id)

    @Slot()
    def revert(self):
        self.ui.button_revert.setEnabled(False)
        self.ui.button_save.setEnabled(False)
        self.load()

    @Slot()
    def save(self):
        self.series_data_handler.write()
        self.accept()

    @Slot()
    def display_selected_item(self):
        if len(self.ui.tree_patterns.selectedItems()) != 1:
            return
        selected_widget = self.ui.tree_patterns.selectedItems()[0]

        if selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SERIES:
            self.ui.line_tvdb_id.setText(selected_widget.data(0, self.ItemDataRole.DATA))
            self.ui.line_season.setText(None)
            self.ui.line_regex.setText(None)
            self.ui.line_target.setText(None)
            self.ui.line_tvdb_id.setEnabled(True)
            self.ui.line_season.setEnabled(False)
            self.ui.line_regex.setEnabled(False)
            self.ui.line_target.setEnabled(False)
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SEASON:
            self.ui.line_tvdb_id.setText(selected_widget.parent().data(0, self.ItemDataRole.DATA))
            self.ui.line_season.setText(selected_widget.data(0, self.ItemDataRole.DATA))
            self.ui.line_regex.setText(None)
            self.ui.line_target.setText(None)
            self.ui.line_tvdb_id.setEnabled(True)
            self.ui.line_season.setEnabled(True)
            self.ui.line_regex.setEnabled(False)
            self.ui.line_target.setEnabled(False)
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.PATTERN_SET:
            self.ui.line_tvdb_id.setText(selected_widget.parent().parent().data(0, self.ItemDataRole.DATA))
            self.ui.line_season.setText(selected_widget.parent().data(0, self.ItemDataRole.DATA))
            self.ui.line_regex.setText(selected_widget.data(0, self.ItemDataRole.DATA))
            self.ui.line_target.setText(selected_widget.data(1, self.ItemDataRole.DATA))
            self.ui.line_tvdb_id.setEnabled(True)
            self.ui.line_season.setEnabled(True)
            self.ui.line_regex.setEnabled(True)
            self.ui.line_target.setEnabled(True)
        else:
            return  # TODO ERROR

    @Slot()
    def update_data_tvdb_id(self):
        if len(self.ui.tree_patterns.selectedItems()) != 1:
            return
        qa2_util.debug("update_data_tvdb_id() called", level=1)
        selected_widget = self.ui.tree_patterns.selectedItems()[0]
        new_tvdb_id = self.ui.line_tvdb_id.text()
        text = self.tvdb_handler.get_series_name(new_tvdb_id)
        if not isinstance(text, str):
            text = "(SERIES NOT FOUND) " + new_tvdb_id

        # SERIES Item
        if selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SERIES:
            old_tvdb_id = selected_widget.data(0, self.ItemDataRole.DATA)
            if new_tvdb_id == old_tvdb_id:
                return

            for t_idx in range(self.ui.tree_patterns.topLevelItemCount()):
                new_tvdb_item = self.ui.tree_patterns.topLevelItem(t_idx)
                if new_tvdb_item.data(0, self.ItemDataRole.DATA) == new_tvdb_id:
                    # New tvdb id already has an entry

                    # Check if seasons are disjoint
                    for x in range(selected_widget.childCount()):
                        old_season_item = selected_widget.child(x)
                        season = old_season_item.data(0, self.ItemDataRole.DATA)
                        for y in range(new_tvdb_item.childCount()):
                            new_season_item = new_tvdb_item.child(y)
                            if season == new_season_item.data(0, self.ItemDataRole.DATA):
                                # existing season

                                qa2_util.debug("Season", season, "found in both data sets. Merging these sub-dictionaries:", "\n",
                                               self.series_data_handler.series_data[new_tvdb_id][season], "\n",
                                               self.series_data_handler.series_data[old_tvdb_id][season],
                                               level=1)

                                self.series_data_handler.series_data[new_tvdb_id][season] = \
                                    {**self.series_data_handler.series_data[new_tvdb_id][season],
                                     **self.series_data_handler.series_data[old_tvdb_id].pop(season)}

                                qa2_util.debug("Result:", self.series_data_handler.series_data[new_tvdb_id][season],
                                               level=1)

                                pattern_items1 = old_season_item.takeChildren()
                                pattern_items2 = new_season_item.takeChildren()

                                non_duplicates = [item2 for item2 in pattern_items2 if item2.data(0, self.ItemDataRole.DATA) not in
                                        [item1.data(0, self.ItemDataRole.DATA) for item1 in pattern_items1]]

                                new_season_item.addChildren(pattern_items1 + non_duplicates)

                                selected_widget.removeChild(old_season_item)
                                break
                        else:
                            # season is not preexisting in target widget

                            self.series_data_handler.series_data[new_tvdb_id][season] = \
                                self.series_data_handler.series_data[old_tvdb_id].pop(season)

                            selected_widget.removeChild(old_season_item)
                            new_tvdb_item.addChild(old_season_item)

                    if selected_widget.childCount() <= 0:
                        self.ui.tree_patterns.takeTopLevelItem(
                            self.ui.tree_patterns.indexOfTopLevelItem(selected_widget))
                    break
            else:
                # New tvdb id is not preexisting, so no merge needed. Just change the TVDB ID.
                selected_widget.setData(0, self.ItemDataRole.DATA, new_tvdb_id)
                selected_widget.setText(0, text)
                self.series_data_handler.series_data[new_tvdb_id] = self.series_data_handler.series_data.pop(old_tvdb_id)

            # clean up empty tvdb id entries in our json data
            try:
                if not self.series_data_handler.series_data[old_tvdb_id]:
                    qa2_util.debug("Removing empty dictionary entry for TVDB ID", old_tvdb_id, level=1)
                    del self.series_data_handler.series_data[old_tvdb_id]
            except KeyError:
                pass

        # SEASON item
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SEASON:
            old_tvdb_id_item = selected_widget.parent()
            old_tvdb_id = old_tvdb_id_item.data(0, self.ItemDataRole.DATA)
            if new_tvdb_id == old_tvdb_id:
                return
            season = selected_widget.data(0, self.ItemDataRole.DATA)

            for t_idx in range(self.ui.tree_patterns.topLevelItemCount()):
                new_tvdb_item = self.ui.tree_patterns.topLevelItem(t_idx)
                if new_tvdb_item.data(0, self.ItemDataRole.DATA) == new_tvdb_id:
                    # New tvdb id already has an entry
                    for y in range(new_tvdb_item.childCount()):
                        new_season_item = new_tvdb_item.child(y)
                        if season == new_season_item.data(0, self.ItemDataRole.DATA):
                            # same season
                            qa2_util.debug("Season", season,
                                           "found in both data sets. Merging these sub-dictionaries:", "\n",
                                           self.series_data_handler.series_data[new_tvdb_id][season], "\n",
                                           self.series_data_handler.series_data[old_tvdb_id][season],
                                           level=1)

                            self.series_data_handler.series_data[new_tvdb_id][season] = \
                                {**self.series_data_handler.series_data[new_tvdb_id][season],
                                 **self.series_data_handler.series_data[old_tvdb_id].pop(season)}

                            qa2_util.debug("Result:", self.series_data_handler.series_data[new_tvdb_id][season],
                                           level=1)

                            pattern_items1 = selected_widget.takeChildren()
                            pattern_items2 = new_season_item.takeChildren()

                            non_duplicates = [item2 for item2 in pattern_items2 if
                                              item2.data(0, self.ItemDataRole.DATA) not in
                                              [item1.data(0, self.ItemDataRole.DATA) for item1 in pattern_items1]]

                            new_season_item.addChildren(pattern_items1 + non_duplicates)

                            old_tvdb_id_item.removeChild(selected_widget)
                            break
                    else:
                        # season is not preexisting in target widget
                        self.series_data_handler.series_data[new_tvdb_id][season] = \
                            self.series_data_handler.series_data[old_tvdb_id].pop(season)

                        old_tvdb_id_item.removeChild(selected_widget)
                        new_tvdb_item.addChild(selected_widget)
                    break
            else:
                # New tvdb id is not preexisting, so no merge needed.
                new_tvdb_id_item = create_tvdb_id_item(new_tvdb_id, text)
                old_tvdb_id_item.removeChild(selected_widget)
                new_tvdb_id_item.addChild(selected_widget)
                self.ui.tree_patterns.addTopLevelItem(new_tvdb_id_item)
                self.series_data_handler.series_data[new_tvdb_id] = {
                    season:
                        self.series_data_handler.series_data[old_tvdb_id].pop(season)
                }

            if old_tvdb_id_item.childCount() <= 0:
                self.ui.tree_patterns.takeTopLevelItem(
                    self.ui.tree_patterns.indexOfTopLevelItem(old_tvdb_id_item))

            # clean up empty tvdb id entries in our json data
            try:
                if not self.series_data_handler.series_data[old_tvdb_id]:
                    qa2_util.debug("Removing empty dictionary entry for TVDB ID", old_tvdb_id, level=1)
                    del self.series_data_handler.series_data[old_tvdb_id]
            except KeyError:
                pass


        # PATTERN_SET item
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.PATTERN_SET:
            old_season_item = selected_widget.parent()
            old_tvdb_id_item = old_season_item.parent()
            old_tvdb_id = old_tvdb_id_item.data(0, self.ItemDataRole.DATA)
            if new_tvdb_id == old_tvdb_id:
                return
            season = old_season_item.data(0, self.ItemDataRole.DATA)
            this_regex = selected_widget.data(0, self.ItemDataRole.DATA)

            for t_idx in range(self.ui.tree_patterns.topLevelItemCount()):
                new_tvdb_item = self.ui.tree_patterns.topLevelItem(t_idx)
                if new_tvdb_item.data(0, self.ItemDataRole.DATA) == new_tvdb_id:
                    # New tvdb id already has an entry

                    for y in range(new_tvdb_item.childCount()):
                        new_season_item = new_tvdb_item.child(y)
                        if season == new_season_item.data(0, self.ItemDataRole.DATA):
                            # same season
                            qa2_util.debug("Season", season,
                                           "found in both data sets. Merging these sub-dictionaries:", "\n",
                                           self.series_data_handler.series_data[new_tvdb_id][season], "\n",
                                           self.series_data_handler.series_data[old_tvdb_id][season],
                                           level=1)

                            self.series_data_handler.series_data[new_tvdb_id][season][this_regex] = \
                                self.series_data_handler.series_data[old_tvdb_id][season].pop(this_regex)


                            qa2_util.debug("Result:", self.series_data_handler.series_data[new_tvdb_id][season],
                                           level=1)

                            pattern_items2 = new_season_item.takeChildren()

                            non_duplicates = [item2 for item2 in pattern_items2 if
                                              item2.data(0, self.ItemDataRole.DATA) != this_regex]

                            new_season_item.addChildren(non_duplicates)
                            old_season_item.removeChild(selected_widget)
                            new_season_item.addChild(selected_widget)

                            break
                    else:
                        # season is not preexisting in target widget
                        qa2_util.debug("Creating new season item", level=0)
                        self.series_data_handler.series_data[new_tvdb_id][season] = {
                            this_regex:
                                self.series_data_handler.series_data[old_tvdb_id][season].pop(this_regex)
                        }

                        new_season_item = create_season_item(new_tvdb_item, season)
                        old_season_item.removeChild(selected_widget)
                        new_season_item.addChild(selected_widget)

                    # clean up empty tvdb id entries in our json data
                    try:
                        if not self.series_data_handler.series_data[old_tvdb_id][season]:
                            qa2_util.debug("Removing empty dictionary entry for Season", season, "of TVDB ID", old_tvdb_id, level=1)
                            del self.series_data_handler.series_data[old_tvdb_id][season]
                    except KeyError:
                        pass
                    break
            else:
                # New tvdb id is not preexisting, so no merge needed.
                new_tvdb_id_item = create_tvdb_id_item(new_tvdb_id, text)
                new_season_item = create_season_item(new_tvdb_id_item, season)

                old_season_item.removeChild(selected_widget)
                new_season_item.addChild(selected_widget)
                new_tvdb_id_item.addChild(new_season_item)
                self.ui.tree_patterns.addTopLevelItem(new_tvdb_id_item)

                self.series_data_handler.series_data[new_tvdb_id] = {
                    season: {
                        selected_widget.data(0, self.ItemDataRole.DATA):
                            self.series_data_handler.series_data[old_tvdb_id][season].pop(this_regex)
                    }
                }

            if old_season_item.childCount() <= 0:
                old_tvdb_id_item.removeChild(old_season_item)

            if old_tvdb_id_item.childCount() <= 0:
                self.ui.tree_patterns.takeTopLevelItem(
                    self.ui.tree_patterns.indexOfTopLevelItem(old_tvdb_id_item))

            # clean up empty tvdb id entries in our json data
            try:
                if not self.series_data_handler.series_data[old_tvdb_id]:
                    qa2_util.debug("Removing empty dictionary entry for TVDB ID", old_tvdb_id, level=1)
                    del self.series_data_handler.series_data[old_tvdb_id]
            except KeyError:
                pass
        else:
            return  # TODO ERROR

        self.ui.button_revert.setEnabled(True)
        self.ui.button_save.setEnabled(True)

    @Slot()
    def update_data_season(self):
        if len(self.ui.tree_patterns.selectedItems()) != 1:
            return
        qa2_util.debug("update_data_season() called", level=1)
        selected_widget = self.ui.tree_patterns.selectedItems()[0]
        new_season = self.ui.line_season.text()
        text = format_season_text(new_season)

        # SERIES Item
        if selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SERIES:
            return  # TODO ERROR
        # SEASON item
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SEASON:
            tvdb_item = selected_widget.parent()
            tvdb_id = tvdb_item.data(0, self.ItemDataRole.DATA)
            old_season_item = selected_widget
            old_season = old_season_item.data(0, self.ItemDataRole.DATA)
            if new_season == old_season:
                return

            for y in range(tvdb_item.childCount()):
                new_season_item = tvdb_item.child(y)
                if new_season == new_season_item.data(0, self.ItemDataRole.DATA):
                    # same season
                    qa2_util.debug("Season", new_season,
                                   "found in both data sets. Merging these sub-dictionaries:", "\n",
                                   self.series_data_handler.series_data[tvdb_id][old_season], "\n",
                                   self.series_data_handler.series_data[tvdb_id][new_season],
                                   level=1)

                    self.series_data_handler.series_data[tvdb_id][new_season] = \
                        {**self.series_data_handler.series_data[tvdb_id][new_season],
                         **self.series_data_handler.series_data[tvdb_id].pop(old_season)}

                    qa2_util.debug("Result:", self.series_data_handler.series_data[tvdb_id][new_season],
                                   level=1)

                    pattern_items1 = selected_widget.takeChildren()
                    pattern_items2 = new_season_item.takeChildren()

                    non_duplicates = [item2 for item2 in pattern_items2 if
                                      item2.data(0, self.ItemDataRole.DATA) not in
                                      [item1.data(0, self.ItemDataRole.DATA) for item1 in pattern_items1]]

                    new_season_item.addChildren(pattern_items1 + non_duplicates)

                    tvdb_item.removeChild(selected_widget)
                    break
            else:
                # season is not preexisting in target widget
                self.series_data_handler.series_data[tvdb_id][new_season] = \
                    self.series_data_handler.series_data[tvdb_id].pop(old_season)

                selected_widget.setData(0, PatternSelector.ItemDataRole.DATA, new_season)
                selected_widget.setText(0, text)

            # clean up empty entry in our json data
            try:
                if not self.series_data_handler.series_data[tvdb_id][old_season]:
                    qa2_util.debug("Removing empty dictionary entry for Season", old_season, "of TVDB ID", tvdb_id,
                                   level=1)
                    del self.series_data_handler.series_data[tvdb_id][old_season]
            except KeyError:
                pass

        # PATTERN_SET item
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.PATTERN_SET:
            old_season_item = selected_widget.parent()
            old_season = old_season_item.data(0, self.ItemDataRole.DATA)
            tvdb_item = old_season_item.parent()
            tvdb_id = tvdb_item.data(0, self.ItemDataRole.DATA)
            if new_season == old_season:
                return

            this_regex = selected_widget.data(0, self.ItemDataRole.DATA)

            for y in range(tvdb_item.childCount()):
                new_season_item = tvdb_item.child(y)
                if new_season == new_season_item.data(0, self.ItemDataRole.DATA):
                    # same season
                    qa2_util.debug("Season", new_season,
                                   "found in both data sets. Merging these sub-dictionaries:", "\n",
                                   self.series_data_handler.series_data[tvdb_id][old_season], "\n",
                                   self.series_data_handler.series_data[tvdb_id][new_season],
                                   level=1)

                    self.series_data_handler.series_data[tvdb_id][new_season][this_regex] = \
                        self.series_data_handler.series_data[tvdb_id][old_season].pop(this_regex)

                    qa2_util.debug("Result:", self.series_data_handler.series_data[tvdb_id][new_season],
                                   level=1)

                    pattern_items2 = new_season_item.takeChildren()

                    non_duplicates = [item2 for item2 in pattern_items2 if
                                      item2.data(0, self.ItemDataRole.DATA) != this_regex]

                    new_season_item.addChildren(non_duplicates)
                    old_season_item.removeChild(selected_widget)
                    new_season_item.addChild(selected_widget)

                    break
            else:
                # season is not preexisting in target widget
                qa2_util.debug("Creating new season item", level=0)
                self.series_data_handler.series_data[tvdb_id][new_season] = {
                    this_regex:
                        self.series_data_handler.series_data[tvdb_id][old_season].pop(this_regex)
                }

                new_season_item = create_season_item(tvdb_item, new_season)
                old_season_item.removeChild(selected_widget)
                new_season_item.addChild(selected_widget)

            if old_season_item.childCount() <= 0:
                tvdb_item.removeChild(old_season_item)

            # clean up empty entry in our json data
            try:
                if not self.series_data_handler.series_data[tvdb_id][old_season]:
                    qa2_util.debug("Removing empty dictionary entry for Season", old_season, "of TVDB ID", tvdb_id,
                                   level=1)
                    del self.series_data_handler.series_data[tvdb_id][old_season]
            except KeyError:
                pass

        else:
            return  # TODO ERROR


        self.ui.button_revert.setEnabled(True)
        self.ui.button_save.setEnabled(True)

    @Slot()
    def update_data_pattern_set(self):
        if len(self.ui.tree_patterns.selectedItems()) != 1:
            return
        qa2_util.debug("update_data_pattern_set() called", level=1)
        selected_widget = self.ui.tree_patterns.selectedItems()[0]
        new_pattern_regex = self.ui.line_regex.text()
        new_pattern_target = self.ui.line_target.text()

        # SERIES Item
        if selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SERIES:
            return  # TODO ERROR
        # SEASON item
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.SEASON:
            return  # TODO ERROR
        # PATTERN_SET item
        elif selected_widget.data(0, self.ItemDataRole.DATA_NAME) == self.ItemType.PATTERN_SET:
            pattern_item = selected_widget
            old_pattern_regex = pattern_item.data(0, self.ItemDataRole.DATA)
            old_pattern_target = pattern_item.data(1, self.ItemDataRole.DATA)
            season_item = selected_widget.parent()
            season = season_item.data(0, self.ItemDataRole.DATA)
            tvdb_item = season_item.parent()
            tvdb_id = tvdb_item.data(0, self.ItemDataRole.DATA)

            if new_pattern_regex != old_pattern_regex:
                self.series_data_handler.series_data[tvdb_id][season][new_pattern_regex] = \
                    self.series_data_handler.series_data[tvdb_id][season].pop(old_pattern_regex)
                pattern_item.setData(0, PatternSelector.ItemDataRole.DATA, new_pattern_regex)
                pattern_item.setText(0, pattern_item.data(0, PatternSelector.ItemDataRole.DATA))
            elif new_pattern_target != old_pattern_target:
                self.series_data_handler.series_data[tvdb_id][season][old_pattern_regex] = new_pattern_target
                pattern_item.setData(1, PatternSelector.ItemDataRole.DATA, new_pattern_target)
                pattern_item.setText(1, pattern_item.data(1, PatternSelector.ItemDataRole.DATA))
            else:
                return
        else:
            return  # TODO ERROR

        self.ui.button_revert.setEnabled(True)
        self.ui.button_save.setEnabled(True)