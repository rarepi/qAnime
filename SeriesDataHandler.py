import json
import os

SERIES_DATA_FILE = "./data2.json"
os.makedirs(os.path.dirname(SERIES_DATA_FILE), exist_ok=True)


def read():
    series_data = {}
    try:
        with open(SERIES_DATA_FILE, 'r') as f:
            series_data = json.load(f)
    except FileNotFoundError:
        file = open(SERIES_DATA_FILE, 'w')
        series_data = {}
    except json.decoder.JSONDecodeError:
        if not os.stat(SERIES_DATA_FILE).st_size == 0:
            print(
                "Failed to read series data. Corrupted file? Check \"" + os.path.abspath(SERIES_DATA_FILE) + "\".")
            quit()  # TODO: really quit? maybe offer to display the file?
    return series_data


def write(series_data):
    with open(SERIES_DATA_FILE, 'w') as f:
        dump = json.dumps(series_data, indent=4, sort_keys=True)
        f.write(dump)


class SeriesDataHandler:
    def __init__(self):
        self.series_data = None

    def read(self):
        self.series_data = read()

    def write(self):
        write(self.series_data)

    def add(self, tvdb_id: int, season: int, regex: str, target: str):
        if not isinstance(tvdb_id, int):
            raise TypeError(f"TVDB ID must be int. {tvdb_id} is {type(tvdb_id)}.")
        if not isinstance(season, int):
            raise TypeError(f"Season Number must be int. {season} is {type(season)}.")
        if not isinstance(regex, str):
            raise TypeError(f"Regex pattern must be str. {regex} is {type(regex)}.")
        if not isinstance(target, str):
            raise TypeError(f"Target pattern must be str. {target} is {type(target)}.")
        if self.series_data is None:
            self.series_data = read()

        tvdb_id = str(tvdb_id)
        season = str(season)

        season_data = {regex: target}
        tvdb_data = {season: season_data}

        if self.series_data.get(tvdb_id) is None:
            self.series_data[tvdb_id] = tvdb_data
        else:
            if self.series_data[tvdb_id].get(season) is None:
                self.series_data[tvdb_id] = {**self.series_data[tvdb_id], **tvdb_data}
            else:
                # if given regex already exists in this season, its target pattern will be overwritten here.
                self.series_data[tvdb_id][season] = {**self.series_data[tvdb_id][season], **season_data}
