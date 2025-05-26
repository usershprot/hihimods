# meta developer: @usershprot
# scope: hikka_only

from telethon.tl.functions.messages import CreateChatRequest
from hikkatl.types import Message
from hikka import loader, utils
import asyncio
import subprocess


@loader.tds
class KeepGoogleShellMod(loader.Module):
    """Не даёт засыпать Google Cloud Shell, отправляя команду в терминал"""

    strings = {
        "name": "KeepGoogleShell",
        "started": "✅ Модуль запущен. Интервал: {interval} сек. Команда: {cmd}",
        "stopped": "⛔️ Модуль остановлен.",
        "created": "✅ Создан чат \"{chat_name}\".",
        "already": "✅ Чат уже существует.",
        "config_title": "Настройки KeepShell",
        "config_cmd": "Команда, которая будет отправляться",
        "config_interval": "Интервал между отправками (в секундах)"
    }

    def __init__(self):
        self.running = False
        self.chat_title = "KeepShellChat"

    async def client_ready(self, client, db):
        self.client = client
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "cmd",
                "hostname",
                lambda: self.strings("config_cmd"),
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "interval",
                900,
                lambda: self.strings("config_interval"),
                validator=loader.validators.Integer(minimum=60)
            ),
        )

    async def _get_or_create_chat(self):
        async for dialog in self.client.iter_dialogs():
            if dialog.name == self.chat_title:
                return dialog.id

        result = await self.client(CreateChatRequest(
            users=[(await self.client.get_me()).id],
            title=self.chat_title
        ))
        return result.chats[0].id

    async def keepshellcmd(self, message: Message):
        """Запустить отправку команды в терминал каждые N секунд"""
        if self.running:
            await message.edit(self.strings("stopped"))
            self.running = False
            return

        self.running = True
        interval = self.config["interval"]
        cmd = self.config["cmd"]
        chat_id = await self._get_or_create_chat()

        await message.edit(self.strings("started").format(interval=interval, cmd=cmd))

        while self.running:
            output = subprocess.getoutput(cmd)
            await self.client.send_message(chat_id, f". {output}")
            await asyncio.sleep(interval)

    async def keepshellcfgcmd(self, message: Message):
        """Открыть конфиг для настройки"""
        await self.configure(message)