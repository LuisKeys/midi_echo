# MIDI Echo Architecture

## Overall Layers

- **Entry Point**: `main.py` boots the app by loading `AppConfig.from_env()`, wiring up `AppContext`, creating `MidiGui`, `MidiEngine`, `MidiProcessor`, the arpeggiator/harmony engines, and then launching the GUI and async MIDI loop.
- **Configuration & Context**: Environment-derived settings live in `src/config/config.py`. `AppContext` centralizes references (`gui`, `engine`, `processor`, `event_loop`, `arp_engine`, `harmony_engine`, `event_log`, `app_config`) so handlers and processors can stay decoupled and testable.

## GUI Layer (`src/gui`)

- **`MidiGui` (`src/gui/app.py`)**: The CustomTkinter window that sets the theme, creates the `ButtonPanel`, `PopupManager`, and `PressDetector`, and registers handler callbacks for each control button (Harmony, Arpeggiator, Scale, Transpose, Octave, Channel, Preset, Panic). It also handles debounced resizing and keeps handler UI state in sync after initialization.
- **Component Suite (`src/gui/components`)**: Modular widgets (button panel, theme manager, popups, layout helpers) encapsulate presentation logic so `MidiGui` stays focused on wiring handlers to buttons.
- **Handlers (`src/gui/handlers`)**: Each button has a handler class that knows how to mutate `AppContext` and send commands to the MIDI layer. Handlers expose short-press/long-press methods used by the `PressDetector` to distinguish actions.
- **Input Utilities (`src/gui/input/press_detector.py`)**: Detects short vs. long presses and feeds the right handler method to the GUI.

## MIDI Layer (`src/midi`)

- **Engine (`src/midi/engine.py`)**: `MidiEngine` runs on an asyncio event loop. It opens MIDI input ports with callback threads that enqueue wrapped messages (`MidiMessageWrapper`) into an `asyncio.Queue`. A consumer task dequeues messages, calls `MidiProcessor.process()`, and forwards resulting messages to the selected MIDI output.
- **Processor (`src/midi/processor.py`)**: Applies runtime transformations—scale snapping, harmonizer delegation, arpeggiator state updates, transpose/octave shifts, channel remapping, and logging. It holds `ArpState` and `HarmonyState`, toggles features (scale, harmonizer, arpeggiator), and can reject notes that fall outside MIDI range or when arpeggiator short-circuits inputs.
- **Arpeggiator Subsystem (`src/midi/arp`)**: Houses the logic that builds rhythmic patterns from held notes, enforces timing, and produces output notes. Modules include the refactored engine, state validator, dispatcher, timing calculations, mode definitions, and note producers.
- **Harmony Subsystem (`src/midi/harmony`)**: Generates harmonic accompaniment by snapping generated intervals to the active scale. `HarmonyEngine` works with `HarmonyState`, `HarmonyGenerator`, and `VoiceManager` to track held voices and emit harmony notes via `MidiProcessor`.
- **Ports & Message Utilities**: `ports.py` manages discovery/selection of virtual and hardware MIDI endpoints; `message_wrapper.py` tags messages so the processor can differentiate between player input and generated notes.

## Supporting Infrastructure

- **Event Logging (`src/midi/event_log.py`)**: Optional logging hook that records inbound/outbound messages for debugging/performance metrics.
- **Scales (`src/midi/scales.py`)**: Defines `ScaleType`, interval tables, and helper functions such as `snap_note_to_scale()` used by both the processor and harmonizer.
- **Contextual Dependency Injection**: `AppContext` is passed around so handlers, GUI, and MIDI components share a single source of truth for configuration, engines, and per-session runtime state.

## Event Flow

1. `MidiEngine` receives raw MIDI input via `mido` callbacks, wraps it with metadata, and queues it on the asyncio loop.
2. `MidiProcessor` dequeues messages. If scale snapping or harmony is enabled, it updates notes before handing off to subsystems. Arpeggiator state is refreshed for player-held notes, and generated notes bypass the held-note dropping logic.
3. After processing (transpose, octave, channel remap), the processor sends the resulting `mido.Message` to the selected output port and optionally logs the event.
4. GUI handlers toggle features in the processor and audio engines, passing state through `AppContext` so the MIDI layer reacts immediately to button presses.

## Testing & Quality

- **Unit Tests (`tests/`)**: Structured mirrors of the `src/` packages. MIDI generators, GUI handlers, and harmony/arp subsystems each have dedicated tests, ensuring handlers behave under both short-press and long-press scenarios.
- **Integration Hooks**: The GUI/engine split allows tests to instantiate `AppContext` with fake engines and processors so logic paths can be validated without launching the full application.

## Runtime Notes

- Async GUI/MIDI split keeps the interface responsive: GUI runs in the main thread via CustomTkinter while `MidiEngine` runs async tasks for message consumption.
- Environment-driven `AppConfig` makes it easy to tweak MIDI ports, thresholds, window size, and theme without code changes.
- Feature toggles (scale, harmonizer, arpeggiator) operate as binary flags inside `MidiProcessor`, which keep the audio pipeline lean when not needed.
