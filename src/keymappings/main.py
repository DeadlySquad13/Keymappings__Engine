import os
import re
from typing import List, Set, Tuple
from dataclasses import dataclass
from pynput import keyboard
from functools import reduce
import keyboard as k
import subprocess
import psutil

# from keymappings.converters import convert_to_readable_key

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

@dataclass
class Action:
    command: str

    def exec(self):
        if self.command == 'TERMINATE':
            return os._exit(0)

        self.command()

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

def P(args):
    print(args)

    return args

@dataclass
class Key:
    name: str
    scan_codes: Tuple[int]

    @classmethod
    def from_keyboard_event(self, event: k.KeyboardEvent):
        return self(event.name, (event.scan_code,))

    def __eq__(self, other: object) -> bool:
        """At least one scan code should match. When we type we get one
        scan_code, when we parsed_keymapping - tuple of all possible.
        """
        # return any(scan_code in other.scan_codes for scan_code in self.scan_codes)
        return any(scan_code in other.scan_codes for scan_code in self.scan_codes)

@dataclass
class KeySequence:
    sequence: List[Key]

# [index: chord_index]
# Example:
#   [
#       0: 1, # On first keymapping (e.g., [Ctrl+Alt+A, Ctrl-B]) first chord (Ctrl+Alt+A) was matched.
#       1: 0, # Second keymapping wasn't matched yet.
#   ]
# matched_sequences = [0 for _ in km.KEYMAPPINGS]

@dataclass
class KeymappingsLoop:
    children_keymappings = KEYMAPPINGS_TREE
    pressed = set()

    def key_is_held(self):
        return len(self.pressed) > 1

    def is_key_or_combination(self, value):
        # Make regex?
        return not (value == 'action' or value == 'description')

    def match_keymappings(self, key, keymappings: dict):
        print(keymappings)
        matched_keymappings = {}

        if (not key in self.pressed):
            self.pressed.add(key)

        print('pressed', self.pressed)

        for current, children in keymappings.items():
            # sequence = k.parse_hotkey('ctrl+w,a')
            if not self.is_key_or_combination(current):
                continue
            chord = k.parse_hotkey(current)[0] # It parses it as combination so we take first element as we always give it a chord.
            print('chord', chord)

            if all(any(key in possible_scan_codes for key in self.pressed) for
                   possible_scan_codes in chord):
                matched_keymappings[current] = children
                print('^This chord was matched!')

            # chord_keys = (Key('', possible_scan_codes) for possible_scan_codes in chord)
            # pressed_keys = (Key('', (scan_code,)) for scan_code in pressed)
            # print(list(pressed_keys), list(chord_keys))

        # matched_keymappings: dict = reduce(lambda accumulator, match: accumulator | keymappings[match], matched, {})

        return matched_keymappings # A subset of a keymappings.


    def on_match_keymappings(self, matched_keymappings):
        # No keymappings found
        if not matched_keymappings:
            #   Some key is held, wait until it's released. Maybe next key will
            # complete the chord
            if self.key_is_held():
                return

            # No keys are held, we are no longer expecting chord parts.
            self.children_keymappings = KEYMAPPINGS_TREE
            return

        matched = filter(self.is_key_or_combination, matched_keymappings.keys())
        # print('matched', list(matched))
        print('children', self.children_keymappings)
        # self.children_keymappings: dict = reduce(lambda accumulator, match: accumulator | P(self.children_keymappings[match]), matched, {}) # or KEYMAPPINGS_TREE

        self.children_keymappings: dict = reduce(lambda accumulator, match: accumulator | self.children_keymappings[match], matched, {}) or KEYMAPPINGS_TREE
        print('children', self.children_keymappings)

        for keymapping in matched_keymappings.values():
            print('keymapping', keymapping)
            action = keymapping.get('action')

            if not action:
                debug_print('No action found!')
                continue

            action.exec()


    def on_press_hook(self, event: k.KeyboardEvent):
        print('--------------------------------------')
        print('pressed:', event.name)
        matched_keymappings = self.match_keymappings(event.scan_code, self.children_keymappings)

        # No keymappings found
        if not matched_keymappings and not self.key_is_held():
            self.children_keymappings = KEYMAPPINGS_TREE
            # No keys are held, we are no longer expecting chord parts.
            matched_keymappings = self.match_keymappings(event.scan_code, self.children_keymappings)

        self.on_match_keymappings(matched_keymappings)

        key = event.scan_code

        # Hack for not registered windows key
        #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
        if key == 91:
            return k.press('left windows')

        k.press(key)

    def on_release_hook(self, event: k.KeyboardEvent):
        key = event.scan_code
        if key in self.pressed:
            self.pressed.remove(key)

        # Hack for not registered windows key
        #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
        if key == 91:
            return k.release('left windows')

        k.release(key)

    def on_event(self, event: k.KeyboardEvent):
        if event.name == '[':
            return os._exit(0)

        if event.event_type == 'down':
            self.on_press_hook(event)
        else:
            self.on_release_hook(event)


def main():
    loop = KeymappingsLoop()
    k.hook(loop.on_event, suppress=True)


    k.wait()

    # def on_press(key):
    #     for c in match_keymappings(key, km.KEYMAPPINGS, matched_sequences):
    #         command = c['command']

    #         if command == 'TERMINATE':
    #             return False

    #         command()


    # # Collect events until released.
    # with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    #     listener.join()


if __name__ == '__main__':
    main()
