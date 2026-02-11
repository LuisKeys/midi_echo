import time
from dotenv import load_dotenv
from src.midi import MidiHandler

load_dotenv()


def main():
    handler = MidiHandler()
    handler.list()
    try:
        while True:
            handler.echo()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
