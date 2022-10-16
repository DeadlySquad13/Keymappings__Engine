from pynput import keyboard

from keymappings.main import Keymapping, match_keymappings

def test_answer():
    km = Keymapping()

    km.add_keymappings({
        "key_sequences": [
            [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="w")}],
            [{keyboard.Key.ctrl_l, keyboard.KeyCode(char="W")}],
        ],
        "command": "TEST",
    })

    matched_sequences = [0 for _ in km.KEYMAPPINGS]

    print(km.KEYMAPPINGS)
    assert match_keymappings(keyboard.Key.ctrl_l,
                             km.KEYMAPPINGS, matched_sequences) == []

    assert match_keymappings(keyboard.KeyCode.from_vk(87), # 'w'
                             km.KEYMAPPINGS, matched_sequences) == km.KEYMAPPINGS
