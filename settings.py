import argparse
from colorama import Fore, Style
from datetime import date
import io
import getpass
import os
import re
import sys
import crypto as cr
import my_functions as mf


# Define some Configurations:
# for windows
if os.name == 'nt':
    # EDITOR = r'C:\Program Files\Typora\Typora.exe'
    EDITOR = r'C:\Program Files (x86)\Vim\vim82\vim.exe'
# for mac and linux
else:
    EDITOR = 'vim'

KEY_CODE_h = 72
KEY_CODE_l = 76
KEY_CODE_e = 69
KEY_CODE_q = 81
KEY_CODE_x = 88
DEF_MODE = 'browse'  # default MODE


def parse():
    global DEF_MODE
    # Read arguments and define MODE, dates, filename, search_term
    # Define arguments
    parser = argparse.ArgumentParser()
    # TODO define the two flags as booleans.
    parser.add_argument("-e", "--edit",
                        action='store_true',
                        required=False,
                        help='Starts the program in edit mode')
    parser.add_argument("-b", "--browse",
                        action='store_true',
                        required=False,
                        help='Starts the program in browse mode')
    parser.add_argument("-p", "--setPassword",
                        action='store_true',
                        required=False,
                        help='Sets a new password for a given journal')
    parser.add_argument("FILE",
                        type=str,
                        help='The filename of the journal. '
                        'If it does not exit it '
                        'will be created')
    parser.add_argument("KEYS",
                        type=str,
                        nargs='*',
                        help='Can be empty, one date, two dates, '
                        'or each of those '
                        'but with search terms (str)')
    args = parser.parse_args()

    # parse MODE
    global MODE
    global setPassword
    setPassword = False
    if not args.edit and not args.browse:
        MODE = DEF_MODE
    elif args.edit and args.browse:
        print(f'Two modes passed.. entering {DEF_MODE} mode')
        MODE = DEF_MODE
    elif args.edit:
        MODE = 'edit'
    elif args.browse:
        MODE = 'browse'
    if args.setPassword:
        setPassword = True
    # parse FILE
    global filename
    filename = args.FILE

    # parse KEYS
    global dates
    global search_term
    dates = []
    search_term = []
    for k in args.KEYS:
        if re.match(r'^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$', k):
            year = int(k[0:4])
            month = int(k[5:7])
            day = int(k[8:10])
            dates.append(date(year, month, day))
        else:
            search_term.append(k)


def process_dates():
    # process date input
    global min_date
    global max_date
    global inp_date
    global MODE
    global search_term
    min_date = ''
    max_date = ''
    inp_date = ''
    # if search_term != '' and len(dates) == 0:
    #     print('No valid dates passed, ignoring and '
    #           f'searching for \'{search_term}\'')
    if len(dates) == 0:
        if len(search_term) == 0:
            print('No valid date passed, assuming today.. ', date.today())
            inp_date = date.today()
    elif len(dates) == 1:
        inp_date = dates[0]
    elif len(dates) == 2:
        if dates[0] < dates[1]:
            min_date = dates[0]
            max_date = dates[1]
        elif dates[0] > dates[1]:
            min_date = dates[1]
            max_date = dates[0]
        else:
            inp_date = dates[0]
            dates.remove(dates[1])
        if MODE == 'edit':
            print(f'its not possible to edit two dates.. will edit {dates[0]}')
            inp_date = dates[0]
    else:
        print('to many dates passed.. I\'m confused.. canceling..')
        sys.exit()


def loadJournal():
    # Check if filename exits if not create it.
    # Load encrypted data
    try:
        with open(filename, 'r', encoding='utf8') as f:
            jnl_str_enc = f.read()
    except NameError:
        print('No filename parsed!')
        sys.exit()
    except FileNotFoundError:
        print('Creating new journal file..')
        with open(filename, 'w+', encoding='utf8') as f:
            jnl_str_enc = f.read()

    # Managing empty/new Journal files. If empty user chooses a password
    # else: decrypt existing file
    if jnl_str_enc == '':
        set_password()
        jnl_str = jnl_str_enc
    else:
        global password
        password = getpass.getpass("Enter your password:")
        jnl_dict_enc = mf.str_2_dict(jnl_str_enc)
        try:
            jnl_str = cr.decrypt(jnl_dict_enc, password).decode()  # DECRYPTION
        except Exception as e:
            print(Fore.RED, end='')
            print('Decryption went wrong.. wrong password?')
            print(e)
            print(Style.RESET_ALL, end='')
            sys.exit()

    jnl_dict_tmp = mf.str_2_dict(jnl_str)
    global jnl_dict
    jnl_dict = {}
    # convert keys to date objects
    for key in jnl_dict_tmp:
        year = int(key[0:4])
        month = int(key[5:7])
        day = int(key[8:10])
        jnl_dict[date(year, month, day)] = jnl_dict_tmp[key]
    del jnl_dict_tmp


def set_password():
    pswd_set = False
    while not pswd_set:
        password1 = getpass.getpass("Set your password: ")
        password2 = getpass.getpass("Repeat your password: ")
        if password1 != password2:
            print('passwords not the same..')
        elif password1 == '':
            print('password can\'t be emtpy..')
        else:
            print('password set!')
            pswd_set = True
    global password
    password = password1
    del password1, password2


def writeJournal():
    global jnl_dict
    global filename
    global password
    # save dict in file as string and encrypt it
    # convert date object keys into strings.
    jnl_str_tmp = {}
    jnl_dict_sorted = sorted(jnl_dict)  # sort the keys
    for key in jnl_dict_sorted:
        jnl_str_tmp[str(key)] = jnl_dict[key]
    with io.open(filename, 'w', encoding='utf8') as file:
        data_str = repr(jnl_str_tmp)
        data_dict_enc = cr.encrypt(data_str, password)  # ENCRYPTION
        data_str_enc = repr(data_dict_enc)
        file.write(data_str_enc)
        file.close()
