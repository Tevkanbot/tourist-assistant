import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import FSInputFile
from dotenv import load_dotenv

# Загрузка данных из JSON-файла
with open('programs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Путь к директории с медиафайлами
MEDIA_PATH = "media/photos"

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для создания inline-кнопок с передачей callback_data
def create_inline_keyboard(buttons):
    inline_buttons = [[InlineKeyboardButton(text=btn['text'], callback_data=btn['callback_data'])] for btn in buttons]
    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    buttons = [{"text": city, "callback_data": f"city:{city}"} for city in data['cities'].keys()]
    await message.answer(
        data["messages"]["welcome"],
        reply_markup=create_inline_keyboard(buttons)
    )

# Обработчик всех callback запросов
@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    action_data = callback_query.data
    parts = action_data.split(":")

    # Удаляем старое сообщение
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

    # Обработка выбора города
    if parts[0] == "city":
        city = parts[1]
        city_info = data['cities'][city]['description']
        buttons = [
            {"text": "Тур на выходные", "callback_data": f"tour:{city}:weekends_trip:1"},
            {"text": "Тур на неделю", "callback_data": f"tour:{city}:week_trip:1"},
            {"text": "Проживание", "callback_data": f"hotels:{city}"},
            {"text": "Назад", "callback_data": "back"}
        ]
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=city_info,
            reply_markup=create_inline_keyboard(buttons)
        )

    # Обработка показа информации о проживании
    elif parts[0] == "hotels":
        city = parts[1]
        hotels_info = data['cities'][city]['hotels']
        city_in = data['cities'][city]['city_in']
        buttons = [{"text": "Назад", "callback_data": f"city:{city}"}]
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"Проживание в {city_in}:\n{hotels_info}",
            reply_markup=create_inline_keyboard(buttons)
        )
    
    # Обработка выбора тура и перехода по дням
    elif parts[0] == "tour":
        city = parts[1]
        tour_type = parts[2]
        day = parts[3]
        trip_data = data['cities'][city][tour_type]
        
        if day in trip_data:
            trip_day = trip_data[day]
            next_day = int(day) + 1
            buttons = [{"text": "Следующий день", "callback_data": f"tour:{city}:{tour_type}:{next_day}"}] if str(next_day) in trip_data else []
            buttons.append({"text": "Назад", "callback_data": f"city:{city}"})
            
            # Путь к изображению для данного дня с использованием английского названия города
            english_city_name = data['cities'][city]['english_name']
            image_path = f"{MEDIA_PATH}/{english_city_name}/{tour_type}/{day}.jpg"
            
            if os.path.exists(image_path):
                print(f"Файл найден: {image_path}")  # Логирование
                # Используем FSInputFile для загрузки файла с файловой системы
                photo = FSInputFile(image_path)
                await bot.send_photo(
                    chat_id=callback_query.message.chat.id,
                    photo=photo,
                    caption=data["messages"]["tour_day"].format(day=day, day_description=trip_day),
                    reply_markup=create_inline_keyboard(buttons)
                )
            else:
                print(f"Файл не найден: {image_path}")  # Логирование
                # Если фото нет, отправляем просто текст
                await bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=data["messages"]["tour_day"].format(day=day, day_description=trip_day),
                    reply_markup=create_inline_keyboard(buttons)
                )
        else:
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=data["messages"]["last_day"],
                reply_markup=create_inline_keyboard([{"text": "Назад", "callback_data": f"city:{city}"}])
            )

    # Обработка нажатия на "Назад"
    elif parts[0] == "back":
        buttons = [{"text": city, "callback_data": f"city:{city}"} for city in data['cities'].keys()]
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=data["messages"]["welcome"],
            reply_markup=create_inline_keyboard(buttons)
        )

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
