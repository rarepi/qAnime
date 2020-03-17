import json
import requests
from PySide2.QtCore import Signal, QObject
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
    update_progress = Signal(int)
    init_progress = Signal(int, int)
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
            index = 0
            self.init_progress.emit(index, len(json_data))
            while index < len(json_data):
                if json_data[index]['progress'] == 1.0:
                    torrent = Torrent(json_data[index]['name'], json_data[index]['hash'])
                    torrent.fetchFiles(self.settings["qbt_url"], self.cookie)
                    torrents.append(torrent)
                index += 1
                self.update_progress.emit(index)
            print('\nFetching done.')
        except json.decoder.JSONDecodeError:
            print("ERROR: QBittorrent returned an invalid torrent list.")
            print("Cookies:", self.cookie.cookies)
            print("Response Status Code:", result.status_code)
            print('Response Text: ', result.text)
        return torrents
