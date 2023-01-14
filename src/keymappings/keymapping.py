from dataclasses import dataclass
import os
import re
from typing import List, Set
from pynput import keyboard

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
    def __init__(self) -> None:
        self.KEYMAPPINGS = {
            'ctrl+alt+f4': {
                'action': Action(command='TERMINATE'),
            }
        }


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
