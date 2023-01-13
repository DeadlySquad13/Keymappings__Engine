import keyboard as k
from keymappings.keymapping import Keymapping

from keymappings.keymappings_loop import KeymappingsLoop

def main():
    loop = KeymappingsLoop(initial_parsed_keymappings=Keymapping.KEYMAPPINGS_TREE)
    k.hook(loop.on_event, suppress=True)


    k.wait()


if __name__ == '__main__':
    main()
