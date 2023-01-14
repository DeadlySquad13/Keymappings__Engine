from typing import List, Optional, Self, Set, Tuple
from dataclasses import dataclass
from functools import reduce
import keyboard as k

from keymappings.debug import debug_print

class Key:
    _name: str
    _scan_codes: Tuple[int]

    def __init__(self, name, scan_codes) -> None:
        self._name = name
        self._scan_codes = scan_codes

    @property
    def name(self):
        return self._name

    @property
    def scan_codes(self):
        return self._scan_codes

    def __str__(self) -> str:
        return f'{{name: {self.name}, scan_codes: {self.scan_codes}}}'

    def __repr__(self) -> str:
        return f'Key({self.name}, {self.scan_codes})'

    def __eq__(self, pressed_key: Self) -> bool:
        """At least one scan code should match.
        When we type we get one scan_code, when we parsed_keymapping - tuple of all possible codes.
        """
        return any(scan_code in self.scan_codes for scan_code in pressed_key.scan_codes)

    def __key__(self):
        return self.scan_codes

    def __hash__(self):
        return hash(self.__key__())

    @classmethod
    def from_keyboard_event(self, event: k.KeyboardEvent):
        return self(event.name, (event.scan_code,))


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
        # Make regex to check if it's a key instead of checking fields?
        return not (value == 'action' or value == 'description')

    def chords_are_equal(self, left: List[Key], right: Set[Key]):
        # return all( # All keys in chords should match.
        #            any(key in left_key.scan_codes for key in right) # But there're multiple variants of the key representation. Match with any of them.
        #                for left_key in left
        #           )
        return all( # All keys in chords should match.
                   any(key == left_key for key in right)
                       for left_key in left
                  )

    def match_keymappings(self, key: Key, keymappings: dict) -> dict:
        """

        :param key: 
        :param keymappings: 
        :return: matched_keymappings - A subset of keymappings
        """
        print(keymappings)
        matched_keymappings = {}

        if not key in self.pressed:
            self.pressed.add(key)

        print('pressed', self.pressed)

        for current, children in keymappings.items():
            # sequence = k.parse_hotkey('ctrl+w,a')
            if not self.is_key_or_combination(current):
                continue

            current_chord = k.parse_hotkey(current)[0] # It parses it as combination so we take first element as we always give it a chord.
            # debug_print('chord', current_chord)
            current_chord = list(map(lambda scan_codes: Key('', scan_codes=scan_codes), current_chord))

            if self.chords_are_equal(current_chord, self.pressed):
                matched_keymappings[current] = children
                # print('^This chord was matched!')

            # chord_keys = (Key('', possible_scan_codes) for possible_scan_codes in chord)
            # pressed_keys = (Key('', (scan_code,)) for scan_code in pressed)
            # print(list(pressed_keys), list(chord_keys))

        return matched_keymappings


    def on_match_keymappings(self, matched_keymappings):
        # No keymappings found.
        if not matched_keymappings:
            #   Some key is held, wait until it's released. Maybe next key will
            # complete the chord.
            if self.key_is_held():
                return False

            # No keys are held, we are no longer expecting chord parts.
            self.children_keymappings = self.initial_parsed_keymappings
            return False

        matched = filter(self.is_key_or_combination, matched_keymappings.keys())
        # print('matched', list(matched))
        # debug_print('children', self.children_keymappings)

        self.children_keymappings: dict = reduce(
                lambda accumulator, match: accumulator | self.children_keymappings[match],
                matched,
                {}
            ) or self.initial_parsed_keymappings

        # debug_print('children', self.children_keymappings)

        for keymapping in matched_keymappings.values():
            print('keymapping', keymapping)
            action = keymapping.get('action')

            if not action:
                debug_print('No action found!')
                continue

            action.exec()

        return True

    current_sequence = []

    def on_press_hook(self, event: k.KeyboardEvent):
        debug_print('--------------------------------------')
        debug_print('pressed:', event.name)
        key = Key.from_keyboard_event(event)
        self.current_sequence.append(key)
        matched_keymappings = self.match_keymappings(key, self.children_keymappings)

        #   No children combinations found, no keys are held, we are no longer
        # expecting chord parts.
        #   Maybe user started typing new sequence. Try again but on root level
        # if we are not already on root level.
        if not matched_keymappings and not self.key_is_held() and len(self.current_sequence) > 1:
            self.children_keymappings = self.initial_parsed_keymappings
            
            matched_keymappings = self.match_keymappings(key, self.children_keymappings)

        # No keymappings found.
        if not self.on_match_keymappings(matched_keymappings):
            print('sequence:',self.current_sequence)
            # Send all accumulated keys.
            for key in self.current_sequence:
                # Hack for not registered windows key
                #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
                if key.scan_codes == (91,):
                    return k.press('left windows')

                k.press(key.scan_codes[0])

            self.current_sequence = []

            return

    def on_release_hook(self, event: k.KeyboardEvent):
        key = Key.from_keyboard_event(event)

        if key in self.pressed:
            self.pressed.remove(key)

        # Hack for not registered windows key
        #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
        if key.scan_codes == (91,):
            return k.release('left windows')

        k.release(key.scan_codes[0])

    def on_event(self, event: k.KeyboardEvent):
        if event.event_type == 'down':
            self.on_press_hook(event)
        else:
            self.on_release_hook(event)

