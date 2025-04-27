# moonarch_chords_extractor.py

import os
import sys
import uuid
import shutil
import tempfile
from moonarch import MusicToChordsConverter
from mido import MidiFile, MidiTrack, Message
import pretty_midi

def save_midi(converter: MusicToChordsConverter, output_file: str):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)

    if not isinstance(converter.midi_chords, pretty_midi.PrettyMIDI):
        raise TypeError(f"converter.midi_chords is not a PrettyMIDI object: {type(converter.midi_chords)}")

    for instrument in converter.midi_chords.instruments:
        for note in instrument.notes:
            midi_note = min(max(note.pitch, 0), 127)
            velocity = min(max(note.velocity, 0), 127)
            start_time = max(int(note.start * 1000), 0)  # ms
            end_time = max(int(note.end * 1000), 0)
            duration = end_time - start_time

            track.append(Message('note_on', note=midi_note, velocity=velocity, time=start_time))
            track.append(Message('note_off', note=midi_note, velocity=0, time=duration))

    midi.save(output_file)

def process_audio(input_audio_path: str):
    if not os.path.isfile(input_audio_path):
        print(f"Error: File {input_audio_path} does not exist.")
        sys.exit(1)

    if not input_audio_path.lower().endswith(('.mp3', '.wav')):
        print("Error: Only .mp3 and .wav files are supported.")
        sys.exit(1)

    # Create a temporary working directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Copy input file to temp dir
        filename = os.path.basename(input_audio_path)
        temp_audio_path = os.path.join(temp_dir, filename)
        shutil.copyfile(input_audio_path, temp_audio_path)

        print("Recognizing chords...")
        converter = MusicToChordsConverter(temp_audio_path)
        converter.recognize_chords()
        converter.generate_midi()

        output_filename = f"{os.path.splitext(filename)[0]}_
