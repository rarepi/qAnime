import json
import os
import sys

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QApplication, QMainWindow, QProgressBar, QDialog, QHeaderView, \
    QTreeWidgetItem

import qAnime2
from QTorrentWidgets import QTorrentTreeWidget
from SeriesDataHandler import SeriesDataHandler
from dialog.SeriesSelection import SeriesSelection
from dialog.PatternEditor import PatternEditor
from dialog.RegexBuilder import RegexBuilder
from qAnime2 import RenameWorker, FileFetcher
from structure.torrent import Torrent
from ui.ui_boolean_dialog import Ui_bool_dialog
from ui.ui_main_window import Ui_MainWindow
from ui.ui_setup_dialog import Ui_setup_dialog

# TODO:
# same patternA may not be in two seasons

SETTINGS_FILE = "./settings.json"
os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)


class SetupDialog(QDialog):
    def __init__(self):
        super(SetupDialog, self).__init__()
        self.ui = Ui_setup_dialog()
        self.ui.setupUi(self)


class BooleanDialog(QDialog):
    def __init__(self):
        super(BooleanDialog, self).__init__()
        self.ui = Ui_bool_dialog()
        self.ui.setupUi(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.file_fetcher = None
        self.rename_worker = None

        self.series_selection = None  # need settings for tvdb auth
        self.regex_builder = None
        self.PatternEditor = None

        # TODO use "Promote Widget" in Qt Designer instead
        # Ugly workaround. Python doesn't allow casting the Qt Designer's QTreeWidget to QTorrentTreeWidget, so we have to rebuild it.
        old_tree_torrents = self.ui.tree_torrents
        self.ui.tree_torrents = QTorrentTreeWidget(self.ui.central_widget)
        self.ui.vlayout_table.replaceWidget(old_tree_torrents, self.ui.tree_torrents)
        old_tree_torrents.deleteLater()

        self.ui.tree_torrents.setColumnCount(3)
        header = QTreeWidgetItem()
        header.setText(0, "Old Name")
        header.setText(1, "New Name")
        header.setText(2, "")
        self.ui.tree_torrents.setHeaderItem(header)
        self.ui.tree_torrents.setColumnCount(3)
        self.ui.tree_torrents.header().setStretchLastSection(False)
        self.ui.tree_torrents.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.tree_torrents.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.tree_torrents.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ui.tree_torrents.header().setDefaultAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar(self.ui.statusbar)
        self.progress_bar.setAlignment(Qt.AlignRight)
        self.progress_bar.setMaximumSize(180, 19)
        self.ui.statusbar.addPermanentWidget(self.progress_bar)
        self.ui.button_scan.clicked.connect(self.rename_scan)
        self.ui.button_add.clicked.connect(self.open_series_selection)
        self.ui.button_confirm_rename.clicked.connect(self.rename_confirm)

        self.settings = {}

    @Slot(int)
    @Slot(int, int)
    def set_progress_bar(self, progress, maximum=None):
        if isinstance(maximum, int):
            self.progress_bar.setMaximum(maximum)
        if isinstance(progress, int):
            self.progress_bar.setValue(progress)

    @Slot(Torrent)
    def append_rename_data(self, torrent):
        self.ui.tree_torrents.add_torrent(torrent)

    def rename_scan(self):
        self.file_fetcher = FileFetcher(self.settings)
        self.file_fetcher.qbt_handler.init_progress.connect(self.set_progress_bar)
        self.file_fetcher.qbt_handler.update_progress.connect(self.set_progress_bar)
        self.file_fetcher.signals.rename_scan_result.connect(self.append_rename_data)
        self.file_fetcher.start()

    def rename_confirm(self):
        self.ui.button_confirm_rename.setEnabled(False)
        self.ui.tree_torrents.setEnabled(False)
        self.rename_worker = RenameWorker(self.settings)
        self.rename_worker.signals.rename_finished.connect(self.rename_finished)
        self.rename_worker.torrent_tree = self.ui.tree_torrents
        self.rename_worker.start()

    @Slot()
    def open_series_selection(self):
        self.series_selection = SeriesSelection(self.settings)
        self.series_selection.done.connect(self.open_regex_builder)
        self.series_selection.show()

    @Slot()
    def open_regex_builder(self):
        self.series_selection.hide()
        self.regex_builder = RegexBuilder()
        self.regex_builder.done.connect(self.open_pattern_editor)
        self.regex_builder.show()

    @Slot(str)
    def open_pattern_editor(self, regex):
        self.regex_builder.hide()
        self.PatternEditor = PatternEditor()
        self.PatternEditor.done.connect(self.finalize_pattern_data)
        self.PatternEditor.setText(regex)
        self.PatternEditor.show()

    @Slot(str, str)
    def finalize_pattern_data(self, regex, target):
        self.PatternEditor.hide()
        tvdb_id = self.series_selection.selected_tvdb_id
        season = self.series_selection.selected_season
        regex_pattern = regex
        target_pattern = target

        series_data_handler = SeriesDataHandler()
        series_data_handler.read()
        series_data_handler.add(tvdb_id, season, regex_pattern, target_pattern)
        series_data_handler.write()

    @Slot()
    def rename_finished(self):
        self.ui.tree_torrents.setEnabled(True)
        self.ui.button_confirm_rename.setEnabled(True)

    def startup(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            file = open(SETTINGS_FILE, 'w')
        except json.decoder.JSONDecodeError:
            if not os.stat(SETTINGS_FILE).st_size == 0:
                print("Failed to read settings file. Check \"" + os.path.abspath(SETTINGS_FILE) + "\".")
                quit()
        if len(self.settings) == 0:
            self.setup()
        else:
            self.show()

    def setup(self):
        dialog = SetupDialog()

        def confirm():
            self.settings["qbt_version"] = "v4.1.9.1"
            self.settings["qbt_client"] = dialog.ui.ledit_absolute_path.text()
            self.settings["qbt_username"] = dialog.ui.ledit_qbt_user.text()
            self.settings["qbt_password"] = dialog.ui.ledit_qbt_password.text()
            self.settings["qbt_url"] = dialog.ui.ledit_qbt_url.text()
            self.settings["tvdb_url"] = dialog.ui.ledit_tvdb_url.text()
            self.settings["tvdb_apikey"] = dialog.ui.ledit_tvdb_key.text()

            with open(SETTINGS_FILE, 'w') as f:
                dump = json.dumps(self.settings, indent=4, sort_keys=False)
                f.write(dump)
            dialog.close()
            self.show()

        dialog.ui.btn_confirm.clicked.connect(confirm)
        dialog.show()

        # print("\nHello there! Running first time setup. To edit these settings in the future check out the settings.json file located next to the executable.\n")
        # settings["qbt_version"] = "v4.1.6"
        # # TODO: Read the client location from Registry, possibly "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\qBittorrent\InstallLocation", and then offer that as the default option.
        # # https://docs.python.org/3.7/library/winreg.html?highlight=winreg
        # settings["qbt_client"] = input("Enter the absolute path for the QBittorrent executable.\nExample: C:\\Program Files\\qBittorrent\\qbittorrent.exe\n>>")
        # settings["qbt_username"] = input("Enter your login name for QBittorrent Web UI.\n>>")
        # settings["qbt_password"] = input("Enter your login password for QBittorrent Web UI.\n>>")
        # settings["qbt_url"] = input("Enter the URL to your QBittorrent Web API. (Keep empty for default)\nDefault: http://localhost:8080/api/v2\n>>")
        # if len(settings["qbt_url"]) == 0:
        #     settings["qbt_url"] = "http://localhost:8080/api/v2"
        # settings["tvdb_url"] = input("Enter the URL to the TheTVDB.com API. (Keep empty for default)\nDefault: https://api.thetvdb.com\n>>")
        # if len(settings["tvdb_url"]) == 0:
        #     settings["tvdb_url"] = "https://api.thetvdb.com"
        # # settings["tvdb_apikey"] = input("Enter your API Key for the TheTVDB.com API. (Keep empty for default)\n >>")
        # settings["tvdb_apikey"] = "2323B61F3A9DA8C8"


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    window.startup()

    sys.exit(app.exec_())

    #     with open(SERIES_DATA_FILE, 'w') as f:
    #         dump = json.dumps(series_data, indent=4, sort_keys=True)
    #         f.write(dump)


main()
