import requests
import json
import os
import subprocess
import re  # regex
import psutil
import time
import sys
from threading import Thread

from PySide2.QtCore import QThread, Signal, QTimer, Slot, QEventLoop, QObject, QRunnable
from qa2_qbt import QBTHandler
from qa2_tvdb import TVDBHandler

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


class TVDBEpisodeNumberNotInResult(Exception):
    """Raised when an episode number is not found in TVDB result"""
    pass


def debug(output, level):
    if DEBUG_OUTPUT_LEVEL >= level:
        print(output)


def qbt_tag_prefix(string):
    # todo check for type?
    string_b = bytes(string, "utf-8")
    length_str_b = bytes(str(len(string_b)), "utf-8")
    return length_str_b + b':' + string_b


def clean_filename(filename):
    illegal_characters = '\\"/:<>?|'
    rem_ill_chars = str.maketrans(illegal_characters, '_' * len(illegal_characters))
    return filename.translate(rem_ill_chars)


def metadata_wizard(tvdb_id, series_data):
    x_name = "Mob Psycho 100"
    x_pattern_a = r"^\[HorribleSubs\] Mob Psycho 100 - (\d\d) \[1080p\]\.mkv"
    x_pattern_b = r"Mob Psycho 100 - s\S\Se\E\E - [\A\A] \T - [2019 ENG-Sub AAC 1080p x264 - HorribleSubs].mkv"

    sdata = {}
    pattern_a = ""
    pattern_b = ""
    # add new entry
    if tvdb_id is -1:
        tvdb_series = {}
        while len(tvdb_series) == 0:
            name = input("Enter the name of the series.\nExample: " + x_name + "\n>> ")
            tvdb_series = tvdb_get_series(name)
        tvdb_id = tvdb_series[0]
        name = tvdb_series[1]

        if tvdb_id in series_data.keys():
            if not input_bool("Series ID " + tvdb_id + " already has an entry named \"" + series_data[tvdb_id]['name'] + "\". Add new pattern?\n>> "):
                return
            sdata = series_data[tvdb_id]
        else:
            sdata = {
                "name": name,
                "patterns": {
                }
            }
    # edit existing entry
    else:
        sdata = series_data[tvdb_id]

        pattern_set_options = {}
        i = 0
        for season, pattern_pairs in sdata['patterns'].items():
            for a, b in pattern_pairs.items():
                pattern_set_options[i] = (season, a)
                print(str(i) + ") " + a + " RENAMES TO " + b)
                i += 1
        while True:
            index = input_int("Choose the pattern set you want to replace by index.\n>> ")
            try:
                pattern_a = pattern_set_options[index][1]
                pattern_b = sdata['patterns'][pattern_set_options[index][0]][pattern_set_options[index][1]]
                print("Pattern set \"{} : {}\" has been removed.".format(pattern_set_options[index][1],
                                                                         sdata['patterns'][
                                                                             pattern_set_options[index][0]].pop(
                                                                             pattern_set_options[index][1])))
            except KeyError as e:
                print("Invalid input.")
                continue
            break

    pattern_a_rgx = re.compile(r".*\((?:\\d)+\).*")
    pattern_b_rgx = re.compile(r".*(?:(?:\\E)|(?:\\A))+.*")
    while True:
        if len(pattern_a) == 0:
            new = input(rf"Enter unique regex for detection. Provide a capture group for the episode number. (e. g. (\d\d))\nExample: {x_pattern_a}\n>> ")
        else:
            new = input(rf"Enter your new unique regex for detection. Provide a capture group for the episode number. (e. g. (\d\d))\nExample: {x_pattern_a}\nKeep empty to keep the current regex: {pattern_a}\n>> ")
            if len(new) == 0:
                new = pattern_a
        try:
            re.compile(new)
        except re.error as e:
            print("Invalid regex.", e)
            continue
        if not pattern_a_rgx.match(new):
            print("Your regex pattern is missing a capture group for episode numbers. Episodes naturally have to be extinguishable by their seasonal or absolute episode numbers.")
            continue
        pattern_a = new
        break
    while True:
        if len(pattern_b) == 0:
            new = input(fr"Enter target file name. You must provide a tag for either seasonal or absolute episode numbers.\nExample: {x_pattern_b}\nValid tags:\n\S - Season Number\n\E - Seasonal Episode Number\n\A - Absolute Episode Number\n\T - Season Title\n>> ")
        else:
            new = input(fr"Enter your new target file name. You must provide a tag for either seasonal or absolute episode numbers.\nExample: {x_pattern_b}\nValid tags:\n\S - Season Number\n\E - Seasonal Episode Number\n\A - Absolute Episode Number\n\T - Season Title\nKeep empty to keep the current pattern: " + pattern_b + "\n>> ")
            if len(new) == 0:
                new = pattern_b
        if not pattern_b_rgx.match(new):
            print("Your filename is missing a capture group for episode numbers. Episodes naturally have to be extinguishable by their seasonal or absolute episode numbers.")
        pattern_b = new
        break
    if input_bool("Are episode numbers for this pattern set given per season or in absolute numbers? (s = seasonal; a = absolute)\n>> ", ('s', "seasonal", 'e', "episodic", 'y'), ('a', "absolute", 'n')):
        season = input("Enter the season number for this pattern set.\nExample for a Season 2: 2\n>> ")
    else:
        season = "-1"

    sdata['patterns'] = {**sdata['patterns'], **{season: {pattern_a: pattern_b}}}
    series_data[tvdb_id] = sdata
    return series_data


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


def input_bool(text, trues=("y", "yes", '1', "true"), falses=("n", "no", '0', "false")):
    valid_answers = trues + falses
    while True:
        answer = input(text).lower()
        if answer in valid_answers:
            if answer in trues:
                return True
            elif answer in falses:
                return False
        else:
            print("Invalid input.")


def input_int(text):
    while True:
        try:
            value = int(input(text))
        except ValueError:
            print("Invalid input.")
            continue
        return value


def read_series_data():
    series_data = {}
    try:
        with open(SERIES_DATA_FILE, 'r') as f:
            series_data = json.load(f)
    except FileNotFoundError:
        file = open(SERIES_DATA_FILE, 'w')
        series_data = {}
    except json.decoder.JSONDecodeError:
        if not os.stat(SERIES_DATA_FILE).st_size == 0:
            print("Failed to read series data. Corrupted file? Check \"" + os.path.abspath(SERIES_DATA_FILE) + "\".")
            quit()  # TODO: really quit? maybe offer to display the file?
    return series_data


class RenameWorker(QThread):
    def __init__(self, settings, parent=None):
        QThread.__init__(self, parent)
        self.settings = settings

    def rename_torrent(self, torrent_info, target_file_info, new_filename):
        """
        Renames a torrent and its files and manipulates the QBittorrent fastresume file accordingly.
        """
        while True:  # using break in exceptions - why not return though? gotta take a closer look at this later on

            # QBittorrent's fastresume files are used at startup to quickly load up any torrents known to it.
            # Right now, renaming of files is not supported via Web API so instead we edit the fastresume files while the Application is closed.
            # Data can be located by certain tags such as "qBt-name" and any form of string is prefixed with its length and a colon.
            # e.g.: The filename "One Piece e300.mp4" would be stored as "18:One Piece e300.mp4". Apparently, unicode characters are still counted as only one character.
            fr = os.path.expandvars("%LOCALAPPDATA%/qBittorrent/BT_backup/") + torrent_info.hash + ".fastresume"
            with open(fr, 'rb') as f:
                fastresume = f.read()

            old_filename_relative = target_file_info.getRelativeFilename()
            old_bytes = qbt_tag_prefix(old_filename_relative)

            new_filename = clean_filename(new_filename)
            new_filename_relative = target_file_info.getRelativeFilename(new_filename)

            tag_mapped_files = qbt_tag_prefix(
                "mapped_files") + b"l"  # the l character is not part of the tag string but a list prefix

            try:
                idx_mapped_files = fastresume.index(tag_mapped_files) + len(
                    tag_mapped_files)  # starting index of file list data
                new_bytes = qbt_tag_prefix(new_filename_relative)
                idx_old_bytes = fastresume.index(old_bytes, idx_mapped_files)
                debug(f"Replacing \n{old_bytes}\nwith \n{new_bytes}\nat index {idx_old_bytes}", 1)
                fastresume = fastresume[:idx_old_bytes] + new_bytes + fastresume[idx_old_bytes + len(old_bytes):]
            except ValueError:
                tag_max_connections = qbt_tag_prefix("max_connections")  # todo explain
                idx_max_connections = fastresume.index(tag_max_connections)

                new_bytes = tag_mapped_files
                for x in range(len(torrent_info.files)):
                    if torrent_info.files[x].filename == target_file_info.filename:
                        torrent_info.files[x].filename = new_filename
                        new_bytes = new_bytes + qbt_tag_prefix(new_filename_relative)
                    else:
                        new_bytes = new_bytes + qbt_tag_prefix(torrent_info.files[x].getRelativeFilename())
                debug(f"Inserting \n{new_bytes}\n as the new filename at index {idx_max_connections}", 1)
                fastresume = fastresume[:idx_max_connections] + new_bytes + b'e' + fastresume[
                                                                                   idx_max_connections:]  # e indicates the end of the list

            # insert new filename as torrent name unless it's a batch torrent
            if len(torrent_info.files) == 1:
                qbttag_name = qbt_tag_prefix("qBt-name")  # torrent title prefix
                idx_name = fastresume.index(qbttag_name) + len(qbttag_name)  # starting index of title data
                new_name = qbt_tag_prefix(new_filename)
                old_name_length = int(fastresume[idx_name:fastresume.index(b':',
                                                                           idx_name)])  # figure out length of current title by parsing its prefixed number
                fastresume = fastresume[:idx_name] + new_name + fastresume[idx_name + len(
                    str(old_name_length)) + 1 + old_name_length:]

            try:
                os.rename('\\'.join(filter(None, [torrent_info.save_path, old_filename_relative])),
                          '\\'.join(filter(None, [torrent_info.save_path, target_file_info.subpath, new_filename])))
                print(f"Renamed {old_filename_relative} to {new_filename_relative}.")
            except OSError as e:
                print(e.strerror)
                print('\\'.join(filter(None, [torrent_info.save_path, old_filename_relative])))
                print("File renaming failed. No changes are being made.")
                break
            try:
                with open(fr, 'wb') as f:
                    f.write(fastresume)
                print("QBittorrent files have been manipulated accordingly.")
            except OSError as e:
                print(e.strerror)
                print("Failed to manipulate QBittorrent files. Reverting file rename...")
                try:
                    os.rename('\\'.join(filter(None, [torrent_info.save_path, target_file_info.subpath, new_filename])),
                              '\\'.join(filter(None, [torrent_info.save_path, old_filename_relative])))
                    print("File renaming reverted.")
                except OSError as e:
                    print(e.strerror)
                    print("Failed to revert renaming of file.")
                    break
            break


class FileFetcherSignals(QObject):
    rename_scan_result = Signal(Torrent)


class FileFetcher(QThread):
    def __init__(self, settings, parent=None):
        QThread.__init__(self, parent)
        self.signals = FileFetcherSignals()
        self.settings = settings
        self.series_data = {}
        self.torrents = {}
        self.qbt_handler = QBTHandler(self.settings)
        self.tvdb_handler = TVDBHandler(self.settings)

    def run(self):
        self.series_data = read_series_data()
        self.torrents = self.qbt_handler.fetch_torrents()
        process = None
        for p in psutil.process_iter():     # find QBittorrent process
            try:
                if self.settings["qbt_client"] in p.exe():
                    process = p
                    break           # assuming only one running QBittorrent process here. whatever.
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        # On Windows, Process.terminate() doesn't terminate the process peacefully, it just kills it right away like Process.kill()
        subprocess.call("taskkill /im  {}".format(self.settings["qbt_client"].split('\\')[-1]), stdout=open(os.devnull, 'w'), shell=False)
        # process.terminate()
        print("Waiting for QBittorrent to terminate...")
        if process is not None:
            process.wait(60)
            print("QBittorrent has been terminated.")
        else:
            print("No running QBittorrent process found. Assuming it has been terminated.")
        self.action_rename_scan()
        self.exec_()    # start event handling

    def action_rename_scan(self):
        # check all files by regex in our series data
        for torrent_info in self.torrents:
            irrelevant = True
            rename_whole_batch = False
            for file_info in torrent_info.files:
                if file_info.priority == 0:  # skip ignored files
                    continue
                for tvdb_id, data in self.series_data.items():
                    for season, patterns in data['patterns'].items():
                        for patternA, patternB in patterns.items():
                            pattern = re.compile(patternA)
                            if pattern.match(file_info.filename):   # send whole torrent to GUI, but first generate new names. also need to handle not matching files like .nfo files and shit like that. (ignore files without new filenames?)
                                file_info.filename_new = self.pattern_wizard(tvdb_id, season, patternA, patternB, file_info.filename)
                                irrelevant = False
            if not irrelevant:
                self.signals.rename_scan_result.emit(torrent_info)



        # check all files by regex in our series data
        # for torrent_info in self.torrents:
        #     torrent_item = QTorrentTreeWidgetItem()
        #     rename_whole_batch = False
        #     for file_info in torrent_info.files:
        #         if file_info.priority == 0:  # skip ignored files
        #             continue
        #         for tvdb_id, data in self.series_data.items():
        #             for season, patterns in data['patterns'].items():
        #                 for patternA, patternB in patterns.items():
        #                     pattern = re.compile(patternA)
        #                     if pattern.match(file_info.filename):
        #                         # self.signals.rename_scan_result.emit('\\'.join(filter(None, [torrent_info.save_path, file_info.subpath, file_info.filename])))
        #                         save_path = torrent_info.save_path
        #                         subpath = file_info.subpath
        #                         filename_old = file_info.filename
        #                         filename_new = self.pattern_wizard(tvdb_id, season, patternA, patternB, file_info.filename)
        #                         data = (save_path, subpath, filename_old, filename_new)
        #                         self.signals.rename_scan_result.emit(data)


                            #     if rename_whole_batch or input_bool("Rename this?\n{}\n>> ".format('\\'.join(filter(None, [torrent_info.save_path, file_info.subpath, file_info.filename])))):
                            #         try:
                            #             if not rename_whole_batch and len(torrent_info.files) > 1 and input_bool("Try to rename whole batch?\n>> "):
                            #                 rename_whole_batch = True
                            #             filename_new = pattern_wizard(tvdb_id, season, patternA, patternB,
                            #                                           file_info.filename)
                            #             rename_torrent(torrent_info, file_info, filename_new)
                            #         except TVDBEpisodeNumberNotInResult:
                            #             print("Failed to find an episode entry for this episode. Wait for TheTVDB to add this entry or rename the file by hand.")
        print("Restarting QBittorrent...")
        subprocess.Popen(self.settings["qbt_client"], close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
        print("Restarted!")
        self.qbt_handler.auth()
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
                filename_new = pattern_replace(filename_new, r"\S", season_number, True)
            while r"\E" in filename_new:
                filename_new = pattern_replace(filename_new, r"\E", episode_number, True)
            while r"\A" in filename_new:
                filename_new = pattern_replace(filename_new, r"\A", absolute_number, True)
            while r"\T" in filename_new:
                filename_new = pattern_replace(filename_new, r"\T", title, False)
            return clean_filename(filename_new)