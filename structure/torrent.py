import requests

from .episode import Episode

class File():
    """File"""
    def __init__(self, subpath, filename, episode=None, torrent=None, priority=None):
        self.subpath = subpath
        self.filename = filename
        self.episode = episode
        self.torrent = torrent
        self.priority = priority
    def setEpisode(self, episode):
        self.episode = episode
    def setTorrent(self, torrent):
        if not self in torrent.files:
            self.torrent = torrent
            torrent.files.append(self)
    def setPriority(self, priority):
        self.priority = priority

class Torrent():
    """Torrent"""
    def __init__(self, hash, save_path=""):
        self.hash = hash
        self.save_path = save_path
        self.files = []

    def setSavePath(self, save_path):
        if save_path[-1] == '\\':   #remove trailing backslash
            self.save_path = save_path[:-1]
        else:
            self.save_path = save_path
    def addFile(self, file):
        if not file in self.files:
            file.torrent = self
            self.files.append(file)

    def fetchFiles(self, qbt_url, qbt_cookie):
        #https://github.com/qbittorrent/qBittorrent/wiki/Web-API-Documentation#get-torrent-contents
        options = {'hash': self.hash}
        result_files = requests.get(qbt_url + '/torrents/files', cookies=qbt_cookie.cookies, params=options)
        json_files = result_files.json()
        result_properties = requests.get(qbt_url + '/torrents/properties', cookies=qbt_cookie.cookies, params=options)
        json_properties = result_properties.json()

        save_path = json_properties['save_path']

        if type(json_files) is list:
            self.setSavePath(save_path)
            for item in json_files:
                filename_split = item["name"].split('\\')
                subpath = '\\'.join(filename_split[:-1])    #is empty string if no subpath
                filename = filename_split[-1]
                f = File(subpath, filename)
                f.setPriority(item["priority"])
                self.addFile(f)