import re
from typing import List, Set
from pynput import keyboard
import subprocess
import psutil

from keymappings.converters import convert_to_readable_key

ENV = 'debug'

def debug_arguments(func):
    def wrapper(*args, **kwargs):
        print(*args, **kwargs)
        func(*args, **kwargs)

    return wrapper

def debug_print(*args, **kwargs):
    if ENV == 'debug':
        print(*args, **kwargs)


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
def run(shell_process: str) -> None:
    subprocess.call(shell_process, shell=True)

@with_decoration
@debug_arguments
def run_if_process_does_not_exist(shell_command: str, process: str) -> None:
    """
    Example:
        run_if_process_does_not_exist('Chrome', 'chrome.exe')
        run_if_process_does_not_exist('Chrome') # Will search for `Chrome.exe` and `chrome.exe`.

    :param shell_command: what to run.
    :param process: for which process to check.
    """
    running_processes = (p.name() for p in psutil.process_iter())

    if any(process_to_be_created in running_processes for process_to_be_created in
           [process, shell_command + '.exe', shell_command.upper() + '.exe']):
        debug_print(f'{shell_command} is already running')
        return

    run(shell_command)

class Keymapping:
    def __init__(self) -> None:
        self.KEYMAPPINGS = [{
            'key_sequences': [
                [{keyboard.Key.ctrl_l, keyboard.Key.alt_l, keyboard.Key.f4}],
            ],
            'command': 'TERMINATE',
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


pressed = []

START_MENU_PROGRAMS = 'C:\\Users\\ds13\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\'
km = Keymapping()
km.add_keymappings([
    {
        'key_sequences': [
            'ctrl_l + w',
        ],
        'command': lambda: print('TEST'),
    },
    {
        'key_sequences': [
            ['ctrl_l + w', 'ctrl_l + a'],
        ],
        'command': lambda: print('KEK'),
    }
]).add_keymappings([{
        'key_sequences': [
            'cmd + c',
        ],
        'command': lambda: run_if_process_does_not_exist('Chrome', 'chrome.exe'),
    },
    {
        'key_sequences': [
            'cmd + o',
        ],
        'command': lambda: run('Opera'),
    }
]).add_keymappings([{
        'key_sequences': [
            ['cmd + m', 'd'],
        ],
        'command': lambda:
        run_if_process_does_not_exist(f'{START_MENU_PROGRAMS}\\Discord Inc\\Discord', 'Discord.exe'),
    },
    {
        'key_sequences': [
            ['cmd + m', 't'],
        ],
        'command': lambda:
        run_if_process_does_not_exist(f'{START_MENU_PROGRAMS}\\Telegram Desktop\\Telegram', 'Telegram.exe'),
    },
    {
        'key_sequences': [
            ['cmd + m', 'o'],
        ],
        'command': lambda: print('Telegram!'),
    },
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
        for key_sequences in keymapping['key_sequences']:
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

    print('Result', matched_keymappings)
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
