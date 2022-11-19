"""Voice bot CLI.

Usage:
    python -m cli --user-name Brendan --prompt-file chatbots/assistant.txt

Say "exit" or "goodbye" to end the chat.
"""
import sys
import time
import traceback
from typing import Dict

import click
import diskcache
from prompt_toolkit import print_formatted_text as print

from voicebots import audio_utils
from voicebots.asr.google_transcriber import GoogleTranscriber
from voicebots.speech import google_speech
from voicebots.settings import Settings
from voicebots.oai_client import OAIClient
from voicebots import chat_utils

DEFAULT_VOICE_NAME = "en-IN-Wavenet-A"  # "en-GB-Neural2-C"
POST_SPEECH_SLEEP_TIME_SEC = 0
# List of common phrases we expect. Used to "prime" speech rec provider
# and improve results
SUPPORTED_PHRASES = []

# Update PROMPT_CONFIG to customize your experience.
PROMPT_CONFIG = {
    "model": "text-davinci-002",
    "temperature": 0.7,
    "max_tokens": 50,
    "logit_bias": {198: -100},  # Prevent "\n" from being generated
}

def get_prompt_config(user_name: str, agent_name: str) -> Dict:
    """Get prompt config for chatbot.

    What this does:
    - Handles adding stop tokens based on user/agent names
    - Prevents newlines from being generated (you can disable this if you want)
    - Returns a copy of PROMPT_CONFIG with your custom params.
    """
    params = PROMPT_CONFIG.copy()
    params["stop"] = ["\n", f"{user_name}:", f"{agent_name}:"]
    print(params)
    return params


def user_desires_call_end(text: str) -> bool:
    # TODO(bfortuner): Replace with regex / fuzzy match
    clean_text = (
        text.strip().lower().replace(".", "").replace("?", "").replace("!", ".")
    )

    # Direct commands (allow deterministic exit)
    if clean_text in ["exit", "end call"]:
        return True

    end_call_phrases = [
        "goodbye",
        "good bye",
        "bye now",
    ]
    for phrase in end_call_phrases:
        if phrase in clean_text:
            return True
    return False



def _get_transcriber():
    return GoogleTranscriber(
        supported_phrases=SUPPORTED_PHRASES, single_utterance=False
    )


def speak_text(text=None, ssml=None, enable=True, voice=DEFAULT_VOICE_NAME):
    if enable:
        audio_bytes = google_speech.load_or_convert_text_to_speech(
            text=text, ssml=ssml, voice_name=voice
        )
        audio_utils.play_audio_bytes(audio_bytes)
        time.sleep(POST_SPEECH_SLEEP_TIME_SEC)


@click.command()
@click.option(
    "--prompt-file",
    default="chatbots/assistant.txt",
    help="Path to your customized prompt.txt file",
)
@click.option(
    "--secrets-file",
    default=".env.secret",
    help="Path to .env.secrets file with env variables"
)
@click.option(
    "--user-name",
    default="Human",
    help="First name of user.",
)
@click.option(
    "--agent-name",
    default="Assistant",
    help="First name of agent.",
)
@click.option(
    "--chat-id",
    help="Unique id for the chat (allows loading/testing historical chat). If provided, other arguments are ignored.",
)
@click.option(
    "--chat-name",
    default="test_chat",
    help="Unique-ish name for the chat (allows loading/testing historical chat). Not required if chat_id is provided.",
)
def chat(
    prompt_file: str,
    secrets_file: str,
    user_name: str,
    agent_name: str,
    chat_id: str,
    chat_name: str,
):
    """Run a chat session with the Agent."""
    ctx = Settings.from_env_file(secrets_file)

    listener = _get_transcriber()

    cache = diskcache.Cache(directory=ctx.disk_cache_dir)
    oai_client = OAIClient(
        ctx.openai_api_key,
        organization_id=ctx.openai_org_id,
        cache=cache,
    )
    prompt_config = get_prompt_config(
        user_name=user_name, agent_name=agent_name
    )
    opening_line, prompt_text = chat_utils.get_prompt_text(
        prompt_file=prompt_file, user_name=user_name, agent_name=agent_name
    )

    agent_text_fn = chat_utils.get_write_text_fn(agent_name, "bot")
    user_text_fn = chat_utils.get_write_text_fn(user_name, "user")

    # Load historical chat if available
    turns = []
    if chat_id is not None:
        turn_dict = chat_utils.load_turns(chat_id=chat_id, turns_dir=ctx.chat_turns_dir)
        turns = turn_dict["turns"]
        click.echo(chat_utils.build_transcript(turns))
        user_name = turn_dict["user_name"]
    else:
        chat_id = chat_utils.make_chat_id(chat_name)
        click.echo(f"Chat Id: {chat_id}")
        speak_text(opening_line)
        agent_text_fn(opening_line)
        turns.append({"speaker": "agent", "text": opening_line})

    exit_loop = False
    while not exit_loop:
        # Begin transcribing microphone audio stream
        # TODO(bfortuner): Handle transcriber error (retry/backoff)
        transcripts = listener.listen()
        for transcript in transcripts:

            # If user desires exit or silence for 10 seconds, end the call.
            if exit_loop or transcript.deadline_exceeded:
                exit_loop = True
                break

            # Only a partial, continue
            user_text = transcript.text.strip()
            if not transcript.is_final or not user_text:
                continue
                
            try:
                user_text_fn(user_text)
                turns.append({"speaker": "user", "text": user_text})
                if user_desires_call_end(user_text):
                    exit_loop = True
                else:
                    agent_text = chat_utils.chat_prompt(
                        turns=turns,
                        user_name=user_name,
                        agent_name=agent_name,
                        prompt_text=prompt_text,
                        prompt_config=prompt_config,
                        oai_client=oai_client,
                    )
                    speak_text(text=agent_text)
                    agent_text_fn(agent_text)
                    turns.append({"speaker": "agent", "text": agent_text})
            except Exception as e:
                click.echo(e)
                traceback.print_exc(file=sys.stdout)

    chat_utils.save_turns(
        chat_id=chat_id,
        turns=turns,
        user_name=user_name,
        agent_name=agent_name,
        turns_dir=ctx.chat_turns_dir,
    )


if __name__ == "__main__":
    chat()
