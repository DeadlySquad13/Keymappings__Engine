from dataclasses import dataclass, field
from functools import reduce
from typing import List, Set
import keyboard as k
import copy

from keymappings.debug import debug_print
from keymappings.key import Key
from keymappings.chord import Chord

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


    def _on_match_keymappings(self, matched_keymappings):
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
        # print('matched', list(matched))
        # debug_print('children', self.children_keymappings)

        # debug_print('children', self.children_keymappings)

        self.children_keymappings: dict = reduce(
                lambda accumulator, match: accumulator | self.children_keymappings[match],
                matched,
                {}
            ) or self.initial_parsed_keymappings

        return True

    current_sequence_index = 0
    current_sequence: List[Chord] = field(default_factory=list)

    def send_current_sequence(self):
        print('sequence:', self.current_sequence)
        # Send all accumulated chords.
        for i, chord in enumerate(self.current_sequence):
            is_last = i == len(self.current_sequence) - 1

            for key in chord:
                # Hack for not registered windows key
                #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
                if key.scan_codes == (91,):
                    k.press('left windows')
                    continue

                k.press(key.scan_codes[0])

            if not is_last:
                for key in chord:
                    # Hack for not registered windows key
                    #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
                    if key.scan_codes == (91,):
                        k.release('left windows')
                        continue

                    k.release(key.scan_codes[0])


    def on_press_hook(self, event: k.KeyboardEvent):
        debug_print('--------------------------------------')
        debug_print('pressed key:', event.name)
        key = Key.from_keyboard_event(event)
        self.pressed.add(key)

        debug_print('pressed', self.pressed)

        debug_print('index:', self.current_sequence_index)
        if self.current_sequence_index > len(self.current_sequence) - 1:
            self.current_sequence.append(copy.deepcopy(self.pressed))

        debug_print('current_sequence:', self.current_sequence)

        matched_keymappings = self._match_keymappings(self.children_keymappings)

        #   No children combinations found, no keys are held, we are no longer
        # expecting chord parts.
        #   Maybe user started typing new sequence. Try again but on root level
        # if we are not already on root level.
        if not matched_keymappings:
            if not self._keys_are_held() and len(self.current_sequence) > 1:
                self.children_keymappings = self.initial_parsed_keymappings
            
                self.send_current_sequence()
                self.current_sequence_index = 0
                self.current_sequence = []

            matched_keymappings = self._match_keymappings(self.children_keymappings)

        # No next keymappings found.
        if not self._on_match_keymappings(matched_keymappings):
            self.send_current_sequence()

            self.current_sequence_index = 0
            self.current_sequence = []
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
                self.current_sequence_index = 0
                self.current_sequence = []



    def on_release_hook(self, event: k.KeyboardEvent):
        key = Key.from_keyboard_event(event)

        if key in self.pressed:
            self.pressed.remove(key)

        if len(self.pressed) == 0:
            self.current_sequence_index += 1

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

