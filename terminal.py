import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils import executor

API_TOKEN = "7718204976:AAGhQNlS9ulnqj_SatBQucQTsABVnOE9Co0"
OWNER_ID = 6450469685  # <-- Твой Telegram user ID

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Простой старт
@dp.message(CommandStart())
async def start(message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("🚫 Доступ запрещён.")
    await message.answer("🖥️ Бот-терминал активен.\nПросто напиши команду.")

# Терминальное выполнение
@dp.message()
async def execute_command(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    cmd = message.text.strip()

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        result = ""
        if stdout:
            result += f"<b>📤 Вывод:</b>\n<code>{stdout.decode().strip()}</code>\n"
        if stderr:
            result += f"<b>⚠️ Ошибка:</b>\n<code>{stderr.decode().strip()}</code>"

        if not result:
            result = "✅ Команда выполнена, но ничего не вывела."

        await message.reply(result[:4096])

    except Exception as e:
        await message.reply(f"❌ Ошибка: <code>{e}</code>")

# Запуск
if __name__ == "__main__":
    import asyncio
    from aiogram import F

    dp.include_router(dp.router)
    asyncio.run(dp.start_polling(bot))