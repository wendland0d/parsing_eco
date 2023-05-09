import os

from .base import BaseParser

import asyncio
import requests
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict, Optional
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from json.decoder import JSONDecodeError
from datetime import datetime
import requests

class Buff(BaseParser):
    HOME_PAGE = ''
    MARKET_PAGE = ''
    MARKET_API_PAGE = ''
    ITEM_PAGE = 'https://buff.163.com/api/market/goods/bill_order?game=csgo&goods_id='
    ITEM_HISTORY_PAGE = 'https://buff.163.com/api/market/goods/price_history/buff?game=csgo&goods_id='

    def __init__(self, login: str, password: str, secret: str, proxies: List[str]) -> None:
        super().__init__(login, password, secret)
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/20.0 Chrome/106.0.5249.126 Safari/537.36'
        self.proxies = proxies

    def log_in(self):
        login_headers = {
        'user-agent': f'{self.user_agent}',
        'accept': '*/*',
        }
        temp_html = self.session.get('https://steamcommunity.com/openid/login?openid.mode=checkid_setup&openid.ns=http%3A%2F'
                            '%2Fspecs.openid.net%2Fauth%2F2.0&openid.realm=https%3A%2F%2Fbuff.163.com%2F&openid.sreg'
                            '.required=nickname%2Cemail%2Cfullname&openid.assoc_handle=None&openid.return_to=https%3A'
                            '%2F%2Fbuff.163.com%2Faccount%2Flogin%2Fsteam%2Fverification%3Fback_url%3D%252Faccount'
                            '%252Fsteam_bind%252Ffinish&openid.ns.sreg=http%3A%2F%2Fopenid.net%2Fextensions%2Fsreg'
                            '%2F1.1&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select'
                            '&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select',
                            headers=login_headers).content
        soup = BeautifulSoup(temp_html, features='html.parser')
        print(soup)
        openid = {
            'action': (None, soup.find('input', {'id': 'actionInput'})['value']),
            'openid.mode': (None, soup.find('input', {'name': 'openid.mode'})['value']),
            'openidparams': (None, soup.find('input', {'name': 'openidparams'})['value']),
            'nonce': (None, soup.find('input', {'name': 'nonce'})['value'])
        }
        self.session.post('https://steamcommunity.com/openid/login', files=openid, headers=login_headers)
        
    @classmethod
    def max_pages(cls) -> int:
        mp_headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/111.0.0.0 Mobile Safari/537.36',
        'accept': '*/*',
        'host': 'buff.163.com',
        'referer': 'https://buff.163.com/'
        }
        dt = datetime.now()
        count = requests.get(f'https://buff.163.com/api/market/goods?game=csgo&page_num=1&use_suggestion=0&_={datetime.timestamp(dt)}',
                         headers=mp_headers).json()['data']['total_page']
        return count

    def request(self, page: int):
        request_header = {
            'user-agent': f'{self.user_agent}',
            'accept': '*/*',
            'host': 'buff.163.com',
            'referer': 'https://buff.163.com/'
            }
        dt = datetime.now()
        response = self.session.get(
        url=f'https://buff.163.com/api/market/goods?game=csgo&page_num={page}&use_suggestion=0&_={datetime.timestamp(dt)}',
        headers=request_header)
        
        try:
            response = response.json()
        except JSONDecodeError as err:
            print(response.content)
        except Exception as err:
            self.session.proxies.update({'http': 'http://' + self.proxies.pop().replace('\n','')})
            response = self.request(page)
        

        try:
            for item in response["data"]["items"]:
                continue
        except TypeError:
            print(response)
            response = self.request(page)
        except KeyError:
            print(response)
            response = self.request(page)
        except JSONDecodeError as err:
            print(response.content)

        return response


    
    def parse_point(self, item_id):
        request_header = {
            'user-agent': f'{self.user_agent}',
            'accept': '*/*',
            'host': 'buff.163.com',
            'referer': 'https://buff.163.com/'
            }
        url = self.ITEM_PAGE + f'{item_id}&_={datetime.timestamp}' 
        try:
            raw_points = self.session.get(url=url, headers=request_header).json()
        except:
            print(self.session.get(url=url, headers=request_header).content)
            raise Exception('Что-то пошло не так!')
        
        points = [{
                "UniqueID" : raw_points["data"]["items"][0]["goods_id"],
                "Points": [{'Price': float(date["price"]), 'Time': f'{datetime.fromtimestamp(date["buyer_pay_time"])}', "TimeStamp": date["buyer_pay_time"]} for date in raw_points['data']['items']],
                "BuyOffers": [0],
                "SellOffers": [0]
            }]
        
        return points
    
    def parse_history(self, item_id):
        request_header = {
            'user-agent': f'{self.user_agent}',
            'accept': '*/*',
            'host': 'buff.163.com',
            'referer': 'https://buff.163.com/'
            }
        dt = datetime.now()
        url = self.ITEM_HISTORY_PAGE + f'{item_id}' f'&currency=USD&days=30&buff_price_type=2&_={datetime.timestamp(dt)}'
        raw_data = self.session.get(url=url, headers=request_header).json()

        points=[{
            "UniqueID" : f'{item_id}',
            "Points": [{"Price": i[1], "Timestamp": f'{int(i[0]/1000)}'} for i in raw_data["data"]["price_history"]],
            "BuyOffers": [],
            "SellOffers": []
        }]
        return points

    def parse(self, start_page, end_page, sleep_timer = 10, sleep_history = 5) -> Dict[str, dict]:
        data: dict = {}
        for page in range(start_page, end_page):
            response = self.request(page=page)
            for item in response["data"]["items"]:
                if float(item["sell_min_price"]) < 1:
                    continue
                else:
                    if item['has_buff_price_history']:
                        analytic = self.parse_history(item['id'])
                        print(analytic)
                        raw = requests.post(url=os.getenv('ANALYTIC_IP'), json=analytic).json()
                        item['quick_price'] = raw[0]['sellPrice']
                    data.update({f'{item["market_hash_name"]}': [item]})
                    time.sleep(sleep_history)
            time.sleep(sleep_timer)
        return data

    def parse_page(self, page, sleep_history = 5):
        analytic_price = []
        data: dict = {}
        response = self.request(page)
        for item in response["data"]["items"]:
            if float(item["sell_min_price"]) < 1:
                continue
            else:
                if item['has_buff_price_history']:
                    analytic = self.parse_history(item['id'])
                    print(analytic)
                    raw = requests.post(url=os.getenv('ANALYTIC_IP'), json=analytic).json()
                    print(raw)
                    if raw['data'][0]['sellPrice'] != None:
                        analytic_price.append(raw['data'][0]['sellPrice'])
                data.update({f'{item["market_hash_name"]}': [item]})
                time.sleep(sleep_history)
        return data, analytic_price

