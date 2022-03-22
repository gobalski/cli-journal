"""
Beispielhafter Aufruf: journal.py [MODE] my_journal [KEYS]
    MODE: -e Edit: journal.py -e my_journal [KEYS]
                KEYS ist ein Datum. Wenn keine KEYS geben sind,
                wird das heutige Datum gesetzt.
                Zusätliche Keys wie Suchbegriffe oder weitere Daten werden
                ignoriert.
          -b Browse: journal.py [-b] my_journal [KEYS]
                Browse ist der Standardmodus
                KEYS ist eine Reihe von Begriffen. Daten der Form YYYY-MM-DD
                werden erkannt, der Rest werden als Strings nach denen das
                Journal durchsucht wird weitergegeben.
                Wird ein Datum angeben, wird der Eintrag angezeigt oder falls
                der noch nicht vorhanden ist, kann ein neuer erstellt werden.
                Werden zwei Daten angeben werden alle Einträge in diesem
                Berreich angezeigt. Dies kann auch mit Suchbegriffen kombi-
                niert werden.
          -p setPassword: Erstellt ein neues Password für das gegebene Journal.
"""

import core
import settings as set

set.parse()
set.process_dates()
set.loadJournal()

try:
    if set.setPassword:
        set.set_password()
        set.MODE = 'done'
    if set.MODE == 'browse':
        core.browse()
    elif set.MODE == 'edit':
        core.edit()
except Exception as e:
    print(e)
finally:
    print('See you soon..')
    set.writeJournal()
