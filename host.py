import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
import time

API_TOKEN = "ВАШ_ТОКЕН_БОТА"

DONATION_MIN_USD = 0.13
MAX_USERS = 4
SESSION_DURATION = 12 * 3600  # 12 часов в секундах

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

# Подключение к SQLite для хранения пользователей и сессий
conn = sqlite3.connect("hikkahostlite.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    api_id TEXT,
    api_hash TEXT,
    session_start INTEGER,
    paid INTEGER DEFAULT 0
)
""")
conn.commit()

# FSM для пошагового ввода данных
class Form(StatesGroup):
    waiting_api_id = State()
    waiting_api_hash = State()
    waiting_auth_choice = State()
    waiting_donation = State()
    waiting_code = State()

# Вспомогательные функции
def format_blockquote(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"

def is_user_active(user_id: int):
    cursor.execute("SELECT session_start FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return False
    session_start = row[0]
    if session_start + SESSION_DURATION > int(time.time()):
        return True
    else:
        # Сессия закончилась
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return False

def count_active_users():
    now = int(time.time())
    cursor.execute("SELECT COUNT(*) FROM users WHERE session_start + ? > ?", (SESSION_DURATION, now))
    return cursor.fetchone()[0]

async def check_user_allowed(user_id: int) -> bool:
    active = is_user_active(user_id)
    if active:
        return True
    if count_active_users() >= MAX_USERS:
        return False
    return True

async def start_session(user_id: int):
    now = int(time.time())
    cursor.execute("INSERT OR REPLACE INTO users (user_id, session_start, paid) VALUES (?, ?, 1)", (user_id, now))
    conn.commit()

# Хендлеры

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    user_allowed = await check_user_allowed(message.from_user.id)
    if not user_allowed:
        await message.answer(format_blockquote("🚫 Свободных слотов нет! Попробуйте позже."), parse_mode="HTML")
        return
    if is_user_active(message.from_user.id):
        await message.answer(format_blockquote("✅ У вас уже есть активная сессия. Введите только код для повторной авторизации."), parse_mode="HTML")
        await state.set_state(Form.waiting_code)
        return
    await message.answer(format_blockquote("Привет! Введите ваш API ID:"), parse_mode="HTML")
    await state.set_state(Form.waiting_api_id)

@dp.message(Form.waiting_api_id)
async def process_api_id(message: types.Message, state: FSMContext):
    await state.update_data(api_id=message.text.strip())
    await message.answer(format_blockquote("Введите ваш API HASH:"), parse_mode="HTML")
    await state.set_state(Form.waiting_api_hash)

@dp.message(Form.waiting_api_hash)
async def process_api_hash(message: types.Message, state: FSMContext):
    await state.update_data(api_hash=message.text.strip())
    # Кнопки для выбора авторизации
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Авторизоваться по QR", callback_data="auth_qr_yes"),
            InlineKeyboardButton(text="❌ Нет, по коду", callback_data="auth_qr_no")
        ]
    ])
    await message.answer(format_blockquote("Хотите авторизоваться по QR-коду?"), parse_mode="HTML", reply_markup=kb)
    await state.set_state(Form.waiting_auth_choice)

@dp.callback_query(lambda c: c.data in ["auth_qr_yes", "auth_qr_no"])
async def process_auth_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    if callback.data == "auth_qr_yes":
        await callback.message.answer(format_blockquote("Вы выбрали авторизацию по QR. Сейчас отправим QR-код (заглушка)."), parse_mode="HTML")
        # Здесь должна быть логика генерации и отправки QR
        # Пока заглушка:
        await callback.message.answer(format_blockquote("[QR-код для авторизации]"), parse_mode="HTML")
        await start_session(callback.from_user.id)
        await state.clear()
    else:
        # Отправляем символ 'n' на сервер (заглушка)
        await callback.message.answer(format_blockquote("Вы выбрали авторизацию по коду. Отправляем 'n' на сервер..."), parse_mode="HTML")
        # Здесь логика отправки 'n' через SSH
        await start_session(callback.from_user.id)
        await state.clear()

@dp.message(Form.waiting_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    # Заглушка обработки кода
    await message.answer(format_blockquote(f"Получен код: {code}\nПроверяем..."), parse_mode="HTML")
    # В реале здесь проверка и авторизация
    await start_session(message.from_user.id)
    await state.clear()

# Обработчик доната - заглушка
@dp.message(Command(commands=["donate"]))
async def cmd_donate(message: types.Message):
    await message.answer(format_blockquote(
        "Для использования бота необходимо сделать донат минимум 0.13$.\n"
        "Платёж принимается через CryptoBot.\n"
        "Отправьте платеж и после подтверждения получите доступ."
    ), parse_mode="HTML")

# Запуск бота
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    asyncio.run(dp.start_polling(bot))