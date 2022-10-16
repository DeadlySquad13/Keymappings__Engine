from pynput import keyboard

# class MyKeyCode(keyboard.KeyCode):
#     def __init__(self, KeyCode):
#         self.value = 

# Covert value in the Unicode table to the key you pressed on the keyboard.
#   Used vk - virtual key - place of the key on the keyboard or better 'code'
#   which is sent by driver. Of course it exists only on keys that were
#   pressed.
def convert_to_raw_character(key: keyboard.KeyCode):
    return chr(key.vk).lower()

# When you press ctrl+alphanumeric_char, alphanumeric_char gets another code.
#   This function removes it.
def convert_to_readable_key(key):
    if isinstance(key, keyboard.KeyCode):
        return keyboard.KeyCode(char=convert_to_raw_character(key))

    return key


