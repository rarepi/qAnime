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

    def add(self, new_data: dict):
        if self.series_data is None:
            self.series_data = read()
        if isinstance(new_data, dict):
            for tvdb_id in new_data.keys():
                if tvdb_id in self.series_data.keys():
                    raise KeyError(f"Key {tvdb_id} is already in use and thus may not be added by this function.")
                if isinstance(tvdb_id, str) and isinstance(new_data[tvdb_id], dict):
                    int(tvdb_id)    # raises an exception if it's not numeric. (str.isnumeric() misses negative numbers!)
                    for season in new_data[tvdb_id].keys():
                        if isinstance(season, str) and isinstance(new_data[tvdb_id][season], dict):
                            int(season)
                            for regex, target in new_data[tvdb_id][season].items():
                                if isinstance(regex, str) and isinstance(target, str):
                                    pass
                                else:
                                    raise TypeError(f"Patterns must be strings. {regex} is {type(regex)}, {target} is {type(target)}.")
                        else:
                            raise TypeError(f"Seasons must be numeric string keys in a dict. {season} is {type(season)}.")
                else:
                    raise TypeError(f"TVDB IDs must be numeric string keys in a dict. {tvdb_id} is {type(tvdb_id)}.")
        else:
            raise TypeError(f"Series Data must be a dict. {type(new_data)} found for\n{new_data}")
        self.series_data = {**self.series_data, **new_data}