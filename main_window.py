import requests
import json
import os
import subprocess
import re  # regex
import psutil
import time
import sys

from PySide2.QtCore import QTimer, Qt, Slot, QThreadPool
from PySide2.QtWidgets import QApplication, QMainWindow, QProgressBar, QDialog, QTableWidgetItem, QHeaderView
from qAnime2 import FileFetcher
from qa2_tvdb import TVDBHandler

from ui_main_window import Ui_MainWindow
from ui_setup_dialog import Ui_setup_dialog
from ui_boolean_dialog import Ui_bool_dialog

from structure.torrent import Torrent, File, Episode

# TODO:
# Input Evaluations
# rework editing/deleting
# same patternA may not be in two seasons

# 0 = No debug output
# 1 = small stuff?
# 2 = full json data dumps
DEBUG_OUTPUT_LEVEL = 2

SERIES_DATA_FILE = "./data.json"
SETTINGS_FILE = "./settings.json"
os.makedirs(os.path.dirname(SERIES_DATA_FILE), exist_ok=True)
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

        self.ui.table.insertColumn(0)
        self.ui.table.insertColumn(1)
        self.ui.table.setHorizontalHeaderItem(0, QTableWidgetItem("Old File"))
        self.ui.table.setHorizontalHeaderItem(1, QTableWidgetItem("New File"))
        self.ui.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.progress_bar = QProgressBar(self.ui.statusbar)
        self.progress_bar.setAlignment(Qt.AlignRight)
        self.progress_bar.setMaximumSize(180, 19)
        self.ui.statusbar.addPermanentWidget(self.progress_bar)
        self.ui.button_scan.clicked.connect(self.rename_scan)

        self.settings = {}

    @Slot(int)
    @Slot(int, int)
    def set_progress_bar(self, progress, maximum=None):
        if isinstance(maximum, int):
            self.progress_bar.setMaximum(maximum)
        if isinstance(progress, int):
            self.progress_bar.setValue(progress)

    @Slot(tuple)
    def append_rename_data(self, data):
        absolute_filename_old = None
        absolute_filename_new = None
        if isinstance(data, tuple) and len(data) == 4 \
                and isinstance(data[0], str) and isinstance(data[1], str) \
                and isinstance(data[2], str) and isinstance(data[3], str):
            # absolute_filename_old = '\\'.join(filter(None, [data[0], data[1], data[2]]))
            # absolute_filename_new = '\\'.join(filter(None, [data[0], data[1], data[3]]))
            absolute_filename_old = '\\'.join(filter(None, [data[1], data[2]]))
            absolute_filename_new = '\\'.join(filter(None, [data[1], data[3]]))
        else:
            print("Unexpected data. Got '" + str(data) + "' (" + str(type(data)) + ")")

        # append file paths to table
        row = self.ui.table.rowCount()
        self.ui.table.insertRow(row)
        self.ui.table.setItem(row, 0, QTableWidgetItem(absolute_filename_old))
        self.ui.table.setItem(row, 1, QTableWidgetItem(absolute_filename_new))
        print("Appended to table: " + self.ui.table.item(row, 0).text() + " and " + self.ui.table.item(row, 1).text())

    def rename_scan(self):
        self.file_fetcher = FileFetcher(self.settings)
        self.file_fetcher.qbt_handler.init_progress.connect(self.set_progress_bar)
        self.file_fetcher.qbt_handler.update_progress.connect(self.set_progress_bar)
        self.file_fetcher.signals.rename_scan_result.connect(self.append_rename_data)
        self.file_fetcher.start()

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

        # tvdb_auth()
        # qbt_auth()

        # qbt_version_cur = get_qbt_version()
        # if self.settings["qbt_version"] != qbt_version_cur:
        #     if not input_bool(f"WARNING: QBittorrent version mismatch: Got \"{qbt_version_cur}\", expected \"{settings['qbt_version']}\". Compatibility is not ensured. \nContinue?\n>>"):
        #         print("Exiting.")
        #         return
        #     else:
        #         if input_bool(f"If you're sure version {qbt_version_cur} is supported we can remember it as safe so you won't be warned again.\nDo it?\n>>"):
        #             settings["qbt_version"] = qbt_version_cur
        #             with open(SETTINGS_FILE, 'w') as f:
        #                 dump = json.dumps(settings, indent=4, sort_keys=False)
        #                 f.write(dump)

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
