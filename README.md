# TG-bot for getting help in Calculus theory
This is an app for a bot that answers theoretical questions on mathematical analysis.

## Requirements:
- Python 3.12

## Installation:
1. Create venv:
```
python3 -m venv venv
source venv/bin/activate
```

2. Install packages:
```
pip install -r requirements.txt
```

3. Create `.env` file with all env variables 
```bash
TG_BOT_TOKEN=
OLLAMA_MODEL=
```

## Running a bot
1. Build the vector Database 
```
python preparing_db.py
```

2. Run the bot:
```
python bot_ollama.py
```

## TODO-list
- [ ] Add an ability to remember the dialog context
- [ ] Add the database for all users and save theirs chats