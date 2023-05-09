import time

from telegram.bot_setup import tg_bot, engine
from sme_parsers.models import Item, User
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_

async def send_message(chat, item, price, profit, link):
    text = f'BUFF-STEAM\n{item}\nProfit - {profit}%\nBuff Price - {price}\nLink - {link}'
    await tg_bot.send_message(chat_id=chat, text=text)


while True:
    print(
        'НАчали'
    )
    with Session(bind=engine) as db:
        user_list = db.query(User).all()
        buff_items = db.query(Item).filter(Item.parser_name == 'buff').all()
        for buff_item in buff_items:
            print(f'{buff_item.hash_name}')
            same_steam_item = db.query(Item).filter(and_(Item.parser_name == 'steam', Item.hash_name == buff_item.hash_name)).one_or_none()
            if not same_steam_item:
                continue
                print(f'Предмет {buff_item.hash_name} не подходит.')
            elif buff_item.price*0.145 < 5:
                continue
                print(f'Предмет {buff_item.hash_name} не подходит. Профит равен {(same_steam_item.price*0.87 - buff_item.price*0.145) / buff_item.price*0.145 * 100}')
            else:
                if (same_steam_item.price*0.87 - buff_item.price*0.145) / buff_item.price*0.145 * 100 > 15:
                    for user in user_list:
                        profit = (same_steam_item.price*0.87 - buff_item.price*0.145) / buff_item.price*0.145 * 100
                        asyncio.run(send_message(chat=user.tg_id, item=buff_item.hash_name, price=buff_item.price*0.145, link=buff_item.link, profit=profit))
                        time.sleep(5)
        time.sleep(300)
