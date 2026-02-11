import mido
import os
import time


class MidiHandler:
    def __init__(self):
        self.inputs = mido.get_input_names()
        self.outputs = mido.get_output_names()

    def list(self):
        print("MIDI Inputs:")
        for inp in self.inputs:
            print(f"  {inp}")
        print("MIDI Outputs:")
        for out in self.outputs:
            print(f"  {out}")

    def echo(self):
        output_hint = os.environ.get("OUTPUT")
        if not output_hint:
            print("OUTPUT environment variable not set")
            return

        available_outputs = mido.get_output_names()
        output_name = next(
            (out for out in available_outputs if output_hint in out), None
        )

        if not output_name:
            print(f"Could not find an output matching: {output_hint}")
            print(f"Available outputs: {available_outputs}")
            return

        input_names = mido.get_input_names()
        if not input_names:
            print("No MIDI-input ports found.")
            return

        # Filter out 'Midi Through' and the output port itself to prevent loops/hangs
        filtered_inputs = [
            n for n in input_names if "Midi Through" not in n and output_name != n
        ]

        if not filtered_inputs:
            print(
                f"No valid input ports found after filtering. Available: {input_names}"
            )
            return

        print(f"Echoing from: {', '.join(filtered_inputs)}")
        print(f"To output: {output_name}")

        inputs = []
        try:
            # Open all available inputs
            for name in filtered_inputs:
                try:
                    inputs.append(mido.open_input(name))
                except Exception as e:
                    print(f"Could not open input {name}: {e}")

            if not inputs:
                print("Could not open any MIDI-input ports.")
                return

            with mido.open_output(output_name) as outp:
                print("Polling for messages... (Ctrl+C to stop)")
                while True:
                    for inp in inputs:
                        # Non-blocking check for messages from this input
                        for msg in inp.iter_pending():
                            outp.send(msg)
                            if msg.type not in ["clock", "active_sensing"]:
                                print(f"Echoed: {msg}")
                    # Tiny sleep to reduce CPU load while remaining responsive
                    import time

                    time.sleep(0.001)
        except Exception as e:
            print(f"Error during echo session: {e}")
        finally:
            for p in inputs:
                p.close()
