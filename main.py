import time
from src.midi import MidiHandler


def main():
    handler = MidiHandler()
    handler.list()
    while True:
        try:
            handler.echo()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Error, reinitializing...")


if __name__ == "__main__":
    main()
