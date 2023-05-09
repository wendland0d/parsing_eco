import time

from sme_parsers.parser import Buff
from sme_parsers.models import Item, engine

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime


"""with open('buff_accounts.txt', 'r') as f:
    accounts = f.readlines()"""


def create_buff(data: str) -> Buff:
    if '\n' in data:
        data = data.replace('\n', '')
    account, password, secret = data.split(':')
    buff_obj = Buff(login=account, password=password, secret=secret, proxies=[''])
    return buff_obj


def buff_proccessing(buff_obj: Buff, start_page: int, end_page: int, sleeper = 10):
    buff.steam_login()
    buff_obj.log_in()
    for i in range(start_page, end_page):
        print(i)
        data, analytic_price = buff_obj.parse_page(i)
        counter = 1
        for key, item in data.items():
            with Session(bind=engine) as db:
                db_item = db.query(Item).filter(and_(Item.parser_name == 'buff', Item.hash_name == item[0]['market_hash_name'])).one_or_none()
                if db_item:
                    db_item.price = item[0]['quick_price']
                    db_item.analytic = analytic_price[counter-1 if counter > 1 else counter]
                    db_item.time = datetime.now()
                    db.commit()
                else:
                    db_add = Item(
                        hash_name = item[0]['market_hash_name'],
                        price = item[0]['quick_price'],
                        analytic = analytic_price[counter-1 if counter > 1 else counter],
                        count = item[0]['buy_num'],
                        time = datetime.now(),
                        link = f'https://buff.163.com/goods/{item[0]["id"]}/',
                        game = "csgo",
                        parser_name = "buff",
                        tradelock = 0
                    )
                    db.add(db_add)
                    db.commit()
            counter += 1
        time.sleep(10)

if __name__ == '__main__':
    while True:
        account = 'Zaciendishay:es1lKqjOQT6VYJ3c{BX:ITUYDWEA3EWV45VT6XT37GLXIUK3EKQS'
        buff = create_buff(account)
        max_page = Buff.max_pages()
        buff_proccessing(buff, 1, max_page)
