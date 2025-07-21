# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from slack_sdk import WebClient
from db import SessionLocal, User
import os

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

QUESTIONS = [
    "1. What did you do yesterday?",
    "2. What are you working on today?",
    "3. Any blockers?"
]

def send_standup():
    db = SessionLocal()
    users = db.query(User).all()
    for user in users:
        for q in QUESTIONS:
            client.chat_postMessage(channel=user.id, text=q)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_standup, "cron", hour=10)
    scheduler.start()

