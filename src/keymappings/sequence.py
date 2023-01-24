from dataclasses import dataclass, field
from queue import SimpleQueue
from keymappings.chord import Chord

@dataclass
class Sequence:
    chords: SimpleQueue[Chord] = field(default_factory=SimpleQueue)

    def __iter__(self):
        return self.chords.__iter__()

    def __next__(self):
        return self.chords.__next__()

    def size(self) -> int:
        return self.chords.qsize()

    def empty(self) -> bool:
        return self.chords.empty()

    def put(self, chord: Chord):
        return self.chords.put(chord)

    def get(self) -> Chord:
        return self.chords.get()

    def send_element(self) -> None:
        is_last = self.size() == 1
        chord = self.chords.get()
        print('sequence element', chord)
        chord.send(press=True, release=not is_last)

    def send_all_elements(self) -> None:
        while self.chords.qsize() > 1:
            self.send_element()
