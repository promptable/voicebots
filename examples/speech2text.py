"""Example speech2text demo

python -m examples.speech2text main
"""

import click

from voicebots import text_utils
from voicebots.asr.google_transcriber import GoogleTranscriber

# List of common phrases we expect. Used to "prime" speech rec provider
# and improve results
SUPPORTED_PHRASES = []


def _get_transcriber():
    return GoogleTranscriber(
        supported_phrases=SUPPORTED_PHRASES, single_utterance=False
    )


@click.group()
@click.option("--debug", default=False)
def cli(debug: bool):
    """Possibly enable debug logging"""
    pass


@cli.command()
def main():
    """Convert text to speech.
    Say "exit" to exit program (or wait 10 sec).
    """
    listener = _get_transcriber()
    click.echo(f"Listening... Say something!")
    while True:
        transcripts = listener.listen()
        for transcript in transcripts:
            if transcript.is_final:
                if transcript.deadline_exceeded:
                    click.echo(f"Silence detected. Exiting...")
                    return
                text = transcript.text.strip()
                if text:
                    # Currently most of these are for OAI ASR
                    # Google appears to translate more literally - different class of error
                    # text = asr.replace_asr_errors(
                    #     text,
                    #     replacements=asr.ASR_ERROR_REPLACEMENTS,
                    #     debug=False,
                    # )
                    click.echo(f"Final transcript: '{text}'")
                    if text == "exit":
                        return
            elif transcript.text is not None:
                text_utils.display_live_transcription(
                    transcript.text, transcript.overwrite_chars
                )
            else:
                click.echo(f"No results yet.")


if __name__ == "__main__":
    cli()
