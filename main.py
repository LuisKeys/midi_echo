import asyncio
import os
import logging
import sys
import threading
from dotenv import load_dotenv
from src.midi.ports import PortManager
from src.midi.processor import MidiProcessor
from src.midi.engine import MidiEngine
from src.gui.app import MidiGui

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_engine(engine, inputs, output):
    """Function to run the MIDI engine in a separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Store the loop in the engine so it can be accessed
    engine._loop = loop

    try:
        loop.run_until_complete(engine.run(inputs, output))
    except Exception as e:
        logger.error(f"Engine thread error: {e}")
    finally:
        loop.close()


async def main():
    port_manager = PortManager()

    # Get configuration from environment
    output_hint = os.getenv("OUTPUT")
    verbose = os.getenv("VERBOSE", "false").lower() == "true"
    list_ports = os.getenv("LIST_PORTS", "false").lower() == "true"

    if list_ports:
        print("\n--- Available MIDI Inputs ---")
        for p in port_manager.get_input_names():
            print(f"  {p}")
        print("\n--- Available MIDI Outputs ---")
        for p in port_manager.get_output_names():
            print(f"  {p}")
        return

    if not output_hint:
        logger.error("OUTPUT environment variable not set.")
        print("Please set OUTPUT in your .env file or environment.")
        return

    output_name = port_manager.find_output_port(output_hint)

    if not output_name:
        logger.error(f"Could not find output port matching: {output_hint}")
        return

    input_names = port_manager.get_input_names()
    filtered_inputs = port_manager.filter_inputs(
        input_names, output_to_exclude=output_name
    )

    if not filtered_inputs:
        logger.error("No valid input ports found.")
        return

    processor = MidiProcessor(verbose=verbose)
    engine = MidiEngine(processor)

    # Start MIDI engine in a background thread
    engine_thread = threading.Thread(
        target=run_engine, args=(engine, filtered_inputs, output_name), daemon=True
    )
    engine_thread.start()

    # Wait a bit for the loop and queue to be initialized in the thread
    while engine._loop is None or engine.queue is None:
        await asyncio.sleep(0.1)

    # Start the GUI in the main thread
    logger.info("Starting GUI...")
    app = MidiGui(engine, processor, engine._loop)

    try:
        app.mainloop()
    finally:
        logger.info("GUI closed, stopping engine...")
        # Use a thread-safe way to stop the engine
        engine._loop.call_soon_threadsafe(engine._stop_event.set)
        # Give it a moment to clean up
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        # We need a small async wrapper to start the main logic
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.exception(e)
