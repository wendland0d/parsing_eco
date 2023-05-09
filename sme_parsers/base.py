import base64
import hashlib
import hmac
import time

import steam.webauth as wa
import requests

class BaseParser():
    def __init__(self, login: str, password: str, secret: str) -> None:
        self.login = login
        self.password = password
        self.secret_string = secret
        self.session = requests.Session()

    def steam_once_key(self) -> str:
        if '\n' in self.secret_string:
            secret = self.secret_string.replace('\n', '')
        code = ''
        char = '23456789BCDFGHJKMNPQRTVWXY'
        secret = self.secret_string

        hex_time = ('%016x' % (int(time.time()) // 30))
        byte_time = bytes.fromhex(hex_time)

        digest = hmac.new(base64.b32decode(secret), byte_time, hashlib.sha1).digest()
        begin = ord(digest[19:20]) & 0xF
        c_int = int.from_bytes((digest[begin:begin + 4]), "big") & 0x7fffffff

        for r in range(5):
            code += char[int(c_int) % len(char)]
            c_int /= len(char)

        return code
    
    @staticmethod
    def steam_twofa_key(secret_string: str) -> str:
        if '\n' in secret_string:
            secret = secret_string.replace('\n', '')
        code = ''
        char = '23456789BCDFGHJKMNPQRTVWXY'
        secret = secret_string

        hex_time = ('%016x' % (int(time.time()) // 30))
        byte_time = bytes.fromhex(hex_time)

        digest = hmac.new(base64.b32decode(secret), byte_time, hashlib.sha1).digest()
        begin = ord(digest[19:20]) & 0xF
        c_int = int.from_bytes((digest[begin:begin + 4]), "big") & 0x7fffffff

        for r in range(5):
            code += char[int(c_int) % len(char)]
            c_int /= len(char)

        return code
    
    def steam_login(self) -> requests.Session:
        user = wa.WebAuth(self.login)
        try:
            self.session = user.login(password=self.password, twofactor_code=self.steam_once_key())

        except wa.EmailCodeRequired as err:
            print(err)
            email_code = input(f'EMail code: ')
            self.session = user.login(email_code=email_code)
        except wa.TwoFactorCodeRequired as err:
            print(err)
            two_fa = self.steam_once_key()
            self.session = user.login(twofactor_code=two_fa)
        except Exception as err:
            print(err)
            time.sleep(5)
            self.session = self.steam_login()
    
