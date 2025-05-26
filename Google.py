# meta developer: @usershprot
# requires: hikka

from .. import loader, utils
import asyncio
import time

@loader.tds
class KeepShellAlive(loader.Module):
    """Модуль для отправки команды в чат каждые N минут, чтобы не засыпала сессия"""

    strings = {
        "name": "KeepShellAlive",
        "start": "✅ Автосообщения запущены (каждые {time} мин):\n`{cmd}`",
        "stop": "⛔️ Автосообщения остановлены.",
        "configuring": "⚙️ Интервал: {time} мин\nКоманда: `{cmd}`",
        "set_chat": "✅ Рабочий чат установлен. ID: `{}`",
    }

    def __init__(self):
        self._task = None
        self._running = False

    async def client_ready(self, client, db):
        self.client = client
        if self._running:
            self._start_loop()

    async def _send_cmd(self):
        while self._running:
            try:
                chat_id = self.get("chat_id", None)
                if not chat_id:
                    await asyncio.sleep(10)
                    continue
                command = self.config.get("command", "terminal hostname")
                await self.client.send_message(chat_id, command)
            except Exception as e:
                print("[KeepShellAlive] Error:", e)
            await asyncio.sleep(int(self.config.get("interval", 15)) * 60)

    def _start_loop(self):
        if not self._task:
            self._running = True
            self._task = asyncio.create_task(self._send_cmd())

    def _stop_loop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    @loader.command()
    async def keepshell(self, message):
        """Запустить отправку команд"""
        self._start_loop()
        await utils.answer(message, self.strings("start").format(
            time=self.config.get("interval", 15),
            cmd=self.config.get("command", ".terminal hostname")
        ))

    @loader.command()
    async def stopshell(self, message):
        """Остановить отправку команд"""
        self._stop_loop()
        await utils.answer(message, self.strings("stop"))

    @loader.command()
    async def shellchat(self, message):
        """Установить текущий чат как рабочий"""
        cid = utils.get_chat_id(message)
        self.set("chat_id", cid)
        await utils.answer(message, self.strings("set_chat").format(cid))

    @loader.command()
    async def keepshellcfg(self, message):
        """Настроить команду и интервал"""
        await self.config.edit(
            message,
            callback=self._on_config_success,
        )

    async def _on_config_success(self, values, message):
        await utils.answer(
            message,
            self.strings("configuring").format(
                time=self.config["interval"],
                cmd=self.config["command"],
            ),
        )

    async def on_unload(self):
        self._stop_loop()