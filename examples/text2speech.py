"""Example Text to Speech.

python -m examples.text2speech main --user-name Brendan
"""
from textwrap import dedent
import time

import click

from voicebots.speech import google_speech
from voicebots import audio_utils

AGENT_NAME = "Athena"
USER_NAME = "Brendan"
DEFAULT_VOICE_NAME = "en-IN-Wavenet-A"  # "en-GB-Neural2-C"
POST_SPEECH_SLEEP_TIME_SEC = 0

LINES_TEXT = {
    "opening": dedent(
        """
        Hello {user_name}, My name is {agent_name}. How can I help you today?
    """
    ).strip(),
    "closing": dedent(
        """
        Okay, have a nice day!
    """
    ).strip(),
}


def get_line(line_name: str, user_name: str, agent_name: str = AGENT_NAME):
    return LINES_TEXT[line_name].format(user_name=user_name, agent_name=agent_name)


def speak_text(text=None, ssml=None, enable=True, voice=DEFAULT_VOICE_NAME):
    if enable:
        audio_bytes = google_speech.load_or_convert_text_to_speech(
            text=text, ssml=ssml, voice_name=voice
        )
        audio_utils.play_audio_bytes(audio_bytes)
        time.sleep(POST_SPEECH_SLEEP_TIME_SEC)


@click.group()
@click.option("--debug", default=False)
def cli(debug: bool):
    """Possibly enable debug logging"""
    pass


@cli.command()
@click.option(
    "--agent-name",
    default=AGENT_NAME,
    help="Last name of the doctor",
)
@click.option(
    "--user-name",
    default=USER_NAME,
    help="Firsty name of the patient",
)
def main(agent_name, user_name):
    """Convert speech to text."""
    intro_line = get_line("opening", user_name, agent_name)
    closing_line = get_line("closing", user_name, agent_name)
    speak_text(ssml=intro_line)
    while True:
        text = click.prompt("Enter text")
        if text == "exit":
            speak_text(ssml=closing_line)
            return
        speak_text(text=text)


if __name__ == "__main__":
    cli()
