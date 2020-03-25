import os
import re  # regex
import subprocess
from enum import IntEnum

import psutil
from PySide2.QtCore import QThread, Signal, QObject, QEventLoop, Slot
from PySide2.QtWidgets import QMessageBox

import qa2_util
from Fastresume import Fastresume
from QTorrentWidgets import QTorrentTreeWidget
from SeriesDataHandler import SeriesDataHandler
from dialog.QWaitingDialog import QWaitingDialog
from qa2_qbt import QBTHandler
from qa2_tvdb import TVDBHandler
from structure.torrent import Torrent


class RenameWorker(QObject):
    rename_finished = Signal()
    track_progress_text = Signal(str)
    track_progress_update = Signal(int)
    track_progress_range = Signal(int, int)
    track_progress_start = Signal()

    def __init__(self, settings):
        super(RenameWorker, self).__init__()
        self.settings = settings

    def rename(self, torrent_tree:QTorrentTreeWidget):
        """
        Renames a QTorrentTreeWidget's torrents and their files and manipulates the QBittorrent fastresume file accordingly.
        """
        if not isinstance(torrent_tree, QTorrentTreeWidget):
            return  # TODO ERROR
        else:
            process = None
            for p in psutil.process_iter():  # find QBittorrent process
                try:
                    if self.settings["qbt_client"] in p.exe():
                        process = p
                        break  # assuming only one running QBittorrent process here. whatever.
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            # On Windows, Process.terminate() doesn't terminate the process peacefully, it just kills it right away like Process.kill()
            subprocess.call("taskkill /im  {}".format(self.settings["qbt_client"].split('\\')[-1]),
                            stdout=open(os.devnull, 'w'), shell=False)
            # process.terminate()
            print("Waiting for QBittorrent to terminate...")
            if process is not None:
                process.wait(60)
                print("QBittorrent has been terminated.")
            else:
                print("No running QBittorrent process found. Assuming it has been terminated.")

            progress_maximum = torrent_tree.topLevelItemCount()
            progress_interval = int(progress_maximum / 100) if progress_maximum >= 100 else 1
            self.track_progress_text.emit("Renaming...")
            self.track_progress_range.emit(0, progress_maximum)
            self.track_progress_start.emit()

            for progress_index in range(progress_maximum):
                torrent_widget = torrent_tree.topLevelItem(progress_index)

                fastresume_file = os.path.expandvars("%LOCALAPPDATA%/qBittorrent/BT_backup/") + torrent_widget.torrent.hash + ".fastresume"
                with open(fastresume_file, 'rb') as f:
                    fr = f.read()
                fastresume = Fastresume(fr)
                if torrent_widget.checked:
                    fastresume.rename_torrent(torrent_widget.torrent.name_new)
                    torrent_widget.previous_name = torrent_widget.torrent.name  # backup for a possibly needed rollback
                    torrent_widget.setName(torrent_widget.torrent.name_new)

                for j in range(torrent_widget.childCount()):
                    file_widget = torrent_widget.child(j)
                    if not file_widget.checked:
                        continue
                    old_filename_relative = file_widget.file.getRelativeFilename()
                    file_widget.file.filename_new = qa2_util.clean_filename(file_widget.file.filename_new)
                    new_filename_relative = file_widget.file.getRelativeFilename(file_widget.file.filename_new)

                    qa2_util.debug("Renaming", old_filename_relative, "to", new_filename_relative, level=2)
                    fastresume.rename_file(old_filename_relative, new_filename_relative)
                    try:
                        os.rename('\\'.join(filter(None, [torrent_widget.torrent.save_path, old_filename_relative])),
                                  '\\'.join(filter(None, [torrent_widget.torrent.save_path, file_widget.file.subpath, file_widget.file.filename_new])))
                        file_widget.previous_name = file_widget.file.filename                   # backup for a possibly needed rollback
                        file_widget.setName(file_widget.file.filename_new)                      # update current name in GUI

                        print(f"Renamed {old_filename_relative} to {new_filename_relative}.")
                    except OSError as e:
                        print(e.strerror)
                        print('\\'.join(filter(None, [torrent_widget.torrent.save_path, old_filename_relative])))
                        fastresume.rename_file(new_filename_relative, old_filename_relative)
                        print("File renaming failed. No changes are being made.")
                        break
                try:
                    with open(fastresume_file, 'wb') as f:
                        f.write(fastresume.write())
                    print("QBittorrent files have been manipulated accordingly.")
                except OSError as e:
                    print(e.strerror)
                    print("Failed to manipulate QBittorrent fastresume file. Reverting renames...")
                    torrent_widget.revertName()
                    for j in range(torrent_widget.childCount()):
                        file_widget = torrent_widget.child(torrent_widget.childCount()-1-j)
                        if not file_widget.checked:
                            continue
                        old_filename_relative = file_widget.file.getRelativeFilename()
                        new_filename_relative = file_widget.file.getRelativeFilename(file_widget.previous_name)

                        fastresume.rename_file(new_filename_relative, old_filename_relative)

                        try:
                            os.rename(
                                '\\'.join(filter(None, [torrent_widget.torrent.save_path, file_widget.file.subpath,
                                                        file_widget.file.filename])),
                                '\\'.join(filter(None, [torrent_widget.torrent.save_path, file_widget.file.subpath,
                                                        file_widget.previous_name])))
                            file_widget.revertName()
                            print(f"Reverted {new_filename_relative} to {old_filename_relative}.")
                        except OSError as e:
                            print(e.strerror)
                            print("Rename revert failed. Fix it yourself! ¯\\_(ツ)_/¯")
                            break
                if progress_index % progress_interval == 0 or progress_index+progress_interval >= progress_maximum:
                    self.track_progress_update.emit(progress_index+progress_interval)
            print("Restarting QBittorrent...")
            subprocess.Popen(self.settings["qbt_client"], close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
            print("Restarted!")

        # noinspection PyUnresolvedReferences
        self.rename_finished.emit()


class FileFetcher(QObject):
    wait_for = Signal(int, str)
    failed = Signal(int)
    succeeded = Signal(int)
    authenticating = Signal()
    auth_done = Signal()

    track_progress_text = Signal(str)
    track_progress_update = Signal(int)
    track_progress_range = Signal(int, int)
    track_progress_start = Signal()
    rename_scan_result = Signal(Torrent)
    rename_scan_finished = Signal()

    class Condition(IntEnum):
        QBT_AUTH = 0
        TVDB_AUTH = 1

    def __init__(self, settings):
        super(FileFetcher, self).__init__()
        self.settings = settings
        self.series_data = {}
        self.torrents = {}
        self.series_data_handler = SeriesDataHandler()

        self.auth_state = 0
        self.loop = QEventLoop()
        self.auth_done.connect(self.loop.quit)
        self.thread_tvdb_auth = QThread()
        self.thread_qbt_auth = QThread()
        self.qbt_handler = QBTHandler(self.settings)
        self.qbt_handler.moveToThread(self.thread_qbt_auth)
        self.thread_qbt_auth.started.connect(self.qbt_handler.auth)
        self.qbt_handler.auth_success.connect(self.qbt_authentication_success)
        self.qbt_handler.auth_failure.connect(self.qbt_authentication_failure)
        self.qbt_handler.auth_success.connect(self.thread_qbt_auth.quit)
        self.qbt_handler.auth_failure.connect(self.thread_qbt_auth.quit)

        self.tvdb_handler = TVDBHandler(self.settings)
        self.tvdb_handler.moveToThread(self.thread_tvdb_auth)
        self.thread_tvdb_auth.started.connect(self.tvdb_handler.auth)
        self.tvdb_handler.auth_success.connect(self.tvdb_authentication_success)
        self.tvdb_handler.auth_failure.connect(self.tvdb_authentication_failure)
        self.tvdb_handler.auth_success.connect(self.thread_tvdb_auth.quit)
        self.tvdb_handler.auth_failure.connect(self.thread_tvdb_auth.quit)

    @Slot()
    def qbt_authentication_success(self):
        print("qbt_authentication_success")
        self.succeeded.emit(self.Condition.QBT_AUTH)
        self.auth_state += 1
        if not (self.thread_qbt_auth.isRunning() or self.thread_tvdb_auth.isRunning()):
            print("auth finished by qbt_authentication_success")
            self.auth_done.emit()

    @Slot()
    def qbt_authentication_failure(self):
        # self.qbt_handler.auth_finished.disconnect(self.notify_qbt_auth_response)
        print("qbt_authentication_failure")
        self.failed.emit(self.Condition.QBT_AUTH)
        self.qbt_handler = None
        notification = QMessageBox()
        notification.setText("Failed connecting to QBittorrent WebAPI.")
        notification.setInformativeText("Make sure QBittorrent is running and its Web UI is enabled.")
        notification.setStandardButtons(QMessageBox.Ok)
        notification.setDefaultButton(QMessageBox.Ok)
        notification.setIcon(QMessageBox.Critical)
        notification.exec_()
        if not (self.thread_qbt_auth.isRunning() or self.thread_tvdb_auth.isRunning()):
            self.auth_done.emit()

    @Slot()
    def tvdb_authentication_success(self):
        print("tvdb_authentication_success")
        self.succeeded.emit(self.Condition.TVDB_AUTH)
        self.auth_state += 1
        if not (self.thread_qbt_auth.isRunning() or self.thread_tvdb_auth.isRunning()):
            print("auth finished by tvdb_authentication_success")
            self.auth_done.emit()

    @Slot(int, str)
    def tvdb_authentication_failure(self, response_code=None, details=None):
        # self.tvdb_handler.auth_finished.disconnect(self.notify_tvdb_auth_response)
        print("tvdb_authentication_failure")
        self.failed.emit(self.Condition.TVDB_AUTH)
        self.tvdb_handler = None
        notification = QMessageBox()
        notification.setText("Failed to authenticate with TheTVDB.com.")
        if response_code is not None and details is not None:
            notification.setDetailedText("Response Code: " + str(response_code) + "\n\n" + details)
        notification.setInformativeText("Renaming won't be available.")
        notification.setStandardButtons(QMessageBox.Ok)
        notification.setDefaultButton(QMessageBox.Ok)
        notification.setIcon(QMessageBox.Critical)
        notification.exec_()
        if not (self.thread_qbt_auth.isRunning() or self.thread_tvdb_auth.isRunning()):
            self.auth_done.emit()

    def is_authenticated(self):
        return self.auth_state == len(self.Condition)

    def auth(self):
        if not self.is_authenticated():
            self.wait_for.emit(self.Condition.QBT_AUTH, "Connecting to QBittorrent WebUI.")
            self.wait_for.emit(self.Condition.TVDB_AUTH, "Connecting to TVDB.")
            self.authenticating.emit()

            self.thread_tvdb_auth.start()
            self.thread_qbt_auth.start()

            if self.thread_qbt_auth.isRunning() or self.thread_tvdb_auth.isRunning():
                print("authing")
                self.loop.exec_()
            print("auth done")
        return self.is_authenticated()

    def scan(self):
        if not self.auth():
            print("bruh")
            return  # TODO ERROR
        self.qbt_handler.track_progress_text.connect(self.track_progress_text)
        self.qbt_handler.track_progress_range.connect(self.track_progress_range)
        self.qbt_handler.track_progress_update.connect(self.track_progress_update)
        self.qbt_handler.track_progress_start.connect(self.track_progress_start)

        self.series_data_handler.read()
        print(self.series_data_handler.series_data)
        self.torrents = self.qbt_handler.fetch_torrents()
        self.action_rename_scan()
        self.rename_scan_finished.emit()

    def action_rename_scan(self):
        # check all files by regex in our series data
        progress_index = 0
        progress_maximum = len(self.torrents)
        progress_interval = int(progress_maximum / 100) if progress_maximum >= 100 else 1
        self.track_progress_text.emit("Scanning for matching regex patterns...")
        self.track_progress_range.emit(progress_index, progress_maximum)   # should still be set correctly at this point so this seems unnecessary, just being save
        self.track_progress_start.emit()
        for torrent_info in self.torrents:
            qa2_util.debug("Files:", [x.filename for x in torrent_info.files], level=2)
            irrelevant = True
            for file_info in torrent_info.files:
                if file_info.priority == 0:  # skip ignored files
                    continue
                qa2_util.debug("Checking filename:", file_info.filename, level=2)
                for tvdb_id, data in self.series_data_handler.series_data.items():
                    for season, patterns in data.items():
                        for patternA, patternB in patterns.items():
                            pattern = re.compile(patternA)
                            if pattern.match(file_info.filename):
                                qa2_util.debug("Matched:", file_info.filename, level=2)
                                file_info.filename_new = self.pattern_wizard(tvdb_id, season, patternA, patternB, file_info.filename)
                                irrelevant = False
            if not irrelevant:
                self.rename_scan_result.emit(torrent_info)
            progress_index += 1
            if progress_index % progress_interval == 0 or progress_index >= progress_maximum:
                self.track_progress_update.emit(progress_index)
        return

    def pattern_wizard(self, tvdb_id, season, pattern_a, pattern_b, filename):
        pattern = re.compile(pattern_a)
        if pattern.match(filename):
            episode_number = re.search(pattern_a, filename).group(1)
            episode_json_data = self.tvdb_handler.get_single_episode(tvdb_id, season, episode_number)
            season_number = episode_json_data['airedSeason']
            episode_number = episode_json_data['airedEpisodeNumber']
            absolute_number = episode_json_data['absoluteNumber']
            title = episode_json_data['episodeName']
            filename_new = pattern_b

            while r"\S" in filename_new:
                filename_new = self.pattern_replace(filename_new, r"\S", season_number, True)
            while r"\E" in filename_new:
                filename_new = self.pattern_replace(filename_new, r"\E", episode_number, True)
            while r"\A" in filename_new:
                filename_new = self.pattern_replace(filename_new, r"\A", absolute_number, True)
            while r"\T" in filename_new:
                filename_new = self.pattern_replace(filename_new, r"\T", title, False)
            return qa2_util.clean_filename(filename_new)

    @staticmethod
    def pattern_replace(pattern, old, new, fill=False):
        idx = pattern.find(old)
        if idx >= 0:
            count = 1
            lookahead = len(old)
            while pattern[idx + lookahead:idx + lookahead + len(old)] == old:
                count += 1
                lookahead += len(old)
            if fill:
                new = str(new).zfill(count)
            pattern = pattern[:idx] + new + pattern[idx + len(old) * count:]
        return pattern
