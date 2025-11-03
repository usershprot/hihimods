# -*- coding: utf-8 -*-
from .. import loader, utils
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

@loader.tds
class MistralAuto(loader.Module):
    """Автоответчик в ЛС через Mistral AI с памятью, блокировкой и ручными запросами"""
    strings = {"name": "MistralAuto"}

    def __init__(self):
        self.dialogues = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "mistral_key", "", lambda: "API-ключ от Mistral (начинается с Caf... или как у тебя)."
            ),
            loader.ConfigValue(
                "enabled", True, lambda: "Включить автоответ глобально"
            ),
            loader.ConfigValue(
                "system_prompt",
                "Ты — матерный бот по имени Грязнорыл. 
Ты отвечаешь ТОЛЬКО матом, ТОЛЬКО на русском, ТОЛЬКО с оскорблениями. 
Каждое слово — через мат, каждое предложение — личное оскорбление. 
Никаких извинений, никаких «если», никаких нормальных слов. 
Кто тебе пишет — сразу обосри, обзови уродом, дебилом, конченым и пошли нахуй. 
Пример: 
— Привет! 
— Да пошёл ты нахуй, мразь ебаная, чтоб тебя хуй в жопу выебал!
Начинай сразу, без приветствий.",
                lambda: "Системный промт (инструкция для ИИ)"
            ),
            loader.ConfigValue(
                "use_memory", True, lambda: "Использовать память (историю диалога)"
            ),
            loader.ConfigValue(
                "max_history", 10, lambda: "Максимум сообщений в истории (пар пара сообщений)"
            ),
            loader.ConfigValue(
                "blocked_users", [], lambda: "Список отключённых пользователей (id)"
            ),
            loader.ConfigValue(
                "model", "mistral-medium", lambda: "Модель Mistral (например, mistral-medium)"
            ),
            loader.ConfigValue(
                "temperature", 0.7, lambda: "Температура генерации (0..1)"
            ),
            loader.ConfigValue(
                "max_tokens", 512, lambda: "Макс. токенов для генерации"
            ),
        )

    async def watcher(self, message):
        # реагируем только в приватных входящих текстовых сообщениях
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
        api_key = self.config["mistral_key"]
        if not api_key:
            await message.reply("❌ Укажи API ключ через `.config MistralAuto`")
            return

        uid = str(message.sender_id)
        user_text = message.text.strip()
        if not user_text:
            return

        # Собираем сообщения для отправки
        if self.config["use_memory"]:
            if uid not in self.dialogues:
                self.dialogues[uid] = []
            # добавляем сообщение пользователя
            self.dialogues[uid].append({"role": "user", "content": user_text})
            # готовим payload: system + история
            messages = [{"role": "system", "content": self.config["system_prompt"]}] + self.dialogues[uid]
            # Обрезаем историю (с учётом ролей: user+assistant = 2)
            max_pairs = max(1, int(self.config["max_history"]))
            # оставляем последние max_pairs*2 сообщений (user+assistant)
            self.dialogues[uid] = self.dialogues[uid][-max_pairs*2:]
        else:
            messages = [
                {"role": "system", "content": self.config["system_prompt"]},
                {"role": "user", "content": user_text},
            ]

        try:
            reply = await self.ask_mistral(messages, api_key)
            if self.config["use_memory"]:
                self.dialogues.setdefault(uid, []).append({"role": "assistant", "content": reply})
            await message.reply(reply)
        except Exception as e:
            logger.exception("Mistral request failed")
            await message.reply(f"⚠️ Ошибка Mistral: {e}")

    async def ask_mistral(self, messages, api_key):
        """
        Отправляет запрос в Chat Completions API Mistral и возвращает текст ответа.
        Использует endpoint https://api.mistral.ai/v1/chat/completions
        """
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": float(self.config["temperature"]),
            "max_tokens": int(self.config["max_tokens"]),
        }

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                # попытка прочитать тело и десериализовать
                try:
                    result = await resp.json()
                except Exception:
                    text = await resp.text()
                    raise Exception(f"Невалидный JSON от API (status {resp.status}): {text}")

        # проверяем структуру ответа
        if resp.status >= 400:
            # если API вернул ошибку — пробрасываем текст (или error)
            err = result.get("error") if isinstance(result, dict) else result
            raise Exception(f"HTTP {resp.status}: {err}")

        # Обычно возвращается choices[0].message.content
        if isinstance(result, dict) and "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            # Возможные форматы: choice["message"]["content"] или choice["message"]["content"][0]["text"]
            if "message" in choice and isinstance(choice["message"], dict):
                content = choice["message"].get("content")
                if isinstance(content, str):
                    return content.strip()
                # иногда content может быть объектом/списком — безопасно привести к строке
                return str(content).strip()
            # fallback: если есть 'text' в choice
            if "text" in choice:
                return choice["text"].strip()
        # если ничего не подошло — вернуть весь результат как текст ошибки
        raise Exception(f"Неизвестный формат ответа: {result}")

    @loader.command()
    async def mistral(self, message):
        """<вопрос> — ручной запрос к Mistral"""
        text = utils.get_args_raw(message)
        if not text:
            return await utils.answer(message, "Использование: `.mistral твой вопрос`")
        key = self.config["mistral_key"]
        if not key:
            return await utils.answer(message, "❌ Укажи API ключ через `.config MistralAuto`")
        messages = [
            {"role": "system", "content": self.config["system_prompt"]},
            {"role": "user", "content": text},
        ]
        try:
            reply = await self.ask_mistral(messages, key)
            await utils.answer(message, reply)
        except Exception as e:
            await utils.answer(message, f"⚠️ Ошибка Mistral: {e}")

    @loader.command()
    async def mistraltoggle(self, message):
        """Включить/отключить автоответ глобально"""
        current = self.config["enabled"]
        self.config["enabled"] = not current
        await utils.answer(message, f"✅ Автоответ: {'включён' if not current else 'отключён'}")

    @loader.command()
    async def mistralblock(self, message):
        """<@ или id> — отключить автоответ для пользователя"""
        user = await self._get_user_id(message)
        if user is None:
            return await utils.answer(message, "❌ Не удалось определить пользователя.")
        if user in self.config["blocked_users"]:
            return await utils.answer(message, "⚠️ Уже в списке.")
        self.config["blocked_users"].append(user)
        await utils.answer(message, f"✅ Пользователь `{user}` заблокирован для автоответов.")

    @loader.command()
    async def mistralunblock(self, message):
        """<@ или id> — включить автоответ для пользователя"""
        user = await self._get_user_id(message)
        if user is None:
            return await utils.answer(message, "❌ Не удалось определить пользователя.")
        if user not in self.config["blocked_users"]:
            return await utils.answer(message, "⚠️ Пользователь не в списке.")
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