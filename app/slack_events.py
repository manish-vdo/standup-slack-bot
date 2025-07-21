# app/slack_events.py
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
import os
from dotenv import load_dotenv
from db import add_user, save_response

load_dotenv()

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)
handler = SlackRequestHandler(app)

QUESTIONS = [
    "1. What did you do yesterday?",
    "2. What are you working on today?",
    "3. Any blockers?"
]

# When app is opened, register user
@app.event("app_home_opened")
def handle_home(event, say):
    user_id = event["user"]
    team_id = event["team"]
    add_user(user_id, team_id)
    say(f"👋 Hi <@{user_id}>, I'll start asking you daily standup questions!")

# Optional command
@app.command("/standup")
def manual_standup(ack, command, client):
    ack()
    user = command["user_id"]
    for q in QUESTIONS:
        client.chat_postMessage(channel=user, text=q)

@app.message("")
def handle_message(message, say):
    user = message.get("user")
    text = message.get("text")
    save_response(user, "Manual message", text)

