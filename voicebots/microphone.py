"""Utilities for interacting with microphone.

References:
https://cloud.google.com/speech-to-text/docs/streaming-recognize#speech-streaming-recognize-python
https://github.com/googleapis/python-speech/blob/master/samples/microphone/transcribe_streaming_infinite.py
https://github.com/googleapis/python-speech/blob/master/samples/microphone/transcribe_streaming_mic.py
https://github.com/Uberi/speech_recognition/blob/master/examples/threaded_workers.py
https://github.com/daanzu/kaldi-active-grammar/blob/master/examples/audio.py (new)

This has an example of "activity detection" which would handle silence and chaining commands.
https://github.com/daanzu/dragonfly/blob/kaldi/dragonfly/engines/backend_kaldi/audio.py (example with Kaldi)
"""
import logging
import queue

import pyaudio

logger = logging.getLogger(__name__)


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        """Initialize the MicrophoneStream

        Args:
            rate (int): Sampling rate. Number of frames per second.
            chunk (int): Buffer length. Number of frames to accumulate before returning audio to caller.
        """
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def open_stream(self):
        logger.debug("Turning ON the microphone!")
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def close_stream(self):
        logger.debug("Turning OFF the microphone!")
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

    def __enter__(self):
        return self.open_stream()

    def __exit__(self, type, value, traceback):
        self.close_stream()
