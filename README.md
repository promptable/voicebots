# Voicebot CLI

Give chat bots a voice using speech synthesis and GPT-3.

Adds audio/speech on top of https://github.com/bfortuner/textbots.

## Build a new voice bot

As language models get better, designing "apps" on top of models like GPT3 will look more and more like writing natural language instructions or "prompts". Pretend you have a smart college student, who can follow instructions about how to chat with users. What would you tell them?

Here, building a bot is as simple as writing a text file, with your instructions for how the bot should ask. That's it.

Here are some examples:

### Personal Assistant

An open-ended chat bot for talking about pretty much anything.

> opening_line: Hello {user_name}, how can I help you?
> \#\#\#\#\#\#
>
> Below is a conversation between a knowledgable, helpful, and witty AI assistant and a user, who has some questions about a topic. The AI assistant is able to answer the user's questions and provide additional information about the topic. The AI assistant is able to keep the conversation focused on the topic and provide relevant information to the user. The closer the AI agent can get to answering the user's questions, the more helpful the AI agent will be to the user.
>
> {transcript}
> Assistant:

Here `{user_name}` is replaced with the name you pass as a CLI argument. `{transcript}` is replaced with the dialogue history.

### Interview Bot

A chat bot who gives system design interviews!

> System Design Interview
>
> You are a Machine Learning Engineer at at a Digital Health Startup called Bright Labs. Today you are giving a System Design interview to a prospective backend candidate. Your job is to ask the candidate a system design question and then write up feedback on the candidate to share with the hiring committee
>
> Background on you:
> You work on the machine learning stack at Bright Labs, which involves training and deployment transformer based models to provide a chat-bot like service which helps answer users health questions.
>
> Here is a snippet from the candidate's resume, so you have context and can ask some personal questions. And tailor the interview to the candidate's experiences.
>
> Candidate: {user_name}
>
> Resume:
>
> (prompt continues)

See `examples/interview.txt`.

## Running the bot

Requires Python 3.7+. Tested on Mac M1.

### 1. Setup LLM Provider - OpenAI

Create an account with OpenAI and add your API key to `.env.secrets`

### 2.Setup Google Cloud SDK (for ASR/Speech)

First, create a GCP account + project.
Next, enable the text2speech and speech2text APIs in GCP.
Next, install the SDK and log in
https://cloud.google.com/sdk/docs/install

```
gcloud init (set project to 'YOUR_PROJECT_YOU_SET_UP')
gcloud config list
```

Should see something like

```
[core]
account = bfortuner@gmail.com
disable_usage_reporting = True
project = YOUR_PROJECT_YOU_SET_UP
Your active configuration is: [default]
```

Login to get credentials

```
gcloud auth application-default login
```

### Install Requirements

#### MacOS - M1/M2

0. Ensure XCode, Homebrew, Rust compiler are installed

```bash
# Install XCode (if not installed)

# Install Rust Compiler (if not installed) https://github.com/huggingface/transformers/issues/2831
```

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

```

# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

1. Install homebrew prerequisites

```bash
brew install openssl portaudio
brew link portaudio
```

2. Grpcio Install - add these to to .zshrc / .bashrc (replace paths to libs if required)

```
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
export PATH="/opt/homebrew/opt/openssl@3/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

pip install --no-cache-dir --upgrade --force-reinstall -Iv grpcio
```

3. PyAudio Install

Create a pydistutils config file with the portaudio lib paths

NOTE: PUT THIS IN YOUR HOME DIR!!!

```bash
cat <<EOF >> .pydistutils.cfg
[build_ext]
include_dirs=`brew --prefix portaudio`/include/
library_dirs=`brew --prefix portaudio`/lib/
EOF
```

4. Python requirements

```
pip install -r requirements.txt
```

## Run some examples

```bash
# Verify ASR (speech-to-text) works
python -m examples.speech2text main

# Verify voice synthesis (text-to-speech) works
python -m examples.text2speech main

# Run the basic assistant demo. Type "exit" to end the chat.
python -m cli --user-name Brendan --prompt-file examples/assistant.txt

# Run the interview bot, provide a "chat_name" to save your history
python -m cli --user-name Brendan --prompt-file examples/interview.txt --chat-name my_interview

# Continue where you left off (load history), by passing in the chat_id (prints at top of dialogue)
python -m cli --user-name Brendan --prompt-file examples/interview.txt --chat-id my_interview_971d58d4
```

## Creating a new bot

1. Create a new instruction file in `examples/` like `examples/my_new_bot.txt`.
2. Add your opening line at the top of the file, followed by 6 hashtags `######`.

```txt
opening_line: Hello, how can I help you?
######
<instructions here>
```

3. Add your instructions!
4. Add your final line, typically:

```txt
{transcript}
YourBotName:
```

Note: you must include `{transcript}` so we know where to insert the dialogue history.

4. Run your bot! Type "exit" to end the chat.

```bash
python cli.py --user-name Brendan --prompt-file examples/my_new_bot.txt
```

Look at some of the examples in `examples/` for guidance.
