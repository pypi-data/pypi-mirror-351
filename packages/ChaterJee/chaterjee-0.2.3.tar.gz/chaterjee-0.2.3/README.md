# ChaterJee

<img src="ChaterJee/ProfilePhoto.png" alt="ChaterJee" width="200"/>

Often, we need to run computational `trial and error` experiments by just tweaking one or two key parameters. In machine learning, you face similar problems during hyperparameter tuning experiments. 

These are probably the most boring, time-consuming, yet unavoidable phases in our day-to-day research. But what if your experiments could keep working while you're at a date XD ? What if you could kick off a hyperparameter tuning run just before bed — and wake up with results and plots waiting on your phone, like a good morning message from your research? Real-time updates, one-tap reruns, and zero late-night debugging. It’s like having a research assistant in your pocket.

Let me introduce ChaterJee to you — a playful fusion of `Chater`, meaning one who chats, and `Jee`, an honorific used in Indian culture to show respect. Think of `ChaterJee` as the lab assistant you always wanted — one who actually responds, never crashes your code, doesn't ask for co-authorship, and definitely doesn't need coffee all the time, unlike you.

# Installation
You need two things:
 1. The `ChaterJee` module
 2. A telegram BOT that you own

## Installing the module
I recommend to install `ChaterJee` module inside your project's conda environment for a seamless experience. 
```bash
conda activate yourenv
pip install ChaterJee
```

## Get your telegram BOT
To use this `ChaterJee`, you'll need a Telegram Bot Token and your Chat ID. Follow these simple steps:

### Create a Bot and Get the Token
- Open Telegram and search for **@BotFather**.
- Start a chat and send the command `/newbot`.
- Follow the prompts: choose a name and a username for your bot.
- Once done, **BotFather** will give you a **bot token** — a long string like `123456789:ABCdefGhiJKlmNoPQRsTuvWXyz`.

### Get Your Chat ID
- Open Telegram and start a chat with your newly created bot by searching its username.
- Send `Hi` (any message) to your bot.
- Open your browser and visit this URL, replacing `YOUR_BOT_TOKEN` with your token:
`
https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getUpdates
`

    with the above token, this URL becomes:
`
https://api.telegram.org/bot123456789:ABCdefGhiJKlmNoPQRsTuvWXyz/getUpdates
`
- Look for `"chat":{"id":...}` in the JSON response. This number is your **Chat ID**.


# Quick Start
`ChaterJee` has two components. 
 - `NoteLogs` class: This stores log files, and save project locations for parsing updates.
 - `ChatLogs` class: This reads log files, the last line is sent to you via the BOT. It can also share you final plots that you need for your next rerun.

## The minimal example
This will register your JOB with the given `JOB_NAME` and logfiles into a JSON file, `<your home>/.data/JOB_status.json`.

```python
# This is a minimal example
import ChaterJee

# your code here
JOB_NAME = "job_0.1.10"
OUT_NAME = "experiment_0.1"

for i in range(N):
    # Your code here
    notelogs = ChaterJee.NoteLogs()
    notelogs.write(f"{JOB_NAME}",\
    logSTRING=f"Step {i} done.",\
    logFILE=f"{OUT_NAME}.log",\
    logIMAGE=f"{OUT_NAME}.png")
 ```

Next step is to receive updates on your projects. 

```python
# Run this instance separately to parse job updates
# This is the one which actually communicates with your BOT.

import ChaterJee

if __name__ == '__main__':
    TOKEN = '123456789:ABCdefGhiJKlmNoPQRsTuvWXyz'
    CHATID = '123456789'

    cbot = ChaterJee.ChatLogs(TOKEN, CHATID)
    cbot.cmdTRIGGER()
```