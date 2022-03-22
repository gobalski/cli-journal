import tempfile
from subprocess import run
import os


def vim_input(EDITOR, entry=None) -> str:
    """
    entry: str
    Erwartet entweder None oder str und gibt einen str aus.
    Das Output wird vom User in vim eingeben, dafür wird ein
    temporäres File angelegt.
    Wenn entry nicht None ist, wird entry in vim dargestellt und der User
    kann den entry bearbeiten.
    """

    tmp = tempfile.NamedTemporaryFile(mode='w+', dir='', delete=False)
    try:
        if entry is not None:
            tmp.write(entry)
            tmp.flush()
            tmp.close()
            run([EDITOR, tmp.name])
        else:
            run([EDITOR, '-c', 'startinsert', tmp.name])
        tmp = open(tmp.name, 'r')
        res = tmp.read()
        tmp.close()
    finally:
        # TODO: OVERWRITE tmp WITH JIBBERISH
        os.unlink(tmp.name)
    # clean up vim files:
    try:
        os.remove(tmp.name + '~')
        os.remove(tmp.name[0:-11] + '.' + tmp.name[-11:] + '.un~')
    finally:
        return res


def str_2_dict(dict_str: str):
    """ Converts a string of the form
    '{'key1': 'value1', 'key2': 'value2', ...}'
    into the corresponding dictionary """
    # get rid of escaped backslashes in dict_str:
    # basically replacing '\\' with '\'
    dict_str_dec = decode(dict_str[1:-1])
    # split dict_str into the actual information
    dict_str_lst = dict_str_dec.split('\'')[1::2]
    # store it in an dictionary object
    dict = {}
    length = len(dict_str_lst)
    for i in range(0, length, 2):
        dict[dict_str_lst[i]] = dict_str_lst[i+1]
    return dict


def decode(string):
    return string\
        .replace('\\n', '\n')\
        .replace('\\t', '\t')\
        .replace('\\r', '\r')\
        .replace('\\b', '\b')\
        .replace('\\f', '\f')


# define a clear function
def clear():
    # for windows
    if os.name == 'nt':
        os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        os.system('clear')


# flush stdin system independently.
def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys
        import termios  # for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
