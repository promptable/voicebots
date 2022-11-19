import hashlib
import sys


def normalize_text(text: str):
    """Basic cleanup of text."""
    return text.lstrip().rstrip().lower()


def display_live_transcription(transcript, overwrite_chars):
    """Print interim results of live transcription to stdout.
    We include a carriage return at the end of the line, so subsequent lines will overwrite
    them. If the previous result was longer than this one, we need to print some extra
    spaces to overwrite the previous result
    """
    sys.stdout.write(transcript + overwrite_chars + "\r")
    sys.stdout.flush()


def hash_normalized_text(text, normalize=True):
    if normalize:
        text = normalize_text(text)
    text = text.encode("utf-8")
    return hashlib.sha256(text).hexdigest()
