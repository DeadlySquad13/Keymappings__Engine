import re
from typing import List, Set
from pynput import keyboard
import subprocess

from keymappings.converters import convert_to_readable_key

def debug_arguments(func):
    def wrapper(*args, **kwargs):
        print(*args, **kwargs)
        func(*args, **kwargs)

    return wrapper


def with_decoration(func):
    def wrapper(*args, **kwargs):
        print('-----------')
        func(*args, **kwargs)
        print('-----------')

    return wrapper

def wrap_into_list_if_not_already(item) -> List:
    return item if type(item) == list else [item]


@with_decoration
@debug_arguments
def run(s: str) -> None:
    # subprocess.Popen(s)
    subprocess.call(s, shell=True)

class Keymapping:
    def __init__(self) -> None:
        self.KEYMAPPINGS = [{
            "key_sequences": [
                [{keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.f4}],
            ],
            "command": "TERMINATE",
        }]


    SPECIAL_CHARS = [' ', '+']

    def parse_keymapping_str_notation(self, keymapping: str) -> List[set]:
        """Parse user defined string into usable structure of chars.

        `if type(keymmapings) == dict: keymapping = 'kek'`
        :param keymapping: user defined keymapping
            e.g.: 'c', 'a+w', 'ctrl_l + w'
        :type keymapping: str 
        :return: structure of parsed chars
            e.g.: ['c'], [{'a', 'w'}], [{ 'ctrl_l', 'w' }]
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

    def add_keymappings(self, keymappings: list | dict):
        """Standardize structure and decode, then add to the keymappings list.

        :param keymappings: 
        :return: self
        :rtype: Keymapping
        """
        # Standardize structure: we can get either one keymapping or multiple keymappings.
        if type(keymappings) != list:
            keymappings = [keymappings]

        # Decode string notation and standardize structure: key_sequence can be either a
        #   single key chord or a list of key chords.
        for keymapping in keymappings:
            keymapping['key_sequences'] = [[kc if type(kc) != str else
                                            self.decode_keymapping_str_notation(kc)
                                            for kc in
                                             wrap_into_list_if_not_already(key_sequence)] for
                                            key_sequence in keymapping['key_sequences']]

        self.KEYMAPPINGS += keymappings

        return self


pressed = []
km = Keymapping()
km.add_keymappings([
    {
        "key_sequences": [
            # [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="w")}],
            'ctrl_l + w',
            # [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="W")}],
        ],
        "command": lambda: print("TEST"),
    },
    {
        "key_sequences": [
            ['ctrl_l + w', 'ctrl_l + a'],
        ],
        "command": lambda: print("KEK"),
    }
]).add_keymappings([{
        "key_sequences": [
            'cmd + c',
        ],
        "command": lambda: run("Chrome"),
    },
    {
        "key_sequences": [
            'cmd + o',
        ],
        "command": lambda: run("Opera"),
    }
])


def match_keymappings(key, keymappings, matched_sequences):
    matched_keymappings = []

    print('key', key)
    try:
        print('key_vk', key.vk)
    except:
        pass

    if (not convert_to_readable_key(key) in pressed):
        pressed.append(convert_to_readable_key(key))

    print(pressed)

    for keymappings_index, keymapping in enumerate(keymappings):
        for key_sequences in keymapping["key_sequences"]:
            chord = key_sequences[matched_sequences[keymappings_index]]

            # if chord.issubset(pressed):
            if all(key in pressed for key in chord):
                matched_sequences[keymappings_index] += 1

                # Sequences has ended.
                if matched_sequences[keymappings_index] == len(key_sequences):
                    matched_sequences[keymappings_index] = 0
                    matched_keymappings.append(keymapping)
                    matched_sequences[keymappings_index] = 0

            # Sequence was interrupted.
            else:
                matched_sequences[keymappings_index] = 0

    print("Result", matched_keymappings)
    return matched_keymappings

def main():
    # [index: chord_index]
    # Example:
    #   [
    #       0: 1, # On first keymapping (e.g., [Ctrl+Alt+A, Ctrl-B]) first chord (Ctrl+Alt+A) was matched.
    #       1: 0, # Second keymapping wasn't matched yet.
    #   ]
    matched_sequences = [0 for _ in km.KEYMAPPINGS]

    def on_press(key):
        for c in match_keymappings(key, km.KEYMAPPINGS, matched_sequences):
            command = c["command"]

            if command == 'TERMINATE':
                return False

            command()


    def on_release(key):
        my_key = convert_to_readable_key(key) 

        if my_key in pressed:
            pressed.remove(my_key)

    # Collect events until released.
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == '__main__':
    main()
