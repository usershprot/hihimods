# meta developer: @usershprot
# scope: chat

import asyncio
from telethon.tl.types import Message

class SpamXMod:
    def __init__(self):
        self.name = "SpamX"
        self.running = False

    async def spamxcmd(self, message: Message):
        """[кол-во] [задержка] [текст] — начать спам (используй 0 или ∞ для бесконечного)"""
        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            return await message.edit("Использование: .spamx <кол-во> <задержка> <текст>")

        try:
            count_arg = args[1]
            if count_arg in ("∞", "inf", "бесконечно", "0"):
                count = float("inf")
            else:
                count = int(count_arg)

            delay = float(args[2])
            text = args[3]
        except ValueError:
            return await message.edit("Неверные аргументы.")

        self.running = True
        await message.edit(f"Спам запущен: {'∞' if count == float('inf') else count} сообщений с задержкой {delay} сек.")
        
        i = 1
        while self.running and i <= count:
            txt = text.replace("{count}", str(i))
            await message.respond(txt)
            await asyncio.sleep(delay)
            i += 1

        if self.running:
            await message.respond("Спам завершён.")
        else:
            await message.respond("Спам остановлен.")
        self.running = False

    async def stopspamxcmd(self, message: Message):
        """Остановить текущий спам"""
        if self.running:
            self.running = False
            await message.edit("Останавливаю спам...")
        else:
            await message.edit("Спам не активен.")