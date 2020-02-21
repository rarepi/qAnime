import json
import os
import subprocess
import re  # regex
import psutil

from PySide2.QtCore import QThread, Signal, QObject

from QTorrentWidgets import QTorrentTreeWidget, QTorrentTreeWidgetTorrent
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


def debug(output, level):
    if DEBUG_OUTPUT_LEVEL >= level:
        print(output)


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


class Fastresume:
    def __init__(self, fastresume:bytes):
        self.TAG_DICT = 'd'
        self.TAG_SEPARATOR = ':'
        self.TAG_INT = 'i'
        self.TAG_LIST = 'l'
        self.TAG_END = 'e'

        self.fastresume = fastresume

        self.data = self.read_bencoded()[1]

    def rename_file(self, old:str, new:str):
        if not isinstance(old, str) or not isinstance(new, str):
            return  # TODO ERROR

        if "mapped_files" not in self.data.keys():
            self.data["mapped_files"] = []
        if not isinstance(self.data["mapped_files"], list):
            return  # TODO ERROR

        old = bytes(old, "utf-8")
        new = bytes(new, "utf-8")

        if old in self.data["mapped_files"]:
            self.data["mapped_files"].replace(old, new, 1)
        else:
            self.data["mapped_files"].append(new)   # assuming correct order, kinda bad

    def rename_torrent(self, new:str):
        if isinstance(new, str):
            self.data["qBt-name"] = bytes(new, "utf-8")

    def edit_data(self, key:str, value):
        if isinstance(value, type(self.data[key])):
            self.data[key] = value
        else:
            pass    # TODO type error

    def write(self) -> bytearray:
        output = bytearray(bytes(self.TAG_DICT, "ascii"))
        for k, d in self.data.items():
            output += bytes(str(len(k)), "ascii") \
                      + bytes(self.TAG_SEPARATOR, "ascii") \
                      + bytes(k, "ascii")
            output += self.unpack_data(d)

        output += bytes(self.TAG_END, "ascii")
        return output

    def unpack_data(self, item) -> bytearray:
        output = bytearray()

        if isinstance(item, int):
            output += bytes(self.TAG_INT, "ascii") \
                      + bytes(str(item), "ascii") \
                      + bytes(self.TAG_END, "ascii")
        elif isinstance(item, bytes):
            output += bytes(str(len(item)), "ascii") \
                      + bytes(self.TAG_SEPARATOR, "ascii") \
                      + item
        elif isinstance(item, list):
            output += bytes(self.TAG_LIST, "ascii")
            for element in item:
                output += self.unpack_data(element)
            output += bytes(self.TAG_END, "ascii")
        return output

    def read_bencoded(self, idx=0):
        if chr(self.fastresume[idx]) == self.TAG_DICT:
            data = {}
            idx += 1

            while chr(self.fastresume[idx]) != self.TAG_END:
                # key
                if not chr(self.fastresume[idx]).isdigit():
                    return None, None  # TODO ERROR
                idx_separator = self.fastresume.index(bytes(self.TAG_SEPARATOR, "ascii"), idx)
                length = int(self.fastresume[idx:idx_separator])
                idx = idx_separator + 1
                key = self.fastresume[idx:idx + length].decode("utf-8")
                idx += length

                # value
                idx, value = self.read_bencoded(idx)
                data[key] = value
            return idx, data

        elif chr(self.fastresume[idx]) == self.TAG_LIST:     # data is list
            idx += 1
            data = []
            while chr(self.fastresume[idx]) != self.TAG_END:
                idx, value = self.read_bencoded(idx)
                data.append(value)
            idx += 1
            return idx, data
        elif chr(self.fastresume[idx]) == self.TAG_INT:      # data is int
            idx += 1
            idx_end = self.fastresume.index(bytes(self.TAG_END, "ascii"), idx)
            data = int(self.fastresume[idx:idx_end])  #
            idx = idx_end + 1
            return idx, data
        elif chr(self.fastresume[idx]).isdigit():            # data is bytes
            idx_separator = self.fastresume.index(bytes(self.TAG_SEPARATOR, "ascii"), idx)
            length = int(self.fastresume[idx:idx_separator])
            idx = idx_separator + 1
            data = self.fastresume[idx:idx + length]
            idx += length
            return idx, data
        else:
            print("Got", chr(self.fastresume[idx]))
            return None, None    # TODO ERROR



class RenameWorker(QThread):
    def __init__(self, settings, parent=None):
        super().__init__()
        self.settings = settings

    def rename_torrents(self, tree_torrents:QTorrentTreeWidget):
        """
        Renames a QTorrentTreeWidget's torrents and their files and manipulates the QBittorrent fastresume file accordingly.
        """
        if not isinstance(tree_torrents, QTorrentTreeWidget):
            return
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

            for i in range(tree_torrents.topLevelItemCount()):
                torrent_widget = tree_torrents.topLevelItem(i)

                fastresume_file = os.path.expandvars("%LOCALAPPDATA%/qBittorrent/BT_backup/") + torrent_widget.torrent.hash + ".fastresume"
                with open(fastresume_file, 'rb') as f:
                    fr = f.read()
                fastresume = Fastresume(fr)
                if torrent_widget.checked:
                    fastresume.rename_torrent(torrent_widget.torrent.name_new)

                for j in range(torrent_widget.childCount()):
                    file_widget = torrent_widget.child(j)
                    if not file_widget.checked:
                        continue
                    old_filename_relative = file_widget.file.getRelativeFilename()
                    file_widget.file.filename_new = clean_filename(file_widget.file.filename_new)
                    new_filename_relative = file_widget.file.getRelativeFilename(file_widget.file.filename_new)

                    fastresume.rename_file(old_filename_relative, new_filename_relative)

                    try:
                        os.rename('\\'.join(filter(None, [torrent_widget.torrent.save_path, old_filename_relative])),
                                  '\\'.join(filter(None, [torrent_widget.torrent.save_path, file_widget.file.subpath, file_widget.file.filename_new])))
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
                    print("Failed to manipulate QBittorrent fastresume file. Reverting file rename...")
                    for j in range(torrent_widget.childCount()):
                        file_widget = torrent_widget.child(torrent_widget.childCount()-1-j)
                        if not file_widget.checked:
                            continue
                        old_filename_relative = file_widget.file.getRelativeFilename()
                        new_filename_relative = file_widget.file.getRelativeFilename(file_widget.file.filename_new)

                        fastresume.rename_file(new_filename_relative, old_filename_relative)

                        try:
                            os.rename(
                                '\\'.join(filter(None, [torrent_widget.torrent.save_path, file_widget.file.subpath,
                                                        file_widget.file.filename_new])),
                                '\\'.join(filter(None, [torrent_widget.torrent.save_path, old_filename_relative])))
                            print(f"Reverted {new_filename_relative} to {old_filename_relative}.")
                        except OSError as e:
                            print(e.strerror)
                            print("Rename revert failed. Q_Q")
                            break
            print("Restarting QBittorrent...")
            subprocess.Popen(self.settings["qbt_client"], close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
            print("Restarted!")


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