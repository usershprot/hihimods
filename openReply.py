# -*- coding: utf-8 -*-
from .. import loader, utils
import logging
from openai import OpenAI
import asyncio

logger = logging.getLogger(__name__)

@loader.tds
class OpenRouterAuto(loader.Module):
    """Автоответчик в ЛС через OpenRouter (через библиотеку openai) с памятью"""
    strings = {"name": "OpenRouterAuto"}

    def __init__(self):
        self.dialogues = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "openrouter_key", "", lambda: "API-ключ OpenRouter (начинается с sk-or-v1-...)"
            ),
            loader.ConfigValue(
                "enabled", True, lambda: "Включить автоответчик"
            ),
            loader.ConfigValue(
                "system_prompt",
                "Ты — девушка-бот по имени Алиса. Отвечай дружелюбно, эмоционально и с юмором. Пиши на русском.",
                lambda: "Системный промт (инструкция для ИИ)"
            ),
            loader.ConfigValue(
                "use_memory", True, lambda: "Использовать память диалога"
            ),
            loader.ConfigValue(
                "max_history", 10, lambda: "Количество последних сообщений в памяти"
            ),
            loader.ConfigValue(
                "model", "minimax/minimax-m2:free", lambda: "Модель OpenRouter"
            ),
            loader.ConfigValue(
                "temperature", 0.7, lambda: "Температура генерации (0..1)"
            ),
            loader.ConfigValue(
                "max_tokens", 512, lambda: "Максимум токенов для ответа"
            ),
            loader.ConfigValue(
                "blocked_users", [], lambda: "ID пользователей без автоответов"
            ),
        )

    def get_client(self):
        """Создаёт клиент OpenAI с настройками OpenRouter"""
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.config["openrouter_key"],
            default_headers={
                "HTTP-Referer": "https://t.me/yourbot",  # укажи свой Telegram-юзернейм или проект
                "X-Title": "TelegramUserBot",
            },
        )

    async def watcher(self, message):
        if not self.config["enabled"]:
            return
        if not getattr(message, "is_private", False) or getattr(message, "out", False) or not getattr(message, "text", None):
            return

        try:
            sender = await message.get_sender()
            if getattr(sender, "bot", False):
                return
        except Exception:
            return

        if message.sender_id in self.config["blocked_users"]:
            return

        await self.handle_ai(message)

    async def handle_ai(self, message):
        api_key = self.config["openrouter_key"]
        if not api_key:
            return await message.reply("❌ Укажи API ключ через `.config OpenRouterAuto`")

        uid = str(message.sender_id)
        user_text = message.text.strip()
        if not user_text:
            return

        # История диалога
        if self.config["use_memory"]:
            self.dialogues.setdefault(uid, [])
            self.dialogues[uid].append({"role": "user", "content": user_text})
            messages = [{"role": "system", "content": self.config["system_prompt"]}] + self.dialogues[uid]
            self.dialogues[uid] = self.dialogues[uid][-self.config["max_history"]*2:]
        else:
            messages = [
                {"role": "system", "content": self.config["system_prompt"]},
                {"role": "user", "content": user_text},
            ]

        try:
            reply = await self.ask_openrouter(messages)
            if self.config["use_memory"]:
                self.dialogues[uid].append({"role": "assistant", "content": reply})
            await message.reply(reply)
        except Exception as e:
            logger.exception("OpenRouter error")
            await message.reply(f"⚠️ Ошибка OpenRouter: {e}")

    async def ask_openrouter(self, messages):
        """Отправка запроса через OpenAI SDK (OpenRouter backend)"""
        client = self.get_client()
        loop = asyncio.get_event_loop()

        def sync_call():
            resp = client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=float(self.config["temperature"]),
                max_tokens=int(self.config["max_tokens"]),
            )
            return resp.choices[0].message.content.strip()

        return await loop.run_in_executor(None, sync_call)

    # --- Команды ---
    @loader.command()
    async def orask(self, message):
        """<текст> — ручной запрос к OpenRouter"""
        text = utils.get_args_raw(message)
        if not text:
            return await utils.answer(message, "Использование: `.orask твой вопрос`")
        key = self.config["openrouter_key"]
        if not key:
            return await utils.answer(message, "❌ Укажи API ключ через `.config OpenRouterAuto`")
        messages = [
            {"role": "system", "content": self.config["system_prompt"]},
            {"role": "user", "content": text},
        ]
        try:
            reply = await self.ask_openrouter(messages)
            await utils.answer(message, reply)
        except Exception as e:
            await utils.answer(message, f"⚠️ Ошибка OpenRouter: {e}")

    @loader.command()
    async def ortoggle(self, message):
        """Включить/отключить автоответчик"""
        current = self.config["enabled"]
        self.config["enabled"] = not current
        await utils.answer(message, f"✅ Автоответ: {'включён' if not current else 'отключён'}")

    @loader.command()
    async def orblock(self, message):
        """<@ или id> — заблокировать пользователя"""
        user = await self._get_user_id(message)
        if not user:
            return await utils.answer(message, "❌ Не удалось определить пользователя.")
        if user in self.config["blocked_users"]:
            return await utils.answer(message, "⚠️ Уже заблокирован.")
        self.config["blocked_users"].append(user)
        await utils.answer(message, f"🚫 Пользователь `{user}` заблокирован.")

    @loader.command()
    async def orunblock(self, message):
        """<@ или id> — разблокировать пользователя"""
        user = await self._get_user_id(message)
        if not user:
            return await utils.answer(message, "❌ Не удалось определить пользователя.")
        if user not in self.config["blocked_users"]:
            return await utils.answer(message, "⚠️ Не в списке.")
        self.config["blocked_users"].remove(user)
        await utils.answer(message, f"✅ Пользователь `{user}` разблокирован.")

    async def _get_user_id(self, message):
        args = utils.get_args_raw(message)
        if not args and getattr(message, "reply_to", None):
            reply = await message.get_reply_message()
            return getattr(reply, "sender_id", None)
        if args and args.isdigit():
            return int(args)
        try:
            entity = await message.client.get_entity(args)
            return entity.id
        except Exception:
            return None