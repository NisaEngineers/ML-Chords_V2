# app/main.py

import os
import shutil
import uuid
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from moonarch import MusicToChordsConverter
from mido import MidiFile, MidiTrack, Message
import pretty_midi

app = FastAPI(title="Moonarch Chords Analyzer API", version="1.0.0")

# Helper function to save MIDI properly
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

@app.post("/analyze/", summary="Upload a song and extract chords as MIDI")
async def analyze_audio(file: UploadFile = File(...)):
    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only mp3 or wav allowed.")

    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, file.filename)

        # Save uploaded file
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Process audio to chords
        converter = MusicToChordsConverter(input_path)
        converter.recognize_chords()
        converter.generate_midi()

        # Save MIDI
        midi_filename = f"{uuid.uuid4()}.mid"
        output_midi_path = os.path.join(temp_dir, midi_filename)
        save_midi(converter, output_midi_path)

        # Return the MIDI file for download
        return FileResponse(output_midi_path, media_type='audio/midi', filename=midi_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    finally:
        # Cleanup (optional: if you want to clean temp files after some time instead)
        pass

@app.get("/", summary="Health check")
async def root():
    return JSONResponse(content={"message": "Moonarch Chords Analyzer API is up and running 🚀"})
