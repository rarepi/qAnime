import json
import os
import sys

from PySide2.QtCore import Qt, Slot, QThread
from PySide2.QtWidgets import QApplication, QMainWindow, QProgressBar, QDialog, QHeaderView, \
    QTreeWidgetItem, QProgressDialog

import qAnime2
from QTorrentWidgets import QTorrentTreeWidget
from SeriesDataHandler import SeriesDataHandler
from dialog.SeriesDataEditor import PatternSelector
from dialog.SeriesSelection import SeriesSelection
from dialog.PatternEditor import PatternEditor
from dialog.RegexBuilder import RegexBuilder
from dialog.QWaitingDialog import QWaitingDialog
from qAnime2 import RenameWorker, FileFetcher
from structure.torrent import Torrent
from ui.ui_boolean_dialog import Ui_bool_dialog
from ui.ui_main_window import Ui_MainWindow
from ui.ui_setup_dialog import Ui_setup_dialog

SETTINGS_FILE = "./settings.json"

QBT_VERSION = "v4.2.1"  # TODO check for this
TVDB_CACHE_FILE = "./cache.json"
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

        # load settings and shit
        self.startup()

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

        # buttons
        self.ui.button_scan.clicked.connect(self.rename_scan)
        self.ui.button_add.clicked.connect(self.open_series_selection)
        self.ui.button_edit.clicked.connect(self.open_pattern_selector)
        self.ui.button_confirm_rename.clicked.connect(self.rename_confirm)
        self.ui.button_confirm_rename.setEnabled(False)

        # series data json read/write
        self.series_data_handler = SeriesDataHandler()
        self.series_data_handler.read()

        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.reset()
        self.progress_dialog.setCancelButton(None)

        # QThread
        self.file_fetcher = FileFetcher(self.settings)
        self.thread_rename_scan = QThread()
        if self.file_fetcher.is_authenticated():
            self.file_fetcher.qbt_handler.track_progress_text.connect(self.progress_dialog.setLabelText)
            self.file_fetcher.qbt_handler.track_progress_range.connect(self.progress_dialog.setRange)
            self.file_fetcher.qbt_handler.track_progress_update.connect(self.progress_dialog.setValue)
            self.file_fetcher.qbt_handler.track_progress_start.connect(self.progress_dialog.open)
            self.file_fetcher.track_progress_text.connect(self.progress_dialog.setLabelText)
            self.file_fetcher.track_progress_range.connect(self.progress_dialog.setRange)
            self.file_fetcher.track_progress_update.connect(self.progress_dialog.setValue)
            self.file_fetcher.track_progress_start.connect(self.progress_dialog.open)
            self.file_fetcher.rename_scan_result.connect(self.append_rename_data)
            self.file_fetcher.rename_scan_finished.connect(self.enable_button_confirm_rename)
        else:
            self.ui.button_scan.setEnabled(False)
        # QThread
        self.rename_worker = RenameWorker(self.settings)
        self.thread_rename = QThread()
        self.rename_worker.track_progress_text.connect(self.progress_dialog.setLabelText)
        self.rename_worker.track_progress_range.connect(self.progress_dialog.setRange)
        self.rename_worker.track_progress_update.connect(self.progress_dialog.setValue)
        self.rename_worker.track_progress_start.connect(self.progress_dialog.open)
        self.rename_worker.rename_finished.connect(self.rename_finished)

        # dialogs
        self.series_selection = SeriesSelection(self.settings)
        self.series_selection.accepted.connect(self.open_regex_builder)
        self.regex_builder = RegexBuilder()
        self.regex_builder.accepted.connect(self.open_pattern_editor)
        self.PatternEditor = PatternEditor()
        self.PatternEditor.accepted.connect(self.finalize_pattern_data)
        self.patternSelector = PatternSelector(self.settings)

        # TODO why is this here?
        self.settings = {}

    @Slot(Torrent)
    def append_rename_data(self, torrent):
        self.ui.tree_torrents.add_torrent(torrent)

    @Slot()
    def enable_button_confirm_rename(self):
        if self.ui.tree_torrents.topLevelItemCount() > 0:
            self.ui.button_confirm_rename.setEnabled(True)

    def rename_scan(self):
        self.file_fetcher.moveToThread(self.thread_rename_scan)
        self.thread_rename_scan.started.connect(self.file_fetcher.scan)
        self.file_fetcher.rename_scan_finished.connect(self.thread_rename_scan.quit)
        self.thread_rename_scan.start()

    def rename_confirm(self):
        self.ui.button_confirm_rename.setEnabled(False)
        self.ui.tree_torrents.setEnabled(False)
        self.file_fetcher.moveToThread(self.thread_rename)
        self.thread_rename.started.connect(lambda: self.rename_worker.rename(self.ui.tree_torrents))
        self.file_fetcher.rename_scan_finished.connect(self.thread_rename.quit)
        self.thread_rename.start()

    @Slot()
    def open_series_selection(self):
        self.series_selection.show()

    @Slot()
    def open_regex_builder(self):
        self.regex_builder.show()

    @Slot()
    def open_pattern_editor(self):
        self.PatternEditor.setText(self.regex_builder.text)
        self.PatternEditor.show()

    @Slot()
    def open_pattern_selector(self):
        self.patternSelector.load()
        self.patternSelector.show()

    @Slot()
    def finalize_pattern_data(self):
        tvdb_id = self.series_selection.selected_tvdb_id
        season = self.series_selection.selected_season
        regex_pattern = self.PatternEditor.ui.text_edit_regex.toPlainText()
        target_pattern = self.PatternEditor.ui.text_edit_target.toPlainText()

        self.series_data_handler.add(tvdb_id, season, regex_pattern, target_pattern)
        self.series_data_handler.write()

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
            self.settings["qbt_version"] = QBT_VERSION
            self.settings["qbt_client"] = dialog.ui.ledit_absolute_path.text()
            self.settings["qbt_username"] = dialog.ui.ledit_qbt_user.text()
            self.settings["qbt_password"] = dialog.ui.ledit_qbt_password.text()
            self.settings["qbt_url"] = dialog.ui.ledit_qbt_url.text()
            self.settings["tvdb_url"] = dialog.ui.ledit_tvdb_url.text()
            self.settings["tvdb_apikey"] = dialog.ui.ledit_tvdb_key.text()

            self.settings["tvdb_cache"] = TVDB_CACHE_FILE

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

    sys.exit(app.exec_())

    #     with open(SERIES_DATA_FILE, 'w') as f:
    #         dump = json.dumps(series_data, indent=4, sort_keys=True)
    #         f.write(dump)


main()
