# app/db.py
from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./standup.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Installation(Base):
    __tablename__ = "installations"
    id = Column(Integer, autoincrement=True, unique=True)
    team_id = Column(String, primary_key=True, index=True)
    team_name = Column(String)
    bot_user_id = Column(String)
    access_token = Column(String)
    installed_by = Column(String)
    trigger_time = Column(String, default='10:00') # HH:MM
    trigger_days= Column(String, default='Monday,Tuesday,Wednesday,Thursday,Friday') # csv of Monday,Tuesday
    submit_after_mins = Column(Integer, default=120)
    submit_to_channel = Column(String)
    max_team_size = Column(Integer, default=-1)
    valid_till = Column(Integer, default=-1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, unique=True)
    slack_user_id = Column(String, primary_key=True)
    team_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Trigger(Base):
    __tablename__="triggers"
    id = Column(Integer, autoincrement=True, primary_key=True)
    team_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    triggered_by = Column(String)



class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, autoincrement=True, primary_key=True)
    team_id = Column(String)
    user_id = Column(String)
    question = Column(Text)
    answer = Column(Text)
    trigger_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_team_user', 'team_id', 'user_id'),
    )


Base.metadata.create_all(bind=engine)


# Simple DB helpers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_user(user_id, team_id):
    db = next(get_db())
    if not db.query(User).filter(User.id == user_id).first():
        db.add(User(id=user_id, team_id=team_id))
        db.commit()


def save_response(user_id, question, answer):
    db = next(get_db())
    r = Response(id=f"{user_id}_{datetime.utcnow().isoformat()}", user_id=user_id, question=question, answer=answer)
    db.add(r)
    db.commit()

def save_installation(team_id, team_name, bot_user_id, access_token, installed_by):
    db = next(get_db())
    inst = db.query(Installation).filter(Installation.team_id == team_id).first()
    if inst:
        inst.team_name = team_name
        inst.bot_user_id = bot_user_id
        inst.access_token = access_token
        inst.installed_by = installed_by
    else:
        inst = Installation(
            team_id=team_id,
            team_name=team_name,
            bot_user_id=bot_user_id,
            access_token=access_token,
            installed_by=installed_by
        )
        db.add(inst)
    db.commit()


def get_installation(team_id):
    db = next(get_db())
    return db.query(Installation).filter(Installation.team_id == team_id).first()


def update_installation(team_id, **kwargs):
    db = next(get_db())
    installation = db.query(Installation).filter(Installation.team_id == team_id).first()
    if not installation:
        return False

    for key, value in kwargs.items():
        if hasattr(installation, key):
            setattr(installation, key, value)
    
    db.commit()
    return True

