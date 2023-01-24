from dataclasses import dataclass, field
from functools import reduce
from typing import List, Set
import keyboard as k
from queue import SimpleQueue

from keymappings.debug import debug_print
from keymappings.key import Key
from keymappings.chord import Chord
from keymappings.sequence import Sequence

def is_key_or_combination(value):
    # Make regex to check if it's a key instead of checking fields?
    return not (value == 'action' or value == 'description')


@dataclass
class KeymappingsLoop:
    initial_parsed_keymappings: dict

    children_keymappings: dict = field(default_factory=dict)
    pressed: Set[Key] = field(default_factory=set)

    def __post_init__(self):
        self.children_keymappings = self.initial_parsed_keymappings

    def _keys_are_held(self):
        return len(self.pressed) > 1

    def _match_keymappings(self, keymappings: dict) -> dict:
        """

        :param key: 
        :param keymappings: 
        :return: matched_keymappings - A subset of keymappings
        """
        print(keymappings)
        matched_keymappings = {}

        for current, children in keymappings.items():
            # sequence = k.parse_hotkey('ctrl+w,a')
            if not is_key_or_combination(current):
                continue

            current_chord = Chord.from_keyboard_chord(current)
            if current_chord == Chord(self.pressed):
                matched_keymappings[current] = children
                # print('^This chord was matched!')

            # chord_keys = (Key('', possible_scan_codes) for possible_scan_codes in chord)
            # pressed_keys = (Key('', (scan_code,)) for scan_code in pressed)
            # print(list(pressed_keys), list(chord_keys))

        return matched_keymappings

    def _have_subkeymappings(self, matched_keymappings):
        # No keymappings found.
        if not matched_keymappings:
            #   Some key is held, wait until it's released. Maybe next key will
            # complete the chord.
            if self._keys_are_held():
                return False

            # No keys are held, we are no longer expecting chord parts.
            self.children_keymappings = self.initial_parsed_keymappings
            return False

        matched = filter(is_key_or_combination, matched_keymappings.keys())

        self.children_keymappings: dict = reduce(
                lambda accumulator, match: accumulator | self.children_keymappings[match],
                matched,
                {}
            ) or self.initial_parsed_keymappings

        return True

    current_sequence: Sequence = field(default_factory=Sequence)

    def on_press_hook(self, event: k.KeyboardEvent):
        debug_print('--------------------------------------')
        debug_print('pressed key:', event.name)
        key = Key.from_keyboard_event(event)
        self.pressed.add(key)

        debug_print('pressed', self.pressed)

        self.current_sequence.put(key)

        debug_print('current_sequence:', self.current_sequence)

        matched_keymappings = self._match_keymappings(self.children_keymappings)

        #   No children combinations found, no keys are held, we are no longer
        # expecting chord parts.
        if not matched_keymappings:
            self.current_sequence.send_all_elements()

            # if sequence_is_degenerate and self._keys_are_held():
            if self.children_keymappings != self.initial_parsed_keymappings:
                self.children_keymappings = self.initial_parsed_keymappings

                #   Maybe user started typing new sequence. Try again but on root level
                # if we are not already on root level.
                matched_keymappings = self._match_keymappings(self.children_keymappings)
        
        # No next keymappings found.
        if not self._have_subkeymappings(matched_keymappings):
            self.current_sequence.send_element()
        else:
            actionless = True
            for keymapping in matched_keymappings.values():
                print('keymapping', keymapping)
                action = keymapping.get('action')

                if not action:
                    debug_print('No action found!')
                    continue

                actionless = False
                action.exec()

            if not actionless:
                while not self.current_sequence.empty():
                    self.current_sequence.get()


    def on_release_hook(self, event: k.KeyboardEvent):
        key = Key.from_keyboard_event(event)

        if key in self.pressed:
            self.pressed.remove(key)

        key.release()

    def on_event(self, event: k.KeyboardEvent):
        if event.event_type == 'down':
            self.on_press_hook(event)
        else:
            self.on_release_hook(event)

