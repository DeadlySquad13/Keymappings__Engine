import keyboard as k

from keymappings.user_layer import run_if_process_does_not_exist, run
from keymappings.keymapping import Action, Keymapping

START_MENU_PROGRAMS = 'C:\\Users\\ds13\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\'
km = Keymapping()
km.add_keymappings([
    {
        'key_sequences': [
            'ctrl+w',
        ],
        'command': lambda: print('TEST'),
    },
    {
        'key_sequences': [
            ['ctrl+w', 'ctrl+a'],
        ],
        'command': lambda: print('KEK'),
    }
]).add_keymappings([{
        'key_sequences': [
            'cmd+c',
        ],
        'command': lambda: run_if_process_does_not_exist('Chrome', 'chrome.exe'),
    },
    {
        'key_sequences': [
            'cmd+o',
        ],
        'command': lambda: run('Opera'),
    }
]).add_keymappings([{
        'key_sequences': [
            ['cmd+m', 'd'],
        ],
        'command': lambda:
        run_if_process_does_not_exist(f'{START_MENU_PROGRAMS}\\Discord Inc\\Discord', 'Discord.exe'),
    },
    {
        'key_sequences': [
            ['cmd+m', 't'],
        ],
        'command': lambda:
        run_if_process_does_not_exist(f'{START_MENU_PROGRAMS}\\Telegram Desktop\\Telegram', 'Telegram.exe'),
    },
    {
        'key_sequences': [
            ['cmd+m', 'o'],
        ],
        'command': lambda: print('Telegram!'),
    },
])

import ctypes  # An included library with Python install.


# At the moment of parsing.
km.KEYMAPPINGS |= {
    'ctrl+w': {
        'action': Action(command=lambda: print('TEST')),

        'ctrl+a': {
            'action': Action(command=lambda: print('KEK')),
        },
    },
    'o': {
        'action': Action(command=lambda: print('OOO')),
    },
    'ctrl+space': {
        'g': {
            'action': Action(command=lambda: run_if_process_does_not_exist('Chrome', 'chrome.exe')),
        },
        't': {
            'action': Action(command=lambda: k.call_later(lambda: ctypes.windll.user32.MessageBoxW(0, "Your text", "Your title", 1)))
        },
    },
    'cmd+o': {
        'action': Action(command=lambda: run('Opera')),
    },
    'cmd+m': {
        'd': {
            'action': Action(command=lambda:
                run_if_process_does_not_exist(f'{START_MENU_PROGRAMS}\\Discord Inc\\Discord', 'Discord.exe')
             ),
        },
        't': {
            'action': Action(command=lambda:
                run_if_process_does_not_exist(f'{START_MENU_PROGRAMS}\\Telegram Desktop\\Telegram', 'Telegram.exe')
             ),
        },
        'o': {
            'action': Action(command=lambda: print('Telegram!')),
        }
    },
}

