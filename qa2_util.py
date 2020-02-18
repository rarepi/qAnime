import os

# 0 = No debug output
# 1 = small stuff?
# 2 = full json data dumps
DEBUG_OUTPUT_LEVEL = 2

SERIES_DATA_FILE = "./data.json"
SETTINGS_FILE = "./settings.json"
os.makedirs(os.path.dirname(SERIES_DATA_FILE), exist_ok=True)
os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)


def debug(output, level):
    if DEBUG_OUTPUT_LEVEL >= level:
        print(output)


def clean_filename(filename):
    illegal_characters = '\\"/:<>?|'
    rem_ill_chars = str.maketrans(illegal_characters, '_' * len(illegal_characters))
    return filename.translate(rem_ill_chars)


def input_bool(text, trues=("y", "yes", '1', "true"), falses=("n", "no", '0', "false")):
    valid_answers = trues + falses
    while True:
        answer = input(text).lower()
        if answer in valid_answers:
            if answer in trues:
                return True
            elif answer in falses:
                return False
        else:
            print("Invalid input.")


def input_int(text):
    while True:
        try:
            value = int(input(text))
        except ValueError:
            print("Invalid input.")
            continue
        return value