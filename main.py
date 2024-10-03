# Импортируем необходимые модули
import os  # Для работы с переменными окружения
from aiogram import Bot, Dispatcher, types  # Основные классы для работы с ботом
from aiogram.filters import Command  # Фильтр для обработки команды /start
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup  # Типы сообщений и кнопок
from dotenv import load_dotenv  # Для загрузки переменных из .env файла

# Загружаем токен из файла .env
load_dotenv()  # Функция загружает переменные окружения из файла .env
API_TOKEN = os.getenv("API_TOKEN")  # Получаем токен бота из переменной окружения
 
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)  # Создаем объект бота
dp = Dispatcher()  # Создаем объект диспетчера для управления обработчиками

# Обработчик команды /start
@dp.message(Command("start"))  # Этот декоратор указывает, что функция будет вызвана при команде /start
async def start_command_handler(message: Message):
    # Создаем разметку для inline-кнопок
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Кнопка 1", callback_data="button1"),
            InlineKeyboardButton(text="Кнопка 2", callback_data="button2")
        ]
    ])

    await message.answer("Выберите опцию:", reply_markup=inline_kb)

# Обработчик нажатий на inline-кнопки
@dp.callback_query()  # Этот декоратор обрабатывает все нажатия на inline-кнопки
async def inline_button_handler(callback_query: types.CallbackQuery) -> None:
    """
    Обрабатывает нажатия на inline-кнопки.
    """
    # Проверяем, на какую кнопку нажал пользователь
    if callback_query.data == "button1":
        await callback_query.message.answer("Вы нажали на Кнопку 1")
    elif callback_query.data == "button2":
        await callback_query.message.answer("Вы нажали на Кнопку 2")

    # Уведомляем Telegram, что запрос был обработан
    await callback_query.answer()

# Основная функция для запуска бота
async def main():
    """
    Запускает бота.
    """
    # Запускаем диспетчер в режиме поллинга (прослушивания сообщений)
    await dp.start_polling(bot)

# Если этот файл запускается как основной, стартуем бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
