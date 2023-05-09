from aiogram import types
from aiogram.filters.command import Command
from sqlalchemy.orm import Session
import asyncio

from bot_setup import dp, engine
from models import *





@dp.message(Command('start'))
async def start(message: types.Message):
    with Session(bind=engine) as db:
        tg_id = db.query(User).filter(User.tg_id == message.from_user.id).one_or_none()
        if tg_id:
            await message.answer('You are already exists! Just wait! P.S. Vse chto ya sdelal - libo raboet libo rabotaet no ne tak kak ti ozhidaesh. by DanyaTHEdeveloper')
        else:
            new_user = User(tg_id=message.from_user.id, tg_username=message.from_user.username)
            db.add(new_user)
            db.commit()
            await message.answer('Hi, within time you will get push-ups with legit items "STEAM-BUFF or BUFF-STEAM. See you later!"')

            
