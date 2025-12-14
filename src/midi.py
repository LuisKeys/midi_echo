import mido


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
        if not self.inputs:
            print("No MIDI inputs available")
            return
        if not self.outputs:
            print("No MIDI outputs available")
            return
        input_name = next(inp for inp in self.inputs if "esi" not in inp.lower())
        output_name = self.outputs[0]
        print(f"Echoing from {input_name} to {output_name}")
        try:
            with mido.open_input(input_name) as inp, mido.open_output(
                output_name
            ) as outp:
                for msg in inp:
                    outp.send(msg)
        except KeyboardInterrupt:
            print("Echo stopped")
