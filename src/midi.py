import mido
import os


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
        input_name = os.environ.get("INPUT")
        output_name = os.environ.get("OUTPUT")
        if not input_name:
            print("INPUT environment variable not set")
            return
        if not output_name:
            print("OUTPUT environment variable not set")
            return
        print(f"Echoing from {input_name} to {output_name}")
        try:
            with mido.open_input(input_name) as inp, mido.open_output(
                output_name
            ) as outp:
                for msg in inp:
                    outp.send(msg)
        except KeyboardInterrupt:
            print("Echo stopped")
