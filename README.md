# MIDI Echo

A simple Python application that lists available MIDI input and output ports and provides an echo functionality to forward MIDI messages from the first available input port to the first available output port.

## Purpose

This tool is designed for MIDI enthusiasts, musicians, and developers working with MIDI devices. It allows you to:
- List all connected MIDI input and output ports on your system
- Test MIDI connections by echoing messages in real-time
- Create a basic MIDI through-router for simple setups

The echo functionality runs in an endless loop, forwarding all types of MIDI messages (notes, control changes, etc.) from input to output until interrupted.

## Requirements

- Python 3.7+
- Miniconda (recommended for environment management)
- MIDI devices or virtual MIDI ports for testing

## Installation

1. Clone or download this repository:
   ```bash
   git clone <repository-url>
   cd midi_echo
   ```

2. Create and activate a conda environment (optional but recommended):
   ```bash
   conda create -n midi_echo python=3.12
   conda activate midi_echo
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   This will install:
   - `mido`: MIDI library for Python
   - `python-rtmidi`: Backend for MIDI I/O

## Usage

Run the application using the miniconda Python interpreter:

```bash
/Users/luc/miniconda3/bin/python main.py
```

The application will:
1. Display a list of available MIDI input ports
2. Display a list of available MIDI output ports
3. Attempt to start echoing from the first input to the first output

If no MIDI ports are available, it will display error messages and continue trying.

To stop the echo loop, press `Ctrl+C`.

## Configuration

The application automatically uses the first available input and output ports. For more advanced usage, you can modify the `src/midi.py` file to select specific ports or add additional functionality.

## Development

The project structure:
- `main.py`: Entry point that initializes and runs the MIDI handler
- `src/midi.py`: Contains the `MidiHandler` class with MIDI port management and echo functionality
- `requirements.txt`: Python dependencies
- `.vscode/launch.json`: VS Code debug configuration

## Troubleshooting

- **No MIDI ports found**: Ensure you have MIDI devices connected or virtual MIDI ports configured (e.g., using IAC Driver on macOS)
- **Import errors**: Make sure dependencies are installed in the correct Python environment
- **Permission errors**: On some systems, MIDI access may require special permissions

## License

This project is open-source. Feel free to modify and distribute.