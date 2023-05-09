from aiogram import types, Bot, Dispatcher
from sqlalchemy import create_engine
import os

from .models import Base

tg_bot = Bot(token=os.getenv('BOT_DEV_TOKEN'))
dp = Dispatcher()

engine = create_engine(f"postgresql+psycopg2://admin:admin@{os.getenv('DB_URL')}/{os.getenv('DB_NAME')}", pool_pre_ping=True)
engine.dispose(close=False)
Base.metadata.create_all(bind=engine)