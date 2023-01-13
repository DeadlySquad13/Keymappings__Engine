from dataclasses import dataclass
import os
import re
from typing import List, Set
from pynput import keyboard

from keymappings.user_layer import run_if_process_does_not_exist, run

def wrap_into_list_if_not_already(item) -> List:
    return item if type(item) == list else [item]

@dataclass
class Action:
    command: str

    def exec(self):
        if self.command == 'TERMINATE':
            return os._exit(0)

        self.command()


class Keymapping:
    # At the moment of parsing.
    KEYMAPPINGS_TREE = {
        'ctrl+w': {
            'action': Action(command=lambda: print('TEST')),

            'ctrl+a': {
                'action': Action(command=lambda: print('KEK')),
            },
        },
        'o': {
            'action': Action(command=lambda: print('OOO')),
        },
        'cmd+c': {
            'action': Action(command=lambda: run_if_process_does_not_exist('Chrome', 'chrome.exe')),
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

    def __init__(self) -> None:
        self.KEYMAPPINGS = [{
            'key_sequences': [
                [{keyboard.Key.ctrl, keyboard.Key.alt_l, keyboard.Key.f4}],
            ],
            'command': 'TERMINATE',
        }]


    SPECIAL_CHARS = [' ', '+']

    def parse_keymapping_str_notation(self, keymapping: str) -> List[set]:
        """Parse user defined string into usable structure of chars.

        `if type(keymmapings) == dict: keymapping = 'kek'`
        :param keymapping: user defined keymapping
            e.g.: 'c', 'a+w', 'ctrl+w'
        :type keymapping: str 
        :return: structure of parsed chars
            e.g.: ['c'], [{'a', 'w'}], [{ 'ctrl', 'w' }]
        :rtype: List[set]
        """

        chars = { k for k in re.split(r'\s*\+\s*', keymapping) }

        decoded_keymapping = chars

        return decoded_keymapping


    def decode_keymapping_str_notation(self, keymapping: str) -> Set[keyboard.Key | keyboard.KeyCode]:
        """Decode user defined string into more usable structure.

        :param keymapping: user defined string.
        :return: set of keys pressed (keyboard.Key or keyboard.KeyCode instances).
        """
        parsed_keymapping = self.parse_keymapping_str_notation(keymapping)

        return { keyboard.Key[char] if char in keyboard.Key._member_names_ else
                keyboard.KeyCode(char=char) for char in parsed_keymapping }

    def _add_keymappings(self, keymappings: list | dict):
        """Standardize structure and decode, then add to the keymappings list.

        :param keymappings: 
        :return: self
        :rtype: Keymapping
        """
        # Standardize structure: we can get either one keymapping or multiple keymappings.
        if type(keymappings) != list:
            keymappings = [keymappings]

        # Decode string notation and standardizing structure: key_sequence can be either a
        #   single key chord or a list of key chords.
        for keymapping in keymappings:
            keymapping['key_sequences'] = [[kc if type(kc) != str else
                                            self.decode_keymapping_str_notation(kc)
                                            for kc in
                                             wrap_into_list_if_not_already(key_sequence)] for
                                            key_sequence in keymapping['key_sequences']]

        self.KEYMAPPINGS += keymappings

        return self

    def add_keymappings(self, keymappings: list | dict):
        return self
        keymappings = wrap_into_list_if_not_already(keymappings)

        for keymapping in keymappings:
            for key_sequence in keymapping['key_sequences']:
                if type(key_sequence) == list:
                    debug_print('Adding sequence of chords')
                else:
                    k.add_hotkey(key_sequence, keymapping['command'],
                                 suppress=True, trigger_on_release=True)

        return self


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
