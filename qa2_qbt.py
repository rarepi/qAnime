import json
import requests
from PySide2.QtCore import Signal, QObject

import qa2_util
from structure.torrent import Torrent


def qbt_tag_prefix(string):
    # todo check for type?
    string_b = bytes(string, "utf-8")
    length_str_b = bytes(str(len(string_b)), "utf-8")
    return length_str_b + b':' + string_b


def clean_filename(filename):
    illegal_characters = '\\"/:<>?|'
    rem_ill_chars = str.maketrans(illegal_characters, '_' * len(illegal_characters))
    return filename.translate(rem_ill_chars)


class QBTHandler(QObject):
    track_progress_text = Signal(str)
    track_progress_update = Signal(int)
    track_progress_range = Signal(int, int)
    track_progress_start = Signal()
    auth_finished = Signal(int)

    def __init__(self, settings):
        super(QBTHandler, self).__init__()
        self.settings = settings
        self.cookie = None
        # self.auth()  # TODO exceptions if auth() hasn't been used

    def auth(self):
        auth = {'username': self.settings["qbt_username"], 'password': self.settings["qbt_password"]}
        try:
            self.cookie = requests.get(self.settings["qbt_url"] + '/auth/login', params=auth)
            self.auth_finished.emit(0)
        except requests.exceptions.ConnectionError:
            print("Failed connecting to QBittorrent WebAPI. Make sure QBittorrent is running and its Web UI is enabled.")
            self.auth_finished.emit(-1)

    def get_qbt_version(self):
        version = requests.get(self.settings["qbt_url"] + '/app/version', cookies=self.cookie.cookies)
        return version.text

    def fetch_torrents(self):
        # https://github.com/qbittorrent/qBittorrent/wiki/Web-API-Documentation#get-torrent-list
        options = {'sort': 'name'}
        result = requests.get(self.settings["qbt_url"] + '/torrents/info', cookies=self.cookie.cookies, params=options)

        torrents = []
        try:
            json_data = result.json()
            progress_index = 0
            progress_maximum = len(json_data)
            progress_interval = int(progress_maximum / 100) if progress_maximum >= 100 else 1
            self.track_progress_text.emit("Fetching torrents from QBittorrent...")
            self.track_progress_range.emit(progress_index, progress_maximum)
            self.track_progress_start.emit()
            while progress_index < progress_maximum:
                if json_data[progress_index]['progress'] == 1.0:
                    torrent = Torrent(json_data[progress_index]['name'], json_data[progress_index]['hash'])
                    torrent.fetchFiles(self.settings["qbt_url"], self.cookie)
                    torrents.append(torrent)
                progress_index += 1
                if progress_index % progress_interval == 0 or progress_index >= progress_maximum:
                    self.track_progress_update.emit(progress_index)
            qa2_util.debug("\nFetching done.", level=1)
        except json.decoder.JSONDecodeError:
            print("ERROR: QBittorrent returned an invalid torrent list.")
            print("Cookies:", self.cookie.cookies)
            print("Response Status Code:", result.status_code)
            print('Response Text: ', result.text)
        return torrents
