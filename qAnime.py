import requests
import json
import os
import re #regex
import psutil
import time

#TODO:
#Input Evaluations
#remove by pattern in series, not just by series

qbt_client = "C:\\Program Files\\qBittorrent\\qbittorrent.exe"
qbt_version = "v4.1.5"
url_qbt = 'http://localhost:8080/api/v2'
url_tvdb = 'https://api.thetvdb.com'
log = "log/log.txt"
series_data_file = "./data.json"
os.makedirs(os.path.dirname(log), exist_ok=True)
os.makedirs(os.path.dirname(series_data_file), exist_ok=True)


def clean_filename(filename):
    illegal_characters = '\\"/:<>?'
    rem_ill_chars = str.maketrans(illegal_characters, '_' * len(illegal_characters))
    return filename.translate(rem_ill_chars)

def qbt_auth():
    global qbt_cookie
    auth = {'username': 'shiki', 'password': 'omegalul'}
    qbt_cookie = requests.get(url_qbt + '/auth/login', params=auth)
    
def get_qbt_version():
    version = requests.get(url_qbt + '/app/version', cookies=qbt_cookie.cookies)
    return version.text
    
def fetchTorrentContent(hash):
    options = {'hash': hash}
    result_files = requests.get(url_qbt + '/torrents/files', cookies=qbt_cookie.cookies, params=options)
    json_files = result_files.json()
    result_properties = requests.get(url_qbt + '/torrents/properties', cookies=qbt_cookie.cookies, params=options)
    json_properties = result_properties.json()
    
    save_path = json_properties['save_path']

    if type(json_files) is list:
        files = {}
        files[hash] = (save_path, json_files)
    
    return files

def fetchTorrents():
    options = {'sort': 'name'}
    result = requests.get(url_qbt + '/torrents/info', cookies=qbt_cookie.cookies, params=options)
    json_data = result.json()
    
    json_dump = json.dumps(json_data, indent=4, sort_keys=True)
    with open(log, "w") as f:
        f.write(json_dump)

    return json_data
    
def is_process_running(process):
    for p in psutil.process_iter():
        try:
            if qbt_client in p.exe():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
            
def renameTorrent(hash, save_path, subpath, old_filename, new_filename, tor_files):
    """
    Renames a torrent and manipulates the QBittorrent fastresume files accordingly.
    
    :param str hash: QBittorrent's torrent hash
    :param str save_path: The torrent save path
    :param str subpath: path of subfolders inside save_path
    :param str old_filename: The current filename
    :param str new_filename: The new filename
    :param list(str) tor_files: list of relative filenames of torrent
    """

    while True:
        file = "C:/Users/Shiki/AppData/Local/qBittorrent/BT_backup/" + hash + ".fastresume"
        new_filename = clean_filename(new_filename)
        with open(file, 'rb') as f:
            fastresume = f.read()

        new_filename_relative = bytes('\\'.join(filter(None, [subpath, new_filename])), 'utf-8')

        qbttag_files = b"12:mapped_filesl"
        qbttag_name = b"8:qBt-name"
        qbttag_max_connections = b"15:max_connections"
        qbttag_queue_position = b"17:qBt-queuePosition"
        new_filename_relative_length = bytes(str(len(new_filename_relative)), "ascii")
            
        
        #build byte string of file list 
        tor_files_string = b""
        for tor_file in tor_files:
            tor_file_b = bytes(tor_file, 'utf-8')
            tor_files_string = tor_files_string + bytes(str(len(tor_file_b)), "ascii") + b':' + tor_file_b
        #insert file name
        idx = fastresume.find(qbttag_files)
        idx2 = fastresume.index(qbttag_max_connections)
        if idx is -1:
            fastresume = fastresume[:idx2] + qbttag_files + tor_files_string + b'e' + fastresume[idx2:]
        else:
            fastresume = fastresume[:idx] + qbttag_files + tor_files_string + b'e' + fastresume[idx2:]
            
        #insert new filename as torrent name unless it's a batch torrent
        if len(tor_files) == 1:
            idx = fastresume.index(qbttag_name)
            idx = idx + len(qbttag_name)
            next_idx = fastresume.index(qbttag_queue_position, idx)
            fastresume = fastresume[:idx] + new_filename_relative_length + b':' + new_filename_relative + fastresume[next_idx:]

        try:
            os.rename('\\'.join(filter(None, [save_path, subpath, old_filename])), '\\'.join(filter(None, [save_path, subpath, new_filename])))
            print(f"Renamed {old_filename} to {new_filename}.")
        except OSError as e:
            print(e.strerror)
            print('\\'.join(filter(None, [save_path, subpath, old_filename])))
            print("File renaming failed. No changes are being made.")
            break
        try:
            with open(file, 'wb') as f:
                f.write(fastresume)
            print("QBittorrent files have been manipulated accordingly.")
        except OSError as e:
            print(e.strerror)
            print("Failed to manipulate QBittorrent files. Reverting file rename...")
            try:
                os.rename('\\'.join(filter(None, [save_path, subpath, new_filename])), '\\'.join(filter(None, [save_path, subpath, old_filename])))
                print("File renaming reverted.")
            except OSError as e:
                print(e.strerror)
                print("Failed to revert renaming of file.")
                break
        break

def tvdb_auth():
    global tvdb_auth
    auth = {"apikey" : "2323B61F3A9DA8C8", "username" : "elpingu42", "userkey" : "52EB4C6A3C24B288"}

    result = requests.post(url_tvdb + '/login', json=auth)
    if result.status_code != 200:
        print('TVDB AUTHENTICATION FAILED')
        print('TVDB Auth Response Status Code: ', result.status_code)
        print('TVDB Auth Response: ', result.text)
    else:
        tvdb_auth = result.json()['token']

def tvdb_getSeries(name):
    head = {"Authorization" : "Bearer " + tvdb_auth, "Accept-Language" : "en", "content-type" : "application/json"}
    data = {'name': name}
    result = requests.get(url_tvdb + '/search/series', headers = head, params = data)
    if result.status_code != 200:
        print('TVDB Series Fetch Response Status Code: ', result.status_code)
        print('TVDB Series Fetch Response: ', result.text)
        return {}
    json_data = result.json()
    if type(json_data) is dict:
        series_options = {}
        i = 0
        for item in json_data['data']:
            series_options[i] = (str(item['id']), item['seriesName'])
            print(str(i) + ") " + series_options[i][1] + " (" + item['network'] + ")")
            i+=1
        index = int(input("Choose the correct series by index.\n>> "))    #TODO: Evaluate int
        print("You picked \"" + series_options[index][1] + "\". TheTVDB ID is " + series_options[index][0] + ".")
        
        return series_options[index]

def tvdb_getSingleEpisode(tvdb_id, season, episodeNumber):
    head = {"Authorization" : "Bearer " + tvdb_auth, "Accept-Language" : "en", "content-type" : "application/json"}
    data = {}
    if season == "-1":
        data = {'absoluteNumber': episodeNumber}
    else:
        data = {'airedSeason': season, 'airedEpisodeNumber': episodeNumber.lstrip('0')}
    result = requests.get(url_tvdb + '/series/' + tvdb_id + '/episodes/query', headers = head, params = data)
    if result.status_code != 200:
        print('TVDB Episode Fetch Response Status Code: ', result.status_code)
        print('TVDB Episode Fetch Response: ', result.text)
        return
        
    for item in result.json()['data']:
        if (season != "-1" and item['airedEpisodeNumber'] == int(episodeNumber) and item['airedSeason'] == int(season) 
            or season == "-1" and item['absoluteNumber'] == int(episodeNumber)):
            return item
        
def metadata_wizard(id, series_data):
    x_name = "Mob Psycho 100"
    x_patternA = r"^\[HorribleSubs\] Mob Psycho 100 - (\d\d) \[720p\]\.mkv"
    x_patternB = "Mob Psycho 100 - s\S\Se\E\E - [\A\A] \T - [2019 ENG-Sub AAC 720p HDTV x264 - HorribleSubs].mkv"
    
    sdata = {}
    #add new entry
    if id is -1:
        name = input("Enter the name of the series.\nExample: " + x_name + "\n>> ")
        tvdb_series = tvdb_getSeries(name)
        id = tvdb_series[0]
        name = tvdb_series[1]
        
        if id in series_data.keys():
            if input("Series ID " + id + " already has an entry named \"" + series_data[id]['name'] + "\". Add new pattern? (y/n)\n>> ") != 'y':
                return
            sdata = series_data[id]
        else:
            sdata = {
                "name" : name,
                "patterns" : {
                }
                }
    #edit existing entry
    else:
        sdata = series_data[id]
        
        pattern_set_options = {}
        i = 0
        for item in sdata['patterns']:
            pattern_set_options[i] = item
            print(str(i) + ") " + pattern_set_options[i][0] + " RENAMES TO " + pattern_set_options[i][1])
            i+=1
        index = int(input("Choose the pattern set you want to replace by index.\n>> "))    #TODO: Evaluate int
        print("Pattern set \"" + sdata['patterns'].pop(index) + "\" has been removed.")
    
    patternA = input("Enter unique regex for detection. Provide a capture group for the episode number. (e. g. (\d\d))\nExample: " + x_patternA + "\n>> ")
    patternB = input("Enter target file name.\nExample: " + x_patternB + "\nValid tags:\n\S - Season Number\n\E - Seasonal Episode Number\n\A - Absolute Episode Number\n\T - Season Title\n>> ")
    if input("Are episode numbers for this pattern set given per season? (y = per season; n = absolute)\n>> ") == 'y':
        season = input("Enter the season number for this pattern set.\nExample: 2\n>> ")
    else:
        season = "-1"
    
    sdata['patterns'] = {**sdata['patterns'], **{season:{patternA : patternB}}}
    series_data[id] = sdata
    return series_data
    
def patternReplace(pattern, old, new, fill=False):
    count = 0
    idx = pattern.find(old)
    if idx >= 0:
        count = 1
        lookahead = len(old)
        while pattern[idx+lookahead:idx+lookahead+len(old)] == old:
            count += 1
            lookahead += len(old)
        if fill:
            new = str(new).zfill(count)
        pattern = pattern[:idx] + new + pattern[idx+len(old)*count:]
    return pattern
    
def patternWizard(tvdb_id, season, patternA, patternB, filename):
    pattern = re.compile(patternA)
    if pattern.match(filename):
        episodeNumber = re.search(patternA, filename).group(1)
        episode_json_data = tvdb_getSingleEpisode(tvdb_id, season, episodeNumber)
        seasonNumber = episode_json_data['airedSeason']
        episodeNumber = episode_json_data['airedEpisodeNumber']
        absoluteNumber = episode_json_data['absoluteNumber']
        title = episode_json_data['episodeName']
        filename_new = patternB
        
        while "\S" in filename_new:
            filename_new = patternReplace(filename_new, "\S", seasonNumber, True)
        while "\E" in filename_new:
            filename_new = patternReplace(filename_new, "\E", episodeNumber, True)
        while "\A" in filename_new:
            filename_new = patternReplace(filename_new, "\A", absoluteNumber, True)
        while "\T" in filename_new:
            filename_new = patternReplace(filename_new, "\T", title, False)
        return filename_new

def main():
    tvdb_auth()
    qbt_auth()
    
    qbt_version_cur = get_qbt_version()
    if qbt_version != qbt_version_cur:
        if input("WARNING: QBittorrent version mismatch: Got \"{}\", expected \"{}\". Compatibility is not ensured. \nContinue? (y/n)".format(qbt_version_cur, qbt_version)) != 'y':
            print("Exiting.")
            return
    try:
        with open(series_data_file, 'r') as f:
            series_data = json.load(f)
    except FileNotFoundError:
        file = open(series_data_file, 'w')
        series_data = {}
    except json.decoder.JSONDecodeError:
        if not os.stat(series_data_file).st_size == 0:
            print("Failed to read json data. Check \"" + os.path.abspath(series_data_file) + "\".")
            quit()
        else:
            series_data = {}

    while True:
        print("\n1) Scan for new episodes\n"
            "2) Add data of a new series\n"
            "3) Edit data of a series\n"
            "4) Delete data of a series\n"
            "0) Exit\n")
        job = int(input("What to do?\n>> "))

        if job == 0:
            print("Exiting.")
            break
        elif job == 1:
            torrents = fetchTorrents()
            hashes = []
            contents = {}
            
            if type(torrents) == list:
                for item in torrents:
                    hashes.append(item['hash'])
                    
            #fetch files in torrents
            for item in hashes:
                tc = fetchTorrentContent(item)
                contents = {**contents, **tc}
    
            os.system("taskkill /im  {}".format(qbt_client.split('\\')[-1]))
            timer = 0
            while is_process_running(qbt_client):
                time.sleep(1)
                timer+=1
                if timer >= 60:
                    print("Error: Failed to terminate QBittorrent after 60 seconds.")
                    return
                print(f"Waiting for QBittorrent to terminate... ({timer}s)", end='\r')
            print("\nQBittorrent has been terminated.")
                
            #check all files by regex in our series data
            for hash, file_data in contents.items():
                save_path = file_data[0]
                if save_path[-1] == '\\':           #remove trailing backslash for tidy string joins
                    save_path = save_path[:-1]
                tor_files = []
                renameWholeBatch = False
                for file in file_data[1]:
                    tor_files.append(file['name'])   #list of all filenames in torrent used for fastresume manipulation, needed for batch torrents
                for file in file_data[1]:
                    if file['priority'] == 0:   #skip ignored files
                        continue
                    filename_split = file['name'].split('\\')
                    subpath = '\\'.join(filename_split[:-1])    #is empty string if no subpath
                    filename = filename_split[-1]
                    for tvdb_id, data in series_data.items():
                        for season, patterns in data['patterns'].items():
                            for patternA, patternB in patterns.items():
                                pattern = re.compile(patternA)
                                if pattern.match(filename):
                                    response = input("Rename this? (y/n)\n{}\n>> ".format('\\'.join(filter(None, [save_path, subpath, filename])))) if not renameWholeBatch else 'y'
                                    if response.lower() == 'y':
                                        if not renameWholeBatch and len(tor_files) > 1 and input("Try to rename whole batch? (y/n)\n>> ") == 'y':
                                            renameWholeBatch = True
                                        filename_new = patternWizard(tvdb_id, season, patternA, patternB, filename)
                                        tor_files = [tor_file.replace('\\'.join(filter(None, [subpath, filename])), '\\'.join(filter(None, [subpath, filename_new]))) for tor_file in tor_files]
                                        renameTorrent(hash, save_path, subpath, filename, filename_new, tor_files)
            print("Restarting QBittorrent...")
            os.startfile(qbt_client)
            qbt_auth()
        elif job == 2:
            series_data = metadata_wizard(-1, series_data)
        elif job == 3:
            series_options = {}
            i = 0
            for key, value in series_data.items():
                series_options[i] = key
                print(str(i) + ") " + value['name'] + " (" + str(key) + ")")
                i+=1
            index = int(input("Choose the correct series by index.\n>> "))    #TODO: Evaluate int
            series_data = metadata_wizard(series_options[index], series_data)
        elif job == 4:
            series_options = {}
            i = 0
            for key, value in series_data.items():
                series_options[i] = (key, value['name'])
                print(str(i) + ") " + value['name'] + " (" + str(key) + ")")
                i+=1
            index = int(input("Choose the correct series by index.\n>> "))    #TODO: Evaluate int
            try:
                del series_data[series_options[index][0]]
            except KeyError:
                print("Error: Tried to remove an invalid series entry.")
                continue
            print("Removed series data of " + series_options[index][1] + ".")
        else:
            print("Invalid input.")
        with open(series_data_file, 'w') as f:
            dump = json.dumps(series_data, indent=4, sort_keys=True)
            f.write(dump)
main()