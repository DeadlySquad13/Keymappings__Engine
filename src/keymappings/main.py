import keyboard as k

from keymappings.keymappings_loop import KeymappingsLoop

from keymappings.config import km

def main():
    loop = KeymappingsLoop(initial_parsed_keymappings=km.KEYMAPPINGS)
    k.hook(loop.on_event, suppress=True)

    # Setting terminate key doesn't work unfortunately.
    k.wait()


if __name__ == '__main__':
    main()
