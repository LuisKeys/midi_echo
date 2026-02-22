# MIDI Echo Feature Catalog

## Real-time MIDI Processing
- Multithreaded MIDI I/O via `mido` callbacks feeding an `asyncio.Queue`, ensuring the GUI remains responsive while messages flow through the processor/engine.
- Live transformations include scale snapping, channel remapping, transpose, octave shifts, and arpeggiator/harmony overrides before messages hit the output port.
- Optional event logging captures inbound/outbound messages for debugging and performance metrics.

## Arpeggiator Features
- Multiple arpeggiator modes (up, down, up-down, random, etc.) defined in `src/midi/arp/modes.py`.
- Timing controls for tempo, swing, and clock sync support (including MIDI clock handling when external sync is enabled).
- Held-note tracking, latch modes, and pattern dispatching that feed the `ArpState`/`ArpEngine` combo.
- Velocity, accent, and pattern editing exposed through the GUI tabs and event handlers.

## Harmony Features
- Scale-aware harmony generation that snaps intervals to the currently selected key/scale.
- Voice management tracks polyphonic notes so added harmonies stay musically aligned with the player input.
- Harmonizer engine integrates with the `MidiProcessor` so only melody presses go through harmonizer logic while generated harmony notes bypass input filters.

## GUI & Interaction
- Eight-button control panel (Scale, Arpeggiator, Harmony, Transpose, Octave, Channel, Preset, Panic) with short-press and long-press actions.
- Tabbed configuration area (Pattern, Modes, Timing, Velocity, Advanced) for fine-grained parameter tuning.
- Preset system for saving/loading entire setups, along with theme support for light/dark modes.
- Press detection that distinguishes between taps and holds to issue incremental changes or alternate commands.

## Preset Management
- The `PresetHandler` opens a modal built by `build_preset_selector()` when the PS button is pressed, keeping MIDI logic separate from the UI glue.
- The selector renders 0-127 program slots in a scrollable grid, automatically highlights the current selection, and re-syncs the button colors after each pick.
- Clicking a program sends a MIDI `program_change` message on the active output channel (defaulting to channel 0) through `AppContext` so the processor/engine handles delivery.
- Handler state tracks the chosen program so the next popup launch shows the prior selection and the PS button stays cyan to reflect its active state.

## MIDI Utilities
- Port management automatically discovers available MIDI devices; configuration is driven by `AppConfig` loaded from environment variables or `.env` values.
- Support for multiple output channels and transposition ranges (-12 to +12 semitones plus octave adjustments).
- Panic handler sends “All Notes Off” to clear stuck voices.

## Performance & Reliability
- Low-latency operation powered by asyncio consumers and proper queue draining/cancellation logic in `MidiEngine`.
- Configurable thresholds (short/long press, hold increment rate) tailor the experience to the performer’s style.
- Feature toggles (scale, harmonizer, arpeggiator) keep the processing pipeline lean when unused.
- Compatibility with macOS, Windows, and Linux (virtual MIDI ports such as IAC on macOS or JACK/ALSA on Linux).

## Development & Testing Support
- Conda-based workflow with `requirements.txt` listing `mido`, `python-rtmidi`, `numba`, `python-dotenv`, `customtkinter`, and test dependencies (`pytest`, `pytest-cov`, `pytest-asyncio`).
- Mirrors of production packages under `tests/` allow focused unit and integration coverage for GUI handlers, the harmonizer, and arpeggiator subsystems.
- README outlines installation, configuration, and troubleshooting steps so developers can reproduce the runtime environment quickly.
