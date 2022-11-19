import dataclasses
from dataclasses import dataclass
from typing import Iterable


@dataclass
class Transcript:
    """Stores transcribed speech and metadata.

    Attributes:
        text (str): The transcribed text.
        is_final (bool): Whether the transcript contains the final result or interim results.
        deadline_exceeded (bool): Indicates whether the transcriber exited early due to user inactivity.
        overwrite_chars (str): Used for display purposes when logging interim results to the console. If the last
            `text` result was longer, overwrite_chars is used to clear the console of the longer result.
    """

    text: str
    is_final: bool
    deadline_exceeded: bool = False
    overwrite_chars: str = ""

    def dict(self):
        return dataclasses.asdict(self)


class Transcriber:
    """Base class for all speech-to-text listeners.
    These classes transcribe microphone audio to text. In the future,
    we should also support pre-recorded audio files for integration tests.
    """

    def listen(self) -> Iterable[Transcript]:
        raise NotImplementedError
