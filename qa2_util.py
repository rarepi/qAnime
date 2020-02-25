# 0 = No debug output
# 1 = small stuff?
# 2 = full json data dumps
DEBUG_OUTPUT_LEVEL = 2

CHARSET_ILLEGAL_FILENAME = '\\"/:<>?|'
CHARSET_REGEX_ESCAPES = '+*?^$\\.[]{}()|/'


def debug(*args, level=1):
    if DEBUG_OUTPUT_LEVEL >= level:
        print(*args)


def clean_filename(filename):
    rem_ill_chars = str.maketrans(CHARSET_ILLEGAL_FILENAME, '_' * len(CHARSET_ILLEGAL_FILENAME))
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