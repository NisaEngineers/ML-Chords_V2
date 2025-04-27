import streamlit as st
import base64
import os
import time
from moonarch import MusicToChordsConverter
from mido import MidiFile, MidiTrack, Message
import pretty_midi

# Set the home directory path for moonarch
home_directory = os.getcwd()

# Your app content
st.title("Moonarch Chords Analyzer: Chords")
st.write("Extract chords from any given music.")

# Set the title of the app
st.title("Your Music, Perfected by AI")

# Display the header text
st.header("Experience the Future of Sound")
st.write("""
Everything you need to create and release your music, including samples, plugins, unlimited distribution, and the world's best AI mastering engine.
""")

# Display the Start button
if st.button("Start using Monaarch"):
    st.write("Welcome to Monaarch! Let's start creating amazing music.")

# Add upload option
audio_file = st.file_uploader("Upload a song", type=["mp3", "wav"])

if audio_file is not None:
    st.write("File uploaded successfully.")
    
    # Placeholder for progress bar
    progress_bar = st.progress(0)
    
    # Simulate file processing
    for percent_complete in range(100):
        time.sleep(0.01)
        progress_bar.progress(percent_complete + 1)
    
    st.write("File processing complete.")

    if st.button('Find Chords'):
        with st.spinner('Extracting chords and generating MIDI...'):
            # Convert the uploaded file to a file path
            file_name_without_ext = os.path.splitext(audio_file.name)[0]
            audio_file_path = os.path.join('/tmp', audio_file.name)
            with open(audio_file_path, 'wb') as f:
                f.write(audio_file.getbuffer())

            # Convert music to chords and save as MIDI
            output_midi_file = f'{file_name_without_ext}.mid'
            converter = MusicToChordsConverter(audio_file_path)
            converter.recognize_chords()
            converter.generate_midi()

            # Updated save_midi method to handle PrettyMIDI object and proper message formatting
            def save_midi(self, output_file):
                midi = MidiFile()
                track = MidiTrack()
                midi.tracks.append(track)

                # Ensure self.midi_chords is a PrettyMIDI object
                if not isinstance(self.midi_chords, pretty_midi.PrettyMIDI):
                    raise TypeError(f"self.midi_chords is not a PrettyMIDI object: {type(self.midi_chords)}")

                # Iterate over instruments and notes in the PrettyMIDI object
                for instrument in self.midi_chords.instruments:
                    for note in instrument.notes:
                        # Ensure note, velocity, and time are within valid MIDI data byte range
                        midi_note = min(max(note.pitch, 0), 127)
                        velocity = min(max(note.velocity, 0), 127)
                        start_time = max(int(note.start * 1000), 0)  # Convert to milliseconds
                        end_time = max(int(note.end * 1000), 0)  # Convert to milliseconds
                        duration = end_time - start_time  # Calculate duration

                        # Add note_on and note_off messages with correct formatting
                        track.append(Message('note_on', note=midi_note, velocity=velocity, time=start_time))
                        track.append(Message('note_off', note=midi_note, velocity=0, time=duration))

                midi.save(output_file)

            # Assign the updated method to the converter instance
            converter.save_midi = save_midi.__get__(converter, MusicToChordsConverter)
            converter.save_midi(output_midi_file)

            st.success('Chords extraction and MIDI generation complete!')

            # Provide a button to download the MIDI file
            with open(output_midi_file, 'rb') as f:
                st.download_button(
                    label="Download MIDI file",
                    data=f,
                    file_name=output_midi_file,
                    mime='audio/midi'
                )
