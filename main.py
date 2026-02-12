import asyncio
import os
import logging
import sys
from dotenv import load_dotenv
from src.midi.ports import PortManager
from src.midi.processor import MidiProcessor
from src.midi.engine import MidiEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


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

    try:
        await engine.run(filtered_inputs, output_name)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error during execution: {e}")
        logger.error(f"Execution error: {e}")
    finally:
        await engine.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.exception(e)
