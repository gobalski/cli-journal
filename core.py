from colorama import Fore, Back, Style
import os
from pynput import keyboard
import my_functions as mf
import settings as set
import sys
if os.name != 'nt':
    import tty
    import termios


def edit():
    '''EDIT MODUS'''
    if set.inp_date not in set.jnl_dict:
        entry = mf.vim_input(set.EDITOR)
    else:
        entry = mf.vim_input(set.EDITOR, set.jnl_dict[set.inp_date])
    set.jnl_dict[set.inp_date] = entry


def filter():
    # figure out which entries to show (saved in display_keys)
    display_keys = []
    if len(set.dates) == 2:
        # display only intervall
        for key in set.jnl_dict:
            if set.min_date <= key and key <= set.max_date:
                display_keys.append(key)
    elif len(set.search_term) == 0:
        display_keys = list(set.jnl_dict.keys())

    # search in the range of display_keys for search_term
    if len(set.search_term) != 0:
        display_keys = list(set.jnl_dict.keys())
        bad_keys = []
        for key in display_keys:
            for word in set.search_term:
                if set.jnl_dict[key].find(word) == -1:
                    bad_keys.append(key)
                    break
        for bk in bad_keys:
            display_keys.remove(bk)
        if len(display_keys) == 0:
            answer = input('Nothing found.. display all entries (y/n)? ')
            if answer == 'y':
                display_keys = list(set.jnl_dict.keys())
            else:
                sys.exit()
    return display_keys


def make_code(str):
    if str == 'h':
        return 72
    elif str == 'l':
        return 76
    elif str == 'e':
        return 69
    elif str == 'q':
        return 81
    elif str == 'x':
        return 88
    else:
        return None


def process_key(EVENT_CODE):
    global display_keys
    global curr_date
    global curr_date_ind
    global quit
    global NoInput

    if EVENT_CODE is None:
        return display_keys, curr_date, curr_date_ind, quit, NoInput
    if EVENT_CODE == set.KEY_CODE_h:
        # previous entry
        curr_date_ind -= 1
        if curr_date_ind < len(display_keys) and curr_date_ind >= 0:
            curr_date = display_keys[curr_date_ind]
            NoInput = False
        else:
            curr_date_ind += 1
    if EVENT_CODE == set.KEY_CODE_l:
        # next entry
        curr_date_ind += 1
        if curr_date_ind < len(display_keys) and curr_date_ind >= 0:
            curr_date = display_keys[curr_date_ind]
            NoInput = False
        else:
            curr_date_ind -= 1
    if EVENT_CODE == set.KEY_CODE_e:
        # edit current entry
        entry = mf.vim_input(set.EDITOR, set.jnl_dict[curr_date])
        set.jnl_dict[curr_date] = entry
        NoInput = False
    if EVENT_CODE == set.KEY_CODE_x:
        # delete current entry
        answer = input(
            'Do you really want to delete this entry? (y/n) ')
        if answer == 'y':
            del set.jnl_dict[curr_date]
            del display_keys[curr_date_ind]
            if curr_date_ind != 0:
                curr_date_ind -= 1
            else:
                curr_date_ind = 0
            curr_date = display_keys[curr_date_ind]
        NoInput = False
    if EVENT_CODE == set.KEY_CODE_q:
        # quit the app
        quit = True
        NoInput = False
        mf.clear()


def browse():
    global display_keys
    global curr_date
    global curr_date_ind
    global quit
    global NoInput

    if set.inp_date not in set.jnl_dict and set.inp_date != '':
        answer = input(
            'no entry for given date.. shall i create one? (y/n) ')
        if answer == 'y':
            entry = mf.vim_input(set.EDITOR)
            set.jnl_dict[set.inp_date] = entry
        else:
            set.inp_date = ''

    display_keys = filter()

    # get a curr_date to display the journal entry.
    curr_date = display_keys[-1]
    if set.inp_date != '':
        curr_date = set.inp_date
    curr_date_ind = display_keys.index(curr_date)

    # Display/Event loop
    quit = False
    terms = str(set.search_term).replace('\'', '')

    if os.name == 'nt':
        # start keyboard listener
        listener = keyboard.Listener()
        listener.start()

    while not quit:
        NoInput = True
        mf.clear()
        print(Fore.BLACK + Back.WHITE
              + ' h: previous entry | l: next entry | e: edit entry | '
              'x: delete entry | q: save & exit ')
        print(Style.RESET_ALL)
        print(f'SEARCH FILTER: {terms[1:-1]}')
        print(f'DATE FILTER: {set.min_date} - {set.max_date}')
        print(Fore.BLACK + Back.WHITE)
        print(' ', end='')
        print(curr_date, end='')
        total_entries = len(display_keys)
        print(f'    ({curr_date_ind + 1}/{total_entries}) ')
        print()
        print(Style.RESET_ALL + set.jnl_dict[curr_date])
        while NoInput:
            if os.name == 'nt':
                with keyboard.Events() as events:
                    event = events.get(0.05)
                    mf.flush_input()
                    try:
                        EVENT_CODE = event.key.vk
                    except AttributeError:
                        EVENT_CODE = None
            else:
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                EVENT_CODE = make_code(ch)
            process_key(EVENT_CODE)
    # stop keyboard listener
    if os.name == 'nt':
        listener.stop
    mf.flush_input()
