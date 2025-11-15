import os
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError

DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///state.db')
engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    provider = Column(String, index=True)
    token_json = Column(Text)

class ProcessedMessage(Base):
    __tablename__ = 'processed'
    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def store_token(provider, token_json):
    session = SessionLocal()
    obj = session.query(Token).filter(Token.provider == provider).first()
    if obj:
        obj.token_json = token_json
    else:
        obj = Token(provider=provider, token_json=token_json)
        session.add(obj)
    session.commit()
    session.close()

def load_token(provider):
    session = SessionLocal()
    obj = session.query(Token).filter(Token.provider == provider).first()
    session.close()
    return obj.token_json if obj else None

def mark_processed(message_id):
    session = SessionLocal()
    try:
        pm = ProcessedMessage(message_id=message_id)
        session.add(pm)
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()

def is_processed(message_id):
    session = SessionLocal()
    obj = session.query(ProcessedMessage).filter(ProcessedMessage.message_id==message_id).first()
    session.close()
    return bool(obj)
