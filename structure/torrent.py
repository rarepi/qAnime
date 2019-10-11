import requests
import os

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
    def getRelativeFilename(self, filename_replacement=None):
        if filename_replacement is None:
            return '\\'.join(filter(None, [self.subpath, self.filename]))
        else:
            return '\\'.join(filter(None, [self.subpath, filename_replacement]))
    # def getFastresume(self):
    #     return os.path.expandvars("%LOCALAPPDATA%/qBittorrent/BT_backup/") + self.torrent.hash + ".fastresume"
    # def editFastresume(self, new_filename):
    #     fr = self.getFastresume()
    #     with open(fr, 'rb') as f:
    #         fastresume = f.read()

    #     old_filename_relative = bytes('\\'.join(filter(None, [self.subpath, self.filename])), 'utf-8')
    #     old_filename_relative_length = bytes(str(len(old_filename_relative)), "ascii")
    #     old_bytes = old_filename_relative_length + b':' + old_filename_relative

    #     new_filename_relative = bytes('\\'.join(filter(None, [self.subpath, new_filename])), 'utf-8')
    #     new_filename_relative_length = bytes(str(len(new_filename_relative)), "ascii")
    #     new_bytes = new_filename_relative_length + b':' + new_filename_relative

    #     tag = b"12:mapped_filesl" #torrent file list prefix (last l character is not part of the tag string but assumably prefixes a list)
    #     file_list_idx = fastresume.index(tag)+len(tag) #starting index of file list data
    #     old_idx = fastresume.index(old_bytes, file_list_idx)
    #     fastresume = fastresume[:old_idx] + new_bytes + fastresume[old_idx+len(old_bytes):]

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
            
    # def editFastresume(self, new_title):
    #     fr = self.getFastresume()
    #     with open(fr, 'rb') as f:
    #         fastresume = f.read()

    #     new_title_length = bytes(str(len(new_title)), "ascii")
    #     new_bytes = new_title_length + b':' + new_title

    #     tag = b"8:qBt-name" #torrent title prefix
    #     title_idx = fastresume.index(tag)+len(tag) #starting index of title data
    #     old_title_length = int(fastresume[title_idx:fastresume.index(b':', title_idx)]) #figure out length of current title by parsing its prefixed number
    #     fastresume = fastresume[:title_idx] + new_bytes + fastresume[title_idx+len(str(old_title_length))+1+old_title_length:]
            
    # def getFastresume(self):
    #     return os.path.expandvars("%LOCALAPPDATA%/qBittorrent/BT_backup/") + self.hash + ".fastresume"