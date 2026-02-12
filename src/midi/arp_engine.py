"""Simple arpeggiator engine for generating MIDI note events.

This implementation is intentionally lightweight: it provides a runnable
and syntactically-correct `ArpEngine` that schedules note_on/note_off
messages into a provided `midi_engine.queue`. It is sufficient for tests
and for the GUI code that starts/stops the engine.
"""

import asyncio
import logging
import random
from typing import Optional

import mido

from src.midi.arp_state import ArpState

logger = logging.getLogger(__name__)


class ArpEngine:
    def __init__(
        self,
        arp_state: ArpState,
        midi_engine,
        event_loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.state = arp_state
        self.midi_engine = midi_engine
        self._loop = event_loop or asyncio.get_event_loop()

        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._step = 0
        self._position = 0
        self._direction = 1
        self._active_order: list[int] = []

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = self._loop.create_task(self._run())

    def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    async def _run(self) -> None:
        try:
            while self._running and self.state and self.state.enabled:
                # Basic timing calculation
                bpm = max(20, int(self.state.bpm or 120))
                beat_seconds = 60.0 / bpm

                division_map = {
                    "1/4": 1.0,
                    "1/8": 0.5,
                    "1/16": 0.25,
                    "1/32": 0.125,
                    "TRIPLET": 1.0 / 3.0,
                    "DOTTED": 1.5,
                }
                div = (self.state.division or "1/8").upper()
                factor = division_map.get(div, 0.5)

                interval = (
                    beat_seconds
                    * factor
                    * (1.0 / max(0.0001, float(self.state.shift_tempo_mul or 1.0)))
                )

                self._build_active_order()

                # Apply simple swing: delay every other step by a percentage
                is_odd = (self._step % 2) == 1
                swing_delay = 0.0
                if getattr(self.state, "swing", 0) and factor > 0:
                    swing_pct = max(0, min(75, int(self.state.swing or 0)))
                    swing_delay = (
                        (swing_pct / 100.0) * (interval / 2.0)
                        if is_odd
                        else -(swing_pct / 100.0) * (interval / 2.0)
                    )

                await self._tick()

                sleep_for = max(0.001, interval + swing_delay)
                await asyncio.sleep(sleep_for)
        except asyncio.CancelledError:
            return
        except Exception:
            logger.exception("ArpEngine run loop error")

    async def _tick(self) -> None:
        if not self._active_order:
            self._step += 1
            return

        idx = self._choose_index()
        step_idx = self._active_order[idx]
        play = (
            self.state.pattern_mask[step_idx]
            if step_idx < len(self.state.pattern_mask)
            else False
        )

        if not play:
            self._step += 1
            return

        base_note = 60 + (step_idx % 12)
        octave_offset = (self.state.octave - 1) * 12
        note = base_note + octave_offset

        if (self.state.velocity_mode or "").upper() == "FIXED":
            vel = int(max(1, min(127, getattr(self.state, "fixed_velocity", 100))))
        elif (self.state.velocity_mode or "").upper() == "RANDOM":
            vel = random.randint(40, 127)
        else:
            vel = int(max(1, min(127, getattr(self.state, "fixed_velocity", 100))))

        if (
            getattr(self.state, "accents", None)
            and step_idx < len(self.state.accents)
            and self.state.accents[step_idx]
        ):
            vel = min(127, int(vel * 1.25))

        note_on = mido.Message("note_on", note=note, velocity=vel)

        # Enqueue note_on in a thread-safe manner
        try:
            if getattr(self.midi_engine, "_loop", None):
                self.midi_engine._loop.call_soon_threadsafe(
                    self.midi_engine.queue.put_nowait, note_on
                )
            else:
                self.midi_engine.queue.put_nowait(note_on)
        except Exception:
            logger.exception("Failed to enqueue note_on")

        gate_seconds = max(
            0.01,
            (self.state.gate_pct / 100.0)
            * (60.0 / max(20, int(self.state.bpm or 120))),
        )
        asyncio.create_task(self._schedule_note_off(note, gate_seconds))

        self._step += 1

    def preview(self, steps: int = 8) -> None:
        async def _preview():
            for i in range(steps):
                if not getattr(self.midi_engine, "queue", None):
                    break
                idx = (self._step + i) % len(self.state.pattern_mask)
                if self.state.pattern_mask[idx]:
                    base_note = 60 + idx % 12
                    octave_offset = (self.state.octave - 1) * 12
                    note = base_note + octave_offset
                    vel = int(
                        max(1, min(127, getattr(self.state, "fixed_velocity", 100)))
                    )
                    note_on = mido.Message("note_on", note=note, velocity=vel)
                    note_off = mido.Message("note_off", note=note, velocity=0)
                    try:
                        if getattr(self.midi_engine, "_loop", None):
                            self.midi_engine._loop.call_soon_threadsafe(
                                self.midi_engine.queue.put_nowait, note_on
                            )
                        else:
                            self.midi_engine.queue.put_nowait(note_on)
                        await asyncio.sleep(0.08)
                        if getattr(self.midi_engine, "_loop", None):
                            self.midi_engine._loop.call_soon_threadsafe(
                                self.midi_engine.queue.put_nowait, note_off
                            )
                        else:
                            self.midi_engine.queue.put_nowait(note_off)
                    except Exception:
                        pass

        asyncio.run_coroutine_threadsafe(_preview(), self._loop)

    async def _schedule_note_off(self, note: int, delay: float) -> None:
        await asyncio.sleep(delay)
        note_off = mido.Message("note_off", note=note, velocity=0)
        try:
            if getattr(self.midi_engine, "_loop", None):
                self.midi_engine._loop.call_soon_threadsafe(
                    self.midi_engine.queue.put_nowait, note_off
                )
            else:
                self.midi_engine.queue.put_nowait(note_off)
        except Exception:
            logger.exception("Failed to enqueue note_off")

    def _build_active_order(self) -> None:
        mask = self.state.pattern_mask
        active = [i for i, v in enumerate(mask) if v]
        if not active:
            self._active_order = []
            return

        mode = (self.state.mode or "UP").upper()
        if mode == "RANDOM":
            self._active_order = active
        elif mode == "DOWN":
            self._active_order = list(reversed(active))
        elif mode == "UPDOWN":
            up = active
            down = list(reversed(active))[1:-1] if len(active) > 2 else []
            self._active_order = up + down
        else:
            self._active_order = active

    def _choose_index(self) -> int:
        if not self._active_order:
            return 0
        mode = (self.state.mode or "UP").upper()
        if mode == "RANDOM":
            return random.randrange(len(self._active_order))

        pos = self._position % len(self._active_order)
        # advance position
        self._position = (self._position + 1) % len(self._active_order)
        return pos
