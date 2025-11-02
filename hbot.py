from .. import loader, utils
import asyncio
from telethon import events

@loader.tds
class HBotMod(loader.Module):
    strings = {"name": "HBot"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.config = loader.ModuleConfig("hahrobot", "@hahrobot", lambda: "@hahrobot")
        if not self.db.get(__name__, "enabled", None):
            self.db.set(__name__, "enabled", False)
        if not self.db.get(__name__, "ignored", None):
            self.db.set(__name__, "ignored", [])

    async def hbotcmd(self, m):
        args = utils.get_args_raw(m)
        if not args:
            await m.edit(".hbot on/off | .hbot <текст> | .hbot ignore <id>")
            return
        if args.lower() in ["on", "вкл"]:
            self.db.set(__name__, "enabled", True)
            await m.edit("✅ Включен")
            return
        if args.lower() in ["off", "выкл"]:
            self.db.set(__name__, "enabled", False)
            await m.edit("🚫 Выключен")
            return
        if args.lower().startswith("ignore"):
            parts = args.split()
            if len(parts) < 2:
                await m.edit("Укажи ID пользователя")
                return
            uid = int(parts[1])
            ignored = self.db.get(__name__, "ignored", [])
            if uid in ignored:
                ignored.remove(uid)
                await m.edit(f"✅ Убрано игнорирование {uid}")
            else:
                ignored.append(uid)
                await m.edit(f"🚫 Добавлен в игнор {uid}")
            self.db.set(__name__, "ignored", ignored)
            return
        bot_username = self.config["BOT_USERNAME"]
        try:
            bot_msg = await self.client.send_message(bot_username, args)
            reply = await self.client.wait_for(events.NewMessage(from_users=bot_username), timeout=20)
            if reply.media:
                file = await reply.download_media()
                await self.client.send_file(m.chat_id, file, caption=reply.text)
            else:
                await m.edit(reply.text or "<пусто>")
        except asyncio.TimeoutError:
            await m.edit("⏳ Нет ответа")
        except Exception as e:
            await m.edit(str(e))

    async def watcher(self, m):
        if not m.is_private or m.out:
            return
        s = await m.get_sender()
        if s.bot:
            return
        if not self.db.get(__name__, "enabled", False):
            return
        if s.id in self.db.get(__name__, "ignored", []):
            return
        bot_username = self.config["BOT_USERNAME"]
        try:
            text = m.text or "<медиа>"
            bot_msg = await self.client.send_message(bot_username, text)
            reply = await self.client.wait_for(events.NewMessage(from_users=bot_username), timeout=15)
            if reply.media:
                file = await reply.download_media()
                await self.client.send_file(s.id, file, caption=reply.text)
            else:
                await self.client.send_message(s.id, reply.text or "<пусто>")
        except asyncio.TimeoutError:
            await self.client.send_message(s.id, "⏳ Бот не ответил.")
        except Exception:
            pass