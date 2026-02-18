import asyncio
import os
import logging
import sys
import threading
from dotenv import load_dotenv
from src.config import AppConfig
from src.gui.context import AppContext
from src.midi.ports import PortManager
from src.midi.processor import MidiProcessor
from src.midi.engine import MidiEngine
from src.midi.event_log import EventLog
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


def run_engine(engine, inputs, output, event_loop):
    """Function to run the MIDI engine in a separate thread."""
    try:
        event_loop.run_until_complete(engine.run(inputs, output))
    except Exception as e:
        logger.error(f"Engine thread error: {e}")
    finally:
        event_loop.close()


async def main():
    # Load configuration from environment
    config = AppConfig.from_env()

    port_manager = PortManager()

    if config.list_ports:
        print("\n--- Available MIDI Inputs ---")
        for p in port_manager.get_input_names():
            print(f"  {p}")
        print("\n--- Available MIDI Outputs ---")
        for p in port_manager.get_output_names():
            print(f"  {p}")
        return

    if not config.output:
        logger.error("OUTPUT environment variable not set.")
        print("Please set OUTPUT in your .env file or environment.")
        return

    output_name = port_manager.find_output_port(config.output)

    if not output_name:
        logger.error(f"Could not find output port matching: {config.output}")
        return

    input_names = port_manager.get_input_names()
    filtered_inputs = port_manager.filter_inputs(
        input_names, output_to_exclude=output_name
    )

    if not filtered_inputs:
        logger.error("No valid input ports found.")
        return

    # Create event log for monitoring
    event_log = EventLog(max_events=50)

    processor = MidiProcessor(
        verbose=config.verbose, config=config, event_log=event_log
    )
    engine = MidiEngine(processor, event_log=event_log)

    # Create event loop for MIDI engine
    event_loop = asyncio.new_event_loop()

    # Create application context
    context = AppContext(
        gui=None,  # Will be set after GUI is created
        engine=engine,
        processor=processor,
        event_loop=event_loop,
        event_log=event_log,
    )

    # Create ArpEngine and attach to context (engine runs in event_loop)
    try:
        from src.midi.arp.engine_refactored import ArpEngine

        arp_engine = ArpEngine(processor.arp_state, engine, event_loop)
        context.arp_engine = arp_engine
    except Exception:
        arp_engine = None

    # Create HarmonyEngine
    try:
        from src.midi.harmony.engine import HarmonyEngine
        from src.midi.arp.dispatcher import MidiDispatcher

        dispatcher = MidiDispatcher(engine)
        harmony_engine = HarmonyEngine(dispatcher)
        context.harmony_engine = harmony_engine
        processor.harmony_engine = harmony_engine
    except Exception:
        harmony_engine = None

    # Start MIDI engine in a background thread
    engine_thread = threading.Thread(
        target=run_engine,
        args=(engine, filtered_inputs, output_name, event_loop),
        daemon=True,
    )
    engine_thread.start()

    # Wait for engine queue to be initialized
    while engine.queue is None:
        await asyncio.sleep(0.1)

    # Start the GUI in the main thread
    logger.info("Starting GUI...")
    app = MidiGui(context, config)

    try:
        app.mainloop()
    finally:
        logger.info("GUI closed, stopping engine...")
        # Stop ArpEngine if present
        try:
            if getattr(context, "arp_engine", None):
                event_loop.call_soon_threadsafe(context.arp_engine.stop)
        except Exception:
            pass

        # Stop the engine
        event_loop.call_soon_threadsafe(engine._stop_event.set)
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.exception(e)
