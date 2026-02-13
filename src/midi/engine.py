import asyncio
import mido
import logging
from .processor import MidiProcessor
from .message_wrapper import MidiMessageWrapper

logger = logging.getLogger(__name__)


class MidiEngine:
    """Core engine to handle async MIDI message routing."""

    def __init__(self, processor: MidiProcessor):
        self.processor = processor
        self.queue = None
        self.inputs = []
        self.output = None
        self._running = False
        self._loop = None
        self._stop_event = None

    def _callback(self, msg):
        """Thread-safe callback to push messages into the async queue."""
        if self._loop and self._loop.is_running() and self.queue:
            wrapped_msg = MidiMessageWrapper(msg, is_arp=False)
            self._loop.call_soon_threadsafe(self.queue.put_nowait, wrapped_msg)

    async def run(self, input_names: list[str], output_name: str):
        self._loop = asyncio.get_running_loop()
        self.queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self._running = True
        self._stop_event.clear()

        try:
            self.output = mido.open_output(output_name)
            logger.info(f"Opened output: {output_name}")

            for name in input_names:
                try:
                    # mido.open_input with a callback creates a background thread.
                    # This thread will call self._callback(msg) for every incoming message.
                    inp = mido.open_input(name, callback=self._callback)
                    self.inputs.append(inp)
                    logger.info(f"Listening on input: {name}")
                except Exception as e:
                    print(f"Error opening MIDI input {name}: {e}")
                    logger.error(f"Failed to open input {name}: {e}")

            if not self.inputs:
                logger.error("No valid inputs could be opened. Exiting engine.")
                return

            print(f"MIDI Engine active. Routing messages to {output_name}...")
            print("Press Ctrl+C to stop.")

            # Start the consumer task that processes the queue
            consumer_task = asyncio.create_task(self._consume_queue())

            # Wait for the stop event (this blocks until stop() is called)
            await self._stop_event.wait()

            # Cleanup consumer
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            print(f"MIDI Engine encountered an error: {e}")
            logger.error(f"Engine error: {e}")
        finally:
            await self.stop()

    async def _consume_queue(self):
        """Worker task that pulls messages from the queue and sends them to output."""
        while self._running:
            try:
                msg = await self.queue.get()
                processed_msg = self.processor.process(msg)

                if processed_msg and self.output:
                    self.output.send(processed_msg)

                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def stop(self):
        self._running = False
        self._stop_event.set()
        logger.info("Stopping MIDI engine...")
        for inp in self.inputs:
            inp.close()
        if self.output:
            self.output.close()
        self.inputs = []
        self.output = None
        logger.info("MIDI engine stopped.")
