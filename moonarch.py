import autochord
import pretty_midi
import librosa
class MusicToChordsConverter:
    def __init__(self, audio_file):
        self.audio_file = audio_file
        self.chords = None
        self.midi_chords = pretty_midi.PrettyMIDI()
        self.instrument_chords = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano

    def recognize_chords(self):
        """
        Perform chord recognition on the audio file.
        """
        self.chords = autochord.recognize(self.audio_file, lab_fn='chords.lab')

    def chord_to_midi_notes(self, chord_name):
        """
        Map chord names to MIDI notes.

        Args:
        chord_name (str): The chord name to be mapped.

        Returns:
        list: A list of MIDI notes corresponding to the chord.
        """
        note_mapping = {
            'C:maj': ['C4', 'E4', 'G4'],
            'C:min': ['C4', 'E-4', 'G4'],
            'D:maj': ['D4', 'F#4', 'A4'],
            'D:min': ['D4', 'F4', 'A4'],
            'E:maj': ['E4', 'G#4', 'B4'],
            'E:min': ['E4', 'G4', 'B4'],
            'F:maj': ['F4', 'A4', 'C5'],
            'F:min': ['F4', 'A-4', 'C5'],
            'G:maj': ['G4', 'B4', 'D5'],
            'G:min': ['G4', 'B-4', 'D5'],
            'A:maj': ['A4', 'C#5', 'E5'],
            'A:min': ['A4', 'C5', 'E5'],
            'B:maj': ['B4', 'D#5', 'F#5'],
            'B:min': ['B4', 'D5', 'F#5']
        }
        return note_mapping.get(chord_name, [])

    def generate_midi(self):
        """
        Generate a MIDI file from the recognized chords.
        """
        for chord in self.chords:
            start_time = chord[0]
            end_time = chord[1]
            chord_name = chord[2]
            if chord_name != 'N':  # Ignore no-chord
                chord_notes = self.chord_to_midi_notes(chord_name)
                for note_name in chord_notes:
                    midi_note = pretty_midi.Note(
                        velocity=100,
                        pitch=librosa.note_to_midi(note_name),
                        start=start_time,
                        end=end_time
                    )
                    self.instrument_chords.notes.append(midi_note)

        self.midi_chords.instruments.append(self.instrument_chords)

    def save_midi(self, output_file):
        """
        Save the generated MIDI file to disk.

        Args:
        output_file (str): The path where the MIDI file should be saved.
        """
        self.midi_chords.write(output_file)
        print(f"Saved chords to {output_file}")
