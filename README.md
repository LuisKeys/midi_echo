# MIDI Echo

A comprehensive MIDI arpeggiator and harmony processor with a modern GUI, designed for live performance and music production. This application processes MIDI input in real-time, generating arpeggiated patterns, harmonic accompaniments, and various transformations.

## Features

### Core Functionality
- **Real-time MIDI Processing**: Processes MIDI messages from input devices and routes them to output devices with transformations
- **Arpeggiator Engine**: Generates rhythmic patterns from held notes with customizable timing, velocity, and modes
- **Harmony Engine**: Creates harmonic accompaniment by generating scale-snapped intervals from input melodies
- **Multi-channel Support**: Handles multiple MIDI channels for complex setups

### Main Menu Features
The main interface consists of 8 primary control buttons arranged in a 2x4 grid:

- **HZ (Harmony)**: Toggle harmony generation based on the current scale. Automatically enables the scale when activated and adds harmonic intervals to performed notes
- **TR (Transpose)**: Adjust pitch transposition in semitones (-12 to +12 range)
- **OC (Octave)**: Shift notes by octaves for different registers
- **SC (Scale)**: Select musical scale for note filtering and quantization
- **AR (Arpeggiator)**: Enable/disable the arpeggiator pattern generation
- **CH (Channel)**: Select MIDI output channel for routing messages
- **PS (Preset)**: Access preset management for saving/loading configurations
- **ST (Stop/Panic)**: Emergency stop - sends "All Notes Off" to clear stuck notes

Each button supports short press for primary actions and long press for secondary functions (like reset to default values).

### GUI Interface
- **Live Performance Controls**: Intuitive button-based interface for real-time adjustments
- **Tabbed Configuration**:
  - **Pattern Tab**: Edit arpeggiator patterns with step sequencing, accents, and held notes
  - **Modes Tab**: Select from various arpeggiator modes (up, down, up-down, random, etc.)
  - **Timing Tab**: Control tempo, swing, and rhythmic variations
  - **Velocity Tab**: Adjust note velocities and dynamics
  - **Advanced Tab**: Fine-tune parameters and advanced settings
- **Preset System**: Save and load configurations for different performances
- **Theme Support**: Light and dark modes for different environments

### MIDI Features
- **Port Management**: Automatic detection and selection of MIDI input/output ports
- **Transpose Handler**: Real-time pitch transposition
- **Octave Handler**: Octave shifting capabilities
- **Channel Handler**: MIDI channel routing and filtering
- **Scale Handler**: Scale-based note filtering and quantization
- **Panic Handler**: Emergency stop for stuck notes

### Performance Features
- **Low-latency Processing**: Optimized for real-time performance using asyncio and threading
- **Press Detection**: Short and long press handling for different actions
- **Hold Increment**: Continuous value changes when holding buttons

## Architecture

The application follows a modular architecture designed for maintainability and extensibility:

### Core Modules
- **`src/config/`**: Configuration management using environment variables and dataclasses
- **`src/gui/`**: User interface components built with CustomTkinter
  - `app.py`: Main GUI window and event handling
  - `components/`: Reusable UI components (buttons, tabs, themes)
  - `handlers/`: Event handlers for different controls
- **`src/midi/`**: MIDI processing and engine components
  - `ports.py`: MIDI port discovery and management
  - `processor.py`: Main MIDI message processing
  - `engine.py`: Async MIDI engine with threading
  - `arp/`: Arpeggiator subsystem
    - `engine_refactored.py`: Main arpeggiator logic
    - `modes.py`: Different arpeggiator patterns
    - `timing.py`: Rhythm and tempo handling
    - `note_producer.py`: Note generation algorithms
  - `harmony/`: Harmony generation subsystem
    - `engine.py`: Scale-based harmonic accompaniment logic
    - `harmony_generator.py`: Generates harmony notes snapped to scale
    - `voice_manager.py`: Manages polyphonic harmony voices

### Key Design Patterns
- **Dependency Injection**: AppContext provides shared dependencies
- **Async Processing**: Non-blocking MIDI processing with asyncio
- **Threading**: Separate threads for GUI and MIDI engine
- **Observer Pattern**: Event-driven communication between components
- **Factory Pattern**: Dynamic handler and component creation

## Requirements

- Python 3.8+
- Miniconda or Anaconda (recommended for environment management)
- MIDI devices or virtual MIDI ports
- macOS, Windows, or Linux

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd midi_echo
   ```

2. **Create and activate a conda environment**:
   ```bash
   conda create -n voi python=3.12
   conda activate voi
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `mido`: Core MIDI library
   - `python-rtmidi`: MIDI backend
   - `numba`: Performance optimization for audio processing
   - `python-dotenv`: Environment variable management
   - `customtkinter`: Modern GUI framework
   - Testing dependencies (`pytest`, `pytest-cov`, `pytest-asyncio`)

## Configuration

Create a `.env` file in the project root with your settings:

```env
# Required: MIDI output port name (partial match supported)
OUTPUT=your_midi_output_device

# Optional: Enable verbose logging
VERBOSE=true

# Optional: List available ports and exit
LIST_PORTS=false

# UI Configuration
WINDOW_WIDTH=800
WINDOW_HEIGHT=600
THEME_MODE=dark

# Performance settings
SHORT_PRESS_THRESHOLD=200
LONG_PRESS_THRESHOLD=500
HOLD_INCREMENT_RATE=50

# Preset configuration
DEFAULT_PRESET=0
PRESET_RANGE_MAX=127
```

### Finding MIDI Ports

To list available MIDI ports:

```bash
conda activate voi
python main.py
```

Set `LIST_PORTS=true` in your `.env` file, run the command, and note the available input/output names.

## Usage

1. **Configure your environment**:
   - Set up your MIDI devices or virtual ports
   - Edit `.env` with your output port name

2. **Run the application**:
   ```bash
   conda activate voi
   python main.py
   ```

3. **Using the GUI**:
   - **Pattern Tab**: Click steps to enable/disable notes, right-click for accents
   - **Modes Tab**: Select arpeggiator mode (up, down, random, etc.)
   - **Timing Tab**: Adjust tempo and swing
   - **Velocity Tab**: Set note velocities
   - **Advanced Tab**: Fine-tune parameters
   - **Preset Buttons**: Save/load configurations
   - **Control Buttons**: Transpose, octave, channel controls

4. **Live Performance**:
   - Play notes on your MIDI keyboard
   - Use the GUI buttons for real-time adjustments
   - Press and hold buttons for continuous changes

### Keyboard Shortcuts
- `Ctrl+C`: Exit the application
- GUI buttons support short/long presses for different actions

## Development

### Project Structure
```
midi_echo/
├── main.py                 # Application entry point
├── src/
│   ├── config/            # Configuration management
│   ├── gui/               # GUI components and handlers
│   ├── midi/              # MIDI processing engines
│   └── input/             # Input handling utilities
├── tests/                 # Unit and integration tests
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration (create this)
└── README.md             # This file
```

### Running Tests
```bash
conda activate voi
pytest
```

### Building and Debugging
- Use VS Code with the provided launch configuration
- The application uses asyncio for MIDI processing and threading for GUI separation
- Logging is configured for development debugging

## Troubleshooting

### Common Issues
- **No MIDI ports found**: Ensure MIDI devices are connected and drivers installed
- **GUI not responding**: Check that CustomTkinter is properly installed
- **High latency**: Adjust buffer sizes in MIDI settings or use a dedicated audio interface
- **Import errors**: Verify conda environment is activated and dependencies installed

### Performance Tips
- Use a dedicated MIDI interface for lowest latency
- Close other MIDI applications when using this tool
- Adjust `SHORT_PRESS_THRESHOLD` and `LONG_PRESS_THRESHOLD` for your playing style

### Platform-specific Notes
- **macOS**: Use IAC Driver for virtual MIDI ports
- **Windows**: Install MIDI drivers for your devices
- **Linux**: Use ALSA or JACK for MIDI routing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open-source. See LICENSE file for details.