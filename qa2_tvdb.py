import requests

from PySide2.QtCore import QObject, Signal

import qa2_util


class TVDBEpisodeNumberNotInResult(Exception):
    """Raised when an episode number is not found in TVDB result"""
    pass


class TVDBHandler(QObject):
    series_results_collected = Signal(list)

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
        qa2_util.debug(json_data['data'], level=2)
        if type(json_data) is dict:
            search_result = []
            for item in json_data['data']:
                try:
                    search_result.append((item['id'], item['seriesName'], item['firstAired'][:4], item['network']))
                except TypeError:
                    if item['firstAired'] is None:
                        search_result.append((item['id'], item['seriesName'], None, item['network']))

            self.series_results_collected.emit(search_result)

    def get_series_name(self, id_) -> str:
        head = {"Authorization": "Bearer " + self.token, "Accept-Language": "en", "content-type": "application/json"}
        data = {"keys": "seriesName"}
        result = requests.get(self.settings["tvdb_url"] + '/series/' + str(id_) + "/filter", headers=head, params=data)
        if result.status_code == 404:
            print("TheTVDB.com was unable to find a series using the specified ID. Try a different ID.")
            return {}
        elif result.status_code != 200:
            print('TVDB Series Fetch Response Status Code: ', result.status_code)
            print('TVDB Series Fetch Response: ', result.text)
            return {}
        json_data = result.json()
        qa2_util.debug(json_data['data'], level=2)
        if type(json_data) is dict:
            return json_data['data']['seriesName']


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
