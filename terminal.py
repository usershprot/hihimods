import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hcode
import logging

API_TOKEN = "7718204976:AAGhQNlS9ulnqj_SatBQucQTsABVnOE9Co0"
OWNER_ID = 6450469685  # ← твой Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("🚫 Доступ запрещён.")
    await message.answer("🖥️ Терминал-бот активен.\nНапиши команду.")


@dp.message()
async def execute(message: Message):
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

        out = stdout.decode().strip()
        err = stderr.decode().strip()

        result = ""
        if out:
            result += f"<b>📤 Вывод:</b>\n{hcode(out)}\n"
        if err:
            result += f"<b>⚠️ Ошибка:</b>\n{hcode(err)}"
        if not result:
            result = "✅ Команда выполнена, но ничего не вывела."

        await message.answer(result[:4096])

    except Exception as e:
        await message.answer(f"❌ Ошибка: <code>{e}</code>")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())