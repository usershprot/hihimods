from .. import loader, utils
import asyncio
import aiohttp
import re
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from telethon.tl.types import Message, DocumentAttributeFilename  # Добавлен импорт
import time

@loader.tds
class DoxxMod(loader.Module):
    """Модуль для пробива через 19 ботов с созданием PDF-досье"""
    strings = {"name": "DoxxMod"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        # Список ботов
        self.bots = [
            "t.me/InfinitySearcch_bot",
            "t.me/FastSearch66_bot",
            "t.me/fasthlr_bot",
            "t.me/mnp_bot",
            "t.me/DepSearrchbot",
            "t.me/ipscore_bot",
            "t.me/faribybot",
            "t.me/Numbersearch2025bot",
            "t.me/chaosro_bot",
            "t.me/kdskodko23_bot",
            "t.me/originalpeople_bot",
            "t.me/osintkit_search_bot",
            "t.me/TlgGeoEarthBot",
            "t.me/doxinghawk_bot",
            "t.me/egrul_bot",
            "t.me/WhoisDomBot",
            "t.me/metawaverobot",
            "t.me/kejwasdflkjsdreybot",
            "t.me/Userboxfree1234bot",
        ]
        # Регулярные выражения для проверки ввода
        self.PHONE_REGEX = r"^\+?\d{10,12}$"
        self.SNILS_REGEX = r"^\d{3}-\d{3}-\d{3}\s\d{2}$"
        self.NAME_REGEX = r"^[a-zA-Zа-яА-Я\s]+$"

    # Функция для создания PDF
    def create_pdf(self, results: dict, query: str) -> BytesIO:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Досье по запросу: {query}")
        c.drawString(100, 730, "-" * 50)
        y = 700
        for bot, data in results.items():
            c.drawString(100, y, f"Источник: {bot}")
            y -= 20
            for key, value in data.items():
                c.drawString(120, y, f"{key}: {value}")
                y -= 20
            y -= 10
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    # Функция для отправки запроса боту через Telegram
    async def query_bot(self, bot: str, query: str) -> dict:
        try:
            # Отправляем сообщение боту
            await self.client.send_message(bot, query)
            # Ждём ответа (максимум 30 секунд)
            start_time = time.time()
            while time.time() - start_time < 30:
                messages = await self.client.get_messages(bot, limit=1)
                if messages and messages[0].date.timestamp() > start_time:
                    response = messages[0].text
                    data = self.parse_response(response)
                    return {bot: data}
                await asyncio.sleep(1)
            return {bot: {"error": "Бот не ответил вовремя"}}
        except Exception as e:
            return {bot: {"error": f"Ошибка: {str(e)}"}}

    # Функция для парсинга ответа бота (заглушка, адаптируй под реальные ответы)
    def parse_response(self, response: str) -> dict:
        data = {}
        lines = response.split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()
        return data if data else {"error": "Нет данных"}

    # Функция для сортировки и объединения результатов
    def sort_results(self, results: list) -> dict:
        sorted_data = {}
        seen = set()
        for result in results:
            for bot, data in result.items():
                if "error" not in data:
                    key = (data.get("Имя"), data.get("Телефон"))
                    if key not in seen:
                        seen.add(key)
                        sorted_data[bot] = {
                            "Имя": data.get("Имя", "Неизвестно"),
                            "Телефон": data.get("Телефон", "Неизвестно"),
                            "СНИЛС": data.get("СНИЛС", "Неизвестно"),
                            "Адрес": data.get("Адрес", "Неизвестно"),
                            "Доп. инфо": data.get("Доп. инфо", "Неизвестно")
                        }
                else:
                    sorted_data[bot] = {"error": data["error"]}
        return sorted_data

    # Команда .doxx
    @loader.command()
    async def doxx(self, message: Message):
        """Пробив данных через 19 ботов с созданием PDF-досье. Использование: .doxx <данные>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "Укажи данные для пробива (телефон, СНИЛС или имя).")
            return

        query = args.strip()
        # Нормализация телефона
        if query.startswith('7') or query.startswith('8'):
            query = f"+7{query[1:]}"

        # Проверка формата
        query_type = "Неизвестно"
        if re.match(self.PHONE_REGEX, query):
            query_type = "Телефон"
        elif re.match(self.SNILS_REGEX, query):
            query_type = "СНИЛС"
        elif re.match(self.NAME_REGEX, query):
            query_type = "Имя"
        else:
            await utils.answer(message, "Неверный формат. Отправь телефон (+79991234567), СНИЛС (123-456-789 01) или имя (Иван Иванов).")
            return

        await utils.answer(message, f"Запрашиваю данные по {query_type}: {query}...")

        # Отправляем запросы всем ботам параллельно
        tasks = [self.query_bot(bot, query) for bot in self.bots]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Сортируем результаты
        sorted_results = self.sort_results(results)

        # Создаём PDF
        pdf_buffer = self.create_pdf(sorted_results, query)
        
        # Отправляем PDF через Telethon
        await self.client.send_file(
            message.peer_id,
            file=pdf_buffer,
            caption=f"Досье по {query_type}: {query}",
            attributes=[DocumentAttributeFilename(f"doxx_{query.replace(' ', '_')}.pdf")]  # Исправлено здесь
        )

        # Отправляем текстовый результат
        text_response = f"Досье по {query_type}: {query}\n" + "-" * 50 + "\n"
        for bot, data in sorted_results.items():
            text_response += f"\nИсточник: {bot}\n"
            if "error" in data:
                text_response += f"Ошибка: {data['error']}\n"
            else:
                for key, value in data.items():
                    text_response += f"{key}: {value}\n"
        await utils.answer(message, text_response)