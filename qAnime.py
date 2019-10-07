import requests
import json
import os
import subprocess
import re #regex
import psutil
import time
import sys

#TODO:
#Input Evaluations
#remove by pattern in series, not just by series
#same patternA may not be in two seasons
#editing: asking for season after editing?

series_data_file = "./data.json"
settings_file = "./settings.json"
os.makedirs(os.path.dirname(series_data_file), exist_ok=True)
os.makedirs(os.path.dirname(settings_file), exist_ok=True)

class TVDBEpisodeNumberNotInResult(Exception):
   """Raised when an episode number is not found in TVDB result"""
   pass

def clean_filename(filename):
    illegal_characters = '\\"/:<>?|'
    rem_ill_chars = str.maketrans(illegal_characters, '_' * len(illegal_characters))
    return filename.translate(rem_ill_chars)

def qbt_auth():
    global qbt_cookie
    auth = {'username': settings["qbt_username"], 'password': settings["qbt_password"]}
    try:
        qbt_cookie = requests.get(settings["qbt_url"] + '/auth/login', params=auth)
    except requests.exceptions.ConnectionError as e:
        print("Failed connecting to QBittorrent WebAPI. Make sure QBittorrent is running and its Web UI is enabled.")
        sys.exit()
    
def get_qbt_version():
    version = requests.get(settings["qbt_url"] + '/app/version', cookies=qbt_cookie.cookies)
    return version.text
    
def fetchTorrentContent(hash):
    options = {'hash': hash}
    result_files = requests.get(settings["qbt_url"] + '/torrents/files', cookies=qbt_cookie.cookies, params=options)
    json_files = result_files.json()
    result_properties = requests.get(settings["qbt_url"] + '/torrents/properties', cookies=qbt_cookie.cookies, params=options)
    json_properties = result_properties.json()
    
    save_path = json_properties['save_path']

    if type(json_files) is list:
        files = {}
        files[hash] = (save_path, json_files)
    
    return files

def fetchTorrents():
    options = {'sort': 'name'}
    result = requests.get(settings["qbt_url"] + '/torrents/info', cookies=qbt_cookie.cookies, params=options)
    try:
        json_data = result.json()
    except json.decoder.JSONDecodeError as e:
        print("ERROR: QBittorrent returned an invalid torrent list.")
        print("Cookies:", qbt_cookie.cookies)
        print("Response Status Code:", result.status_code)
        print('Response Text: ', result.text)
    return json_data
    
def is_process_running(process):
    for p in psutil.process_iter():
        try:
            if settings["qbt_client"] in p.exe():
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

    while True: #using break in exceptions - why not return though? gotta take a closer look at this later on
        file =  os.path.expandvars("%LOCALAPPDATA%/qBittorrent/BT_backup/") + hash + ".fastresume"
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
    auth = {"apikey" : settings["tvdb_apikey"]}

    result = requests.post(settings["tvdb_url"] + '/login', json=auth)
    if result.status_code != 200:
        print('TVDB AUTHENTICATION FAILED')
        print('TVDB Auth Response Status Code: ', result.status_code)
        print('TVDB Auth Response: ', result.text)
    else:
        tvdb_auth = result.json()['token']

def tvdb_getSeries(name):
    head = {"Authorization" : "Bearer " + tvdb_auth, "Accept-Language" : "en", "content-type" : "application/json"}
    data = {'name': name}
    result = requests.get(settings["tvdb_url"] + '/search/series', headers = head, params = data)
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
        for item in json_data['data']:
            series_options[i] = (str(item['id']), item['seriesName'])
            print(str(i) + ") " + series_options[i][1] + " (" + item['network'] + ")")
            i+=1
        while True:
            index = numericInput("Choose the correct series by index.\n>> ")
            try:
                print("You picked \"" + series_options[index][1] + "\". TheTVDB ID is " + series_options[index][0] + ".")
            except KeyError as e:
                print("Invalid input.")
                continue
            break
        
        return series_options[index]

def tvdb_getSingleEpisode(tvdb_id, season, episodeNumber):
    head = {"Authorization" : "Bearer " + tvdb_auth, "Accept-Language" : "en", "content-type" : "application/json"}
    data = {}
    if season == "-1":
        data = {'absoluteNumber': episodeNumber}
    else:
        episodeNumber = episodeNumber.lstrip('0') #episode number CAN be 0
        if not episodeNumber:   #empty strings are false
            episodeNumber = "0"
        data = {'airedSeason': season, 'airedEpisodeNumber': episodeNumber}
    result = requests.get(settings["tvdb_url"] + '/series/' + tvdb_id + '/episodes/query', headers = head, params = data)
    if result.status_code != 200:
        print("TVDB Episode Fetch Response Status Code: ", result.status_code)
        print("TVDB Episode Fetch Response: ", result.text)
        return
        
    for item in result.json()['data']:
        if (season != "-1" and item['airedEpisodeNumber'] == int(episodeNumber) and item['airedSeason'] == int(season) 
            or season == "-1" and item['absoluteNumber'] == int(episodeNumber)):
            return item
    raise TVDBEpisodeNumberNotInResult
        
def metadata_wizard(id, series_data):
    x_name = "Mob Psycho 100"
    x_patternA = r"^\[HorribleSubs\] Mob Psycho 100 - (\d\d) \[720p\]\.mkv"
    x_patternB = "Mob Psycho 100 - s\S\Se\E\E - [\A\A] \T - [2019 ENG-Sub AAC 720p HDTV x264 - HorribleSubs].mkv"
    
    sdata = {}
    patternA = ""
    patternB = ""
    #add new entry
    if id is -1:
        tvdb_series = {}
        while len(tvdb_series) == 0:
            name = input("Enter the name of the series.\nExample: " + x_name + "\n>> ")
            tvdb_series = tvdb_getSeries(name)
        id = tvdb_series[0]
        name = tvdb_series[1]
        
        if id in series_data.keys():
            if not booleanQuestion("Series ID " + id + " already has an entry named \"" + series_data[id]['name'] + "\". Add new pattern?\n>> "):
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
        for season, pattern_pairs in sdata['patterns'].items():
            for a, b in pattern_pairs.items():
                pattern_set_options[i] = (season, a)
                print(str(i) + ") " + a + " RENAMES TO " + b)
                i+=1
        while True:
            index = numericInput("Choose the pattern set you want to replace by index.\n>> ")
            try:
                patternA = pattern_set_options[index][1]
                patternB = sdata['patterns'][pattern_set_options[index][0]][pattern_set_options[index][1]]
                print("Pattern set \"{} : {}\" has been removed.".format(pattern_set_options[index][1], sdata['patterns'][pattern_set_options[index][0]].pop(pattern_set_options[index][1])))
            except KeyError as e:
                print("Invalid input.")
                continue
            break

    ep_patternA = re.compile(r".*\((?:\\d)+\).*")
    ep_patternB = re.compile(r".*(?:(?:\\E)|(?:\\A))+.*")
    while(True):
        new = ""
        if len(patternA) == 0:
            new = input("Enter unique regex for detection. Provide a capture group for the episode number. (e. g. (\d\d))\nExample: " + x_patternA + "\n>> ")
        else:
            new = input("Enter your new unique regex for detection. Provide a capture group for the episode number. (e. g. (\d\d))\nExample: " + x_patternA + "\nKeep empty to keep the current regex: " + patternA + "\n>> ")
            if len(new) == 0:
                new = patternA
        try:
            re.compile(new)
        except re.error as e:
            print("Invalid regex.", e)
            continue
        if not ep_patternA.match(new):
            print("Your regex pattern is missing a capture group for episode numbers. Episodes naturally have to be extinguishable by their seasonal or absolute episode numbers.")
            continue
        patternA = new
        break
    while(True):
        new = ""
        if len(patternB) == 0:
            new = input("Enter target file name. You must provide a tag for either seasonal or absolute episode numbers.\nExample: " + x_patternB + "\nValid tags:\n\S - Season Number\n\E - Seasonal Episode Number\n\A - Absolute Episode Number\n\T - Season Title\n>> ")
        else:
            new = input("Enter your new target file name. You must provide a tag for either seasonal or absolute episode numbers.\nExample: " + x_patternB + "\nValid tags:\n\S - Season Number\n\E - Seasonal Episode Number\n\A - Absolute Episode Number\n\T - Season Title\nKeep empty to keep the current pattern: " + patternB + "\n>> ")
            if len(new) == 0:
                new = patternB
        if not ep_patternB.match(new):
            print("Your filename is missing a capture group for episode numbers. Episodes naturally have to be extinguishable by their seasonal or absolute episode numbers.")
        patternB = new
        break;
    if booleanQuestion("Are episode numbers for this pattern set given per season or in absolute numbers? (s = seasonal; a = absolute)\n>> ", ['s',"seasonal", 'e', "episodic", 'y'], ['a',"absolute", 'n']):
        season = input("Enter the season number for this pattern set.\nExample for a Season 2: 2\n>> ")
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
        return clean_filename(filename_new)
        
def booleanQuestion(str, trues = ["y", "yes", '1', "true"], falses = ["n", "no", '0', "false"]):
    while(True):
        valid_answers = trues + falses
        answer = input(str).lower()
        if answer in valid_answers:
            if answer in trues:
                return True
            elif answer in falses:
                return False
        else:
            print("Invalid input.")
        
def numericInput(str):
    while(True):
        try:
            value = int(input(str))
        except ValueError as e:
            print("Invalid input.")
            continue
        return value
        
def actionRenameScan(series_data):
    torrents = fetchTorrents()
    hashes = []
    torrent_contents = {}
    
    if type(torrents) == list:
        for item in torrents:
            hashes.append(item['hash'])
            
    #fetch files in torrents
    i = 0
    for item in hashes:
        i+=1
        print("Fetching torrent " + str(i) + "/" + str(len(hashes)), end="\r")
        sys.stdout.flush()
        tc = fetchTorrentContent(item)
        torrent_contents = {**torrent_contents, **tc}
    print('\nFetching done.')

    #os.system("taskkill /im  {}".format(settings["qbt_client"].split('\\')[-1]))
    subprocess.call("taskkill /im  {}".format(settings["qbt_client"].split('\\')[-1]), shell=True)
    timer = 0
    while is_process_running(settings["qbt_client"]):
        time.sleep(1)
        timer+=1
        if timer >= 60:
            print("Error: Failed to terminate QBittorrent after 60 seconds.")
            return
        print(f"Waiting for QBittorrent to terminate... ({timer}s)", end='\r')
    print("\nQBittorrent has been terminated.")
        
    #check all files by regex in our series data
    for hash, file_data in torrent_contents.items():
        save_path = file_data[0]
        if save_path[-1] == '\\':   #remove trailing backslash for tidy string joins
            save_path = save_path[:-1]
        tor_files = []
        renameWholeBatch = False
        for file in file_data[1]:
            tor_files.append(file['name'])   #list of all filenames in torrent, used for fastresume manipulation, needed for batch torrents
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
                            if renameWholeBatch or booleanQuestion("Rename this?\n{}\n>> ".format('\\'.join(filter(None, [save_path, subpath, filename])))):
                                try:
                                    if not renameWholeBatch and len(tor_files) > 1 and booleanQuestion("Try to rename whole batch?\n>> "):
                                        renameWholeBatch = True
                                    filename_new = patternWizard(tvdb_id, season, patternA, patternB, filename)
                                    tor_files = [tor_file.replace('\\'.join(filter(None, [subpath, filename])), '\\'.join(filter(None, [subpath, filename_new]))) for tor_file in tor_files]
                                    renameTorrent(hash, save_path, subpath, filename, filename_new, tor_files)
                                except TVDBEpisodeNumberNotInResult:
                                    print("Failed to find an episode entry for this episode. Wait for TheTVDB to add this entry or rename the file by hand.")
    print("Restarting QBittorrent...")
    os.startfile(settings["qbt_client"])
    qbt_auth()
    return
        
def actionEdit(series_data):
    series_options = {}
    i = 0
    for key, value in series_data.items():
        series_options[i] = key
        print(str(i) + ") " + value['name'] + " (" + str(key) + ")")
        i+=1
    while True:
        index = numericInput("Choose the correct series by index.\n>> ")
        try:
            series_data = metadata_wizard(series_options[index], series_data)
        except KeyError as e:
            print("Invalid input.")
            continue
        break
    return series_data
    
def actionDelete(series_data):
    series_options = {}
    i = 0
    for key, value in series_data.items():
        series_options[i] = (key, value['name'])
        print(str(i) + ") " + value['name'] + " (" + str(key) + ")")
        i+=1
    index = numericInput("Choose the correct series by index.\n>> ")
    try:
        del series_data[series_options[index][0]]
    except KeyError:
        print("Error: Tried to remove an invalid series entry.")
        return
    print("Removed series data of " + series_options[index][1] + ".")
    return series_data
    
def writeSettings():
    with open(settings_file, 'w') as f:
        dump = json.dumps(settings, indent=4, sort_keys=False)
        f.write(dump)
    
def main():
    global settings
    settings = {}
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        file = open(settings_file, 'w')
    except json.decoder.JSONDecodeError:
        if not os.stat(settings_file).st_size == 0:
            print("Failed to read settings file. Check \"" + os.path.abspath(settings_file) + "\".")
            quit()
    if len(settings) == 0:
        print("\nHello there! Running first time setup. To edit these settings in the future check out the settings.json file next to the executable.\n")
        settings["qbt_version"] = "v4.1.6"
        settings["qbt_client"] = input("Enter the absolute path for the QBittorrent executable.\nExample: C:\\Program Files\\qBittorrent\\qbittorrent.exe\n>>")
        settings["qbt_username"] = input("Enter your login name for QBittorrent Web UI.\n>>")
        settings["qbt_password"] = input("Enter your login password for QBittorrent Web UI.\n>>")
        settings["qbt_url"] = input("Enter the URL to your QBittorrent Web API. (Keep empty for default)\nDefault: http://localhost:8080/api/v2\n>>")
        if len(settings["qbt_url"]) == 0:
            settings["qbt_url"] = "http://localhost:8080/api/v2"
        settings["tvdb_url"] = input("Enter the URL to the TheTVDB.com API. (Keep empty for default)\nDefault: https://api.thetvdb.com\n>>")
        if len(settings["tvdb_url"]) == 0:
            settings["tvdb_url"] = "https://api.thetvdb.com"
        #settings["tvdb_apikey"] = input("Enter your API Key for the TheTVDB.com API. (Keep empty for default)\n >>")
        settings["tvdb_apikey"] = "2323B61F3A9DA8C8"
        writeSettings()

    tvdb_auth()
    qbt_auth()
    
    qbt_version_cur = get_qbt_version()
    if settings["qbt_version"] != qbt_version_cur:
        if not booleanQuestion("WARNING: QBittorrent version mismatch: Got \"{}\", expected \"{}\". Compatibility is not ensured. \nContinue?\n>>".format(qbt_version_cur, settings["qbt_version"])):
            print("Exiting.")
            return
        else:
            if booleanQuestion("If you're sure your current version is supported we can set the supported version to your current one so you won't be warned again.\nDo it?\n>>"):
                settings["qbt_version"] = qbt_version_cur
                writeSettings()
    try:
        with open(series_data_file, 'r') as f:
            series_data = json.load(f)
    except FileNotFoundError:
        file = open(series_data_file, 'w')
        series_data = {}
    except json.decoder.JSONDecodeError:
        if not os.stat(series_data_file).st_size == 0:
            print("Failed to read series data. Check \"" + os.path.abspath(series_data_file) + "\".")
            quit()
        else:
            series_data = {}

    while True:
        job = numericInput("\n1) Scan for new episodes\n"
            "2) Add data of a new series\n"
            "3) Edit data of a series\n"
            "4) Delete data of a series\n"
            "0) Exit\n\nWhat to do?\n>> ")

        if job == 0:
            print("Exiting.")
            break
        elif job == 1:
            actionRenameScan(series_data)
        elif job == 2:
            result = metadata_wizard(-1, series_data)
            if result != None:
                series_data = result
        elif job == 3:
            result = actionEdit(series_data)
            if result != None:
                series_data = result
        elif job == 4:
            result = actionDelete(series_data)
            if result != None:
                series_data = result
        else:
            print("Invalid input.")
        with open(series_data_file, 'w') as f:
            dump = json.dumps(series_data, indent=4, sort_keys=True)
            f.write(dump)
main()