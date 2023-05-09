import datetime
import time

import requests
from sme_parsers.models import Item, engine
from sqlalchemy.orm import Session
from sqlalchemy import and_
import urllib.parse

while True:
    url = "http://80.85.142.188:8000/get"
    send_data = {
          "type": "sell",
          "login": "steam",
          "password": "A@XfpG}VjFCN@sR",
          }
    response = requests.post(url, json=send_data).json()

    with Session(bind=engine) as db:
        for item in response['data']:
            db_item = db.query(Item).filter(and_(Item.hash_name == item['market_hash_name'], Item.parser_name == 'steam')).one_or_none()
            if db_item:
                db_item.price = item['price']
                db_item.time = datetime.datetime.now()
                db.commit()
            else:
                db_add = Item(
                    hash_name=item['market_hash_name'],
                    price=item['price'],
                    analytic=item['price'],
                    count=1,
                    time=datetime.datetime.now(),
                    link=f'https://steamcommunity.com/market/listings/730/{urllib.parse.quote_plus(item["market_hash_name"])}',
                    game="csgo",
                    parser_name="steam",
                    tradelock=0
                )
                db.add(db_add)
                db.commit()
    time.sleep(60)