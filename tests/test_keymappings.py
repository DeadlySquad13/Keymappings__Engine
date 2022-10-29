from typing import Set
from pynput import keyboard
import pytest

from keymappings.main import Keymapping, match_keymappings

def test_answer():
    km = Keymapping()
    keymapping = {
            "key_sequences": [
            [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="w")}],
            [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="W")}],
        ],
        "command": "TEST",
    }
    km.add_keymappings(keymapping)

    matched_sequences = [0 for _ in km.KEYMAPPINGS]

    print(km.KEYMAPPINGS)
    assert match_keymappings(keyboard.Key.ctrl_l,
                             km.KEYMAPPINGS, matched_sequences) == []

    assert match_keymappings(keyboard.KeyCode.from_vk(87), # Added 'w'.
                             km.KEYMAPPINGS, matched_sequences) == [keymapping]

def test_parse_keymapping_str_notation():
    km = Keymapping()

    assert km.parse_keymapping_str_notation('ctrl_l + w') == { 'ctrl_l', 'w' }

@pytest.mark.parametrize('keymapping,decoded_keymapping', [
    ('ctrl_l', { keyboard.Key.ctrl_l }),
    ('w', { keyboard.KeyCode(char='w') }),

    ('ctrl_l+w', { keyboard.Key.ctrl_l, keyboard.KeyCode(char='w') }),
    ('ctrl_l +w', { keyboard.Key.ctrl_l, keyboard.KeyCode(char='w') }),
    ('ctrl_l+ w', { keyboard.Key.ctrl_l, keyboard.KeyCode(char='w') }),
    ('ctrl_l + w', { keyboard.Key.ctrl_l, keyboard.KeyCode(char='w') }),
])
def test_decode_keymapping_str_notation(keymapping: str, decoded_keymapping: Set[keyboard.Key | keyboard.KeyCode]):
    km = Keymapping()
    assert km.decode_keymapping_str_notation(keymapping) == decoded_keymapping
