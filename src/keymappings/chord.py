from dataclasses import dataclass
from typing import Self, Set
import keyboard as k

from keymappings.key import Key

@dataclass()
class Chord:
    keys: Set[Key]

    def __iter__(self):
        return self.keys.__iter__()

    def __next__(self):
        return self.keys.__next__()

    def send(self, press=True, release=True):
        if press:
            for key in self:
                key.press()

        if release:
            for key in self:
                key.release()

    def __eq__(self, other: Self):
        return all( # All keys in chords should match.
                   any(key == left_key for key in other.keys)
                       for left_key in self.keys
                  )

    @classmethod
    def from_keyboard_chord(self, chord: str):
        keys = k.parse_hotkey(chord)[0] # It parses it as combination so we take first element as we always give it a chord.
        keys_translated = set(map(lambda scan_codes: Key('', scan_codes=scan_codes), keys))

        return self(keys=keys_translated)
