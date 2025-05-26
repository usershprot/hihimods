# meta developer: @usershprot
# scope: hikka_only

from telethon.tl.functions.messages import CreateChatRequest, GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import asyncio
import subprocess
from .. import loader, utils


@loader.tds
class KeepShellAlive(loader.Module):
    """Поддерживает Google Cloud Shell активным, отправляя терминальную команду в приватный чат"""

    strings = {
        "name": "KeepShellAlive",
        "configuring": "Настройка завершена. Каждые {time} сек будет выполняться: {cmd}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "interval",
                900,
                "Интервал между запусками (в секундах)",
                validator=loader.validators.Integer(minimum=30),
            ),
            loader.ConfigValue(
                "command",
                "hostname",
                "Команда для выполнения в терминале",
            ),
        )

    async def client_ready(self, client, db):
        self.client = client
        self.chat_title = "CloudKeepAliveLog"
        self.chat_id = await self._ensure_chat_exists()
        self._task = asyncio.create_task(self._keep_alive())

    async def _keep_alive(self):
        while True:
            cmd = self.config["command"]
            output = subprocess.getoutput(cmd)
            await self.client.send_message(self.chat_id, f"$ {cmd}\n`{output}`")
            await asyncio.sleep(self.config["interval"])

    async def _ensure_chat_exists(self):
        dialogs = await self.client(GetDialogsRequest(
            offset_date=None, offset_id=0,
            offset_peer=InputPeerEmpty(), limit=100, hash=0
        ))
        for dialog in dialogs.chats:
            if dialog.title == self.chat_title:
                return dialog.id
        result = await self.client(CreateChatRequest(
            users=[(await self.client.get_me()).id],
            title=self.chat_title
        ))
        return result.chats[0].id

    async def keepshellcfgcmd(self, message):
        """Настроить команду и интервал"""
        await self.inline.form(
            message=message,
            title="Настройка KeepShellAlive",
            fields=self.config.fields,
            on_success=lambda values: self._on_config_success(message),
        )

    async def _on_config_success(self, message):
        await utils.answer(
            message,
            self.strings("configuring").format(
                time=self.config["interval"],
                cmd=self.config["command"],
            ),
        )