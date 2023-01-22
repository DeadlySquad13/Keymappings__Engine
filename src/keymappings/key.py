from typing import Self, Tuple
import keyboard as k

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

    def press(self):
        # Hack for not registered windows key
        #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
        if self.scan_codes == (91,):
            return k.press('left windows')

        k.press(self.scan_codes[0])

    def release(self):
        # Hack for not registered windows key
        #   [mr](https://github.com/boppreh/keyboard/pull/463/files).
        if self.scan_codes == (91,):
            return k.release('left windows')

        k.release(self.scan_codes[0])

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

    # For storing in set.
    def __hash__(self):
        return hash(self.__key__())

    @classmethod
    def from_keyboard_event(self, event: k.KeyboardEvent):
        return self(event.name, (event.scan_code,))
