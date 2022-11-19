# Voicebot CLI
Gives chat bots a voice using speech synthesis, speech to text, and GPT-3. Write a text file, get a voice bot.

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

See `chatbots/interview.txt`.

## Running the bot

Requires Python 3.6+. Tested on Mac M1.

1. Create an account with OpenAI and add your API key to `.env.secrets`

2. Install python requirements.

```bash
# Ensure you're using python 3.6+
python3 --version

# Uses your default python environment
pip3 install -r requirements.txt

# Alternatively, create a virtual environment (recommended)
pip3 install virtualenv
virtualenv .venv --python python3
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run some examples

```bash
# Run the basic assistant demo. Type "exit" to end the chat.
python cli.py --user-name Brendan --prompt-file chatbots/assistant.txt

# Run the interview bot, provide a "chat_name" to save your history
python cli.py --user-name Brendan --prompt-file chatbots/interview.txt --chat-name my_interview

# Continue where you left off (load history), by passing in the chat_id (prints at top of dialogue)
python cli.py --user-name Brendan --prompt-file chatbots/interview.txt --chat-id my_interview_971d58d4
```


## Creating a new bot

1. Create a new instruction file in `chatbots/` like `chatbots/my_new_bot.txt`.
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
python cli.py --user-name Brendan --prompt-file chatbots/my_new_bot.txt
```

Look at some of the examples in `chatbots/` for guidance.
