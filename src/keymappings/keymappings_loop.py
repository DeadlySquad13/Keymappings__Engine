import os
from typing import Tuple
from dataclasses import dataclass
from functools import reduce
import keyboard as k

from keymappings.debug import debug_print

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
class KeymappingsLoop:
    initial_parsed_keymappings: dict

    children_keymappings = {}
    pressed = set()

    def __post_init__(self):
        self.children_keymappings = self.initial_parsed_keymappings

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
            self.children_keymappings = self.initial_parsed_keymappings
            return

        matched = filter(self.is_key_or_combination, matched_keymappings.keys())
        # print('matched', list(matched))
        debug_print('children', self.children_keymappings)

        self.children_keymappings: dict = reduce(lambda accumulator, match: accumulator | self.children_keymappings[match], matched, {}) or self.initial_parsed_keymappings
        debug_print('children', self.children_keymappings)

        for keymapping in matched_keymappings.values():
            print('keymapping', keymapping)
            action = keymapping.get('action')

            if not action:
                debug_print('No action found!')
                continue

            action.exec()


    def on_press_hook(self, event: k.KeyboardEvent):
        debug_print('--------------------------------------')
        debug_print('pressed:', event.name)
        matched_keymappings = self.match_keymappings(event.scan_code, self.children_keymappings)

        # No keymappings found, no keys are held, we are no longer expecting chord parts.
        if not matched_keymappings and not self.key_is_held():
            self.children_keymappings = self.initial_parsed_keymappings
            
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

