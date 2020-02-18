import requests
import json
import os
import re  # regex
import time
import sys
from threading import Thread

from PySide2.QtCore import QThread, Signal, QTimer, Slot, QEventLoop, QObject, QRunnable

# 0 = No debug output
# 1 = small stuff?
# 2 = full json data dumps
DEBUG_OUTPUT_LEVEL = 2


class TVDBEpisodeNumberNotInResult(Exception):
    """Raised when an episode number is not found in TVDB result"""
    pass


def debug(output, level):
    if DEBUG_OUTPUT_LEVEL >= level:
        print(output)


class TVDBHandler(QObject):
    def __init__(self, settings):
        super(TVDBHandler, self).__init__()
        self.settings = settings
        self.cookie = None
        self.token = None
        self.auth()

    def auth(self):
        auth = {"apikey": self.settings["tvdb_apikey"]}
        result = requests.post(self.settings["tvdb_url"] + '/login', json=auth)
        if result.status_code != 200:
            print('TVDB AUTHENTICATION FAILED')
            print('TVDB Auth Response Status Code: ', result.status_code)
            print('TVDB Auth Response: ', result.text)
        else:
            self.token = result.json()['token']

    def get_series(self, name):
        head = {"Authorization": "Bearer " + self.token, "Accept-Language": "en", "content-type": "application/json"}
        data = {'name': name}
        result = requests.get(self.settings["tvdb_url"] + '/search/series', headers=head, params=data)
        if result.status_code == 404:
            print("TheTVDB.com was unable to find a series using the specified name. Try a different name.")
            return {}
        elif result.status_code != 200:
            print('TVDB Series Fetch Response Status Code: ', result.status_code)
            print('TVDB Series Fetch Response: ', result.text)
            return {}
        json_data = result.json()
        if type(json_data) is dict:
            series_options = {}
            i = 0
            debug(f"json data: {json_data['data']}", 2)
            for item in json_data['data']:
                series_options[i] = (str(item['id']), item['seriesName'])

                if isinstance(item['network'], str):  # network can be None
                    print(str(i) + ") " + series_options[i][1] + " (" + item['network'] + ")")
                else:
                    print(f"{str(i)}) {series_options[i][1]}")

                i += 1
            while True:
                index = input_int("Choose the correct series by index.\n>> ")
                try:
                    print(
                        "You picked \"" + series_options[index][1] + "\". TheTVDB ID is " + series_options[index][
                            0] + ".")
                except KeyError:
                    print("Invalid input.")
                    continue
                break

            return series_options[index]

    def get_single_episode(self, tvdb_id, season, episode_number):
        head = {"Authorization": "Bearer " + self.token, "Accept-Language": "en", "content-type": "application/json"}
        data = {}
        if season == "-1":
            data = {'absoluteNumber': episode_number}
        else:
            episode_number = episode_number.lstrip('0')  # episode number CAN be 0
            if not episode_number:  # empty strings are false
                episode_number = "0"
            data = {'airedSeason': season, 'airedEpisodeNumber': episode_number}
        result = requests.get(self.settings["tvdb_url"] + '/series/' + tvdb_id + '/episodes/query', headers=head,
                              params=data)
        if result.status_code != 200:
            print("TVDB Episode Fetch Response Status Code: ", result.status_code)
            print("TVDB Episode Fetch Response: ", result.text)
            return

        for item in result.json()['data']:
            if season != "-1" and item['airedEpisodeNumber'] == int(episode_number) and item['airedSeason'] == int(
                    season) or season == "-1" and item['absoluteNumber'] == int(episode_number):
                return item
        raise TVDBEpisodeNumberNotInResult
