# Metronome Audio Implementation

## Overview

The metronome has been refactored to use internally generated digital audio synthesis instead of MIDI messages.

## Changes Made

### 1. New Audio Module (`src/audio/`)

A new `src/audio/` package has been created with the following components:

- **`synthesizer.py`**: Contains `MetronomeClicker` class
  - Synthesizes high-quality metronome clicks using sine wave synthesis
  - Supports two click types: downbeat (1000 Hz, louder) and beat (800 Hz, softer)
  - Applies realistic amplitude envelope (attack + exponential decay)
  - Compatible with both `sounddevice` and `simpleaudio` audio libraries

### 2. Updated Sequencer

**File**: `src/midi/sequencer/sequencer.py`

Changes:
- Imports `MetronomeClicker` from the new audio module
- Creates an instance (`self.clicker`) in `__init__`
- **Removed**: MIDI note_on/note_off messages in `_on_bar_start()` and `_on_beat()`
- **Added**: Async audio playback via `asyncio.create_task(self.clicker.play_downbeat/play_beat())`

### 3. Dependencies

Added to `requirements.txt`:
- `sounddevice` - Cross-platform audio output library (primary)
- `numpy` - Required for audio synthesis

Fallback support for `simpleaudio` if `sounddevice` is not available.

## How It Works

### Click Synthesis

Each metronome click is synthesized on-demand:

1. **Sine wave generation**: Pure sine wave at the configured frequency
2. **Envelope shaping**: Attack (5ms) + decay for natural click sound
3. **Velocity control**: Volume normalized from MIDI velocity (0-127)
4. **Playback**: Sent to default audio output device

### Timing Integration

- Metronome clicks are triggered by the same high-resolution PPQN=960 clock as before
- `_on_bar_start()` plays a downbeat click (louder, lower frequency)
- `_on_beat()` plays a regular beat click (softer, higher frequency)
- Audio playback is scheduled asynchronously to avoid blocking the clock

## Customization

You can customize the metronome sound by modifying the `MetronomeClicker` properties:

```python
# In MidiSequencer.__init__() or elsewhere:
clicker = sequencer.clicker
clicker.downbeat_freq = 1200  # Hz
clicker.downbeat_velocity = 120  # 0-127
clicker.beat_freq = 900  # Hz
clicker.beat_velocity = 90  # 0-127
clicker.click_duration = 0.04  # seconds
clicker.attack_time = 0.003  # seconds
clicker.release_time = 0.03  # seconds
```

## Advantages

1. **No MIDI channel consumption**: Metronome no longer uses MIDI channel 9/drums
2. **Better sound quality**: Natural sine wave synthesis vs MIDI percussion
3. **Zero latency**: Audio output is direct, no MIDI routing
4. **Cross-platform**: Works on macOS, Windows, Linux
5. **No external sample files**: Everything generated procedurally in real-time

## Troubleshooting

### Audio not working
- Ensure `sounddevice` is installed: `pip install sounddevice`
- Check system audio output is not muted
- Review logs for audio subsystem errors

### Clicks sound different than before
- Fine-tune the frequencies and envelopes in `MetronomeClicker`
- The old MIDI percussion samples had a different tonal quality

### Performance concerns
- Audio synthesis is lightweight (~5KB per click)
- Async scheduling prevents blocking the clock
- CPU impact negligible compared to MIDI processing
