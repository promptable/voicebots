"""Utilities for working with audio data.

Requires pydub and pyaudio to be installed.

Python libraries for playing audio:
- https://github.com/TaylorSMarks/playsound (simple, play from file only)
- https://github.com/jleb/pyaudio (low-level)
- https://github.com/jiaaro/pydub (popular!)
- https://github.com/hamiltron/py-simple-audio (pydub benefits from this being installed)

NOTE: Might need to `brew install ffmpeg`
"""

from pathlib import Path

from pydub import AudioSegment
from pydub.playback import play


def play_audio_bytes(bytes):
    # LINEAR_16 / Wav encoding
    sound = AudioSegment(data=bytes)
    play(sound)


def play_audio_from_file(fpath):
    sound = AudioSegment.from_file(fpath, format="wav")
    play(sound)


def save_audio_to_file(fpath, audio_bytes, tags=None):
    Path(fpath).parent.mkdir(parents=True, exist_ok=True)
    sound = AudioSegment(data=audio_bytes)
    sound.export(fpath, format="wav", tags=tags)


def load_audio_from_file(fpath, format="wav"):
    # https://github.com/jiaaro/pydub/issues/402
    # sound = AudioSegment.from_file(fpath, format="wav")
    # sound.raw_data  <-- doesn't have headers
    with open(fpath, "rb") as f:
        audio_bytes = f.read()
    return audio_bytes
