#!/bin/bash
# Run MIDI Echo with system C++ libraries to fix sounddevice loading

export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/lib:${LD_LIBRARY_PATH}

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate ai

# Run the application
python main.py "$@"
