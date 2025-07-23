import time
import operator
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InputMediaPhoto, ForceReply

import buttons
import config
import keyboards
from custom_filters import button_filter, inline_button_filter, reply_text_filter
from weather import get_current_weather, get_forecast
from random_cat import get_random_cat
from database import Database


class CustomClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = Database()

    def stop(self, *args, **kwargs):
        self.database.close()
        return super().stop(*args, **kwargs)


bot = CustomClient(
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    name="my_cool_bot",
)


@bot.on_message(filters.command("time") | button_filter(buttons.time_button))
async def time_command(client: CustomClient, message: Message):
    now = datetime.now().strftime("%H:%M:%S (%d.%m.%Y)")
    await message.reply(f"🕒 Текущее время: {now}")


@bot.on_message(filters.command("calc"))
async def calc_command(client: CustomClient, message: Message):
    ops = {
        "+": operator.add, "-": operator.sub,
        "*": operator.mul, "/": operator.truediv,
    }

    if len(message.command) != 4:
        await message.reply(
            "Неверное количество аргументов.\n"
            "Пример: `/calc 4 + 2`\n"
            "Операторы: +, -, *, /",
            parse_mode="Markdown"
        )
        return

    _, left, op_symbol, right = message.command
    op = ops.get(op_symbol)
    if op is None:
        await message.reply("Неизвестный оператор")
        return

    try:
        left, right = float(left), float(right)
        result = op(left, right)
    except ZeroDivisionError:
        await message.reply("Ошибка: деление на 0 невозможно")
        return
    except ValueError:
        await message.reply("Аргументы должны быть числами")
        return

    await message.reply(f"Результат: {result}")


@bot.on_message(filters.command("help") | button_filter(buttons.help_button))
async def help_command(client: CustomClient, message: Message):
    commands = await bot.get_bot_commands()
    text_commands = "\n".join(f"/{cmd.command} - {cmd.description}" for cmd in commands)
    await message.reply(f"📋 Список доступных команд:\n{text_commands}")


@bot.on_message(filters.command("start") | button_filter(buttons.back_button))
async def start_command(client: CustomClient, message: Message):
    user = client.database.get_user(message.from_user.id)
    if user is None:
        client.database.create_user(message.from_user.id)

    await message.reply(
        "Привет! Я бот, который умеет считать, показывать погоду, время и котиков 🐱.\n"
        f"Нажми на кнопку {buttons.help_button.text}, чтобы увидеть список команд.",
        reply_markup=keyboards.main_keyboard
    )


@bot.on_message(filters.command("settings") | button_filter(buttons.settings_button))
async def settings_command(client: CustomClient, message: Message):
    await message.reply("⚙️ Настройки", reply_markup=keyboards.settings_keyboard)


@bot.on_message(filters.command("weather") | button_filter(buttons.weather_button))
async def weather_command(client: CustomClient, message: Message):
    if message.command and len(message.command) > 1:
        city = message.command[1]
    else:
        user = client.database.get_user(message.from_user.id)
        city = user.city if user and user.city else "Москва"

    weather = get_current_weather(city)
    await message.reply(weather, reply_markup=keyboards.weather_inline_keyboard)


@bot.on_callback_query(filters=inline_button_filter(buttons.weather_current_inline_button))
async def weather_current_inline(client: CustomClient, query: CallbackQuery):
    user = client.database.get_user(query.from_user.id)
    city = user.city if user and user.city else "Москва"

    weather = get_current_weather(city)
    if weather != query.message.text:
        await query.message.edit_text(weather, reply_markup=keyboards.weather_inline_keyboard)


@bot.on_callback_query(filters=inline_button_filter(buttons.weather_forecast_inline_button))
async def weather_forecast_inline(client: CustomClient, query: CallbackQuery):
    user = client.database.get_user(query.from_user.id)
    city = user.city if user and user.city else "Москва"

    forecast = get_forecast(city)
    if forecast != query.message.text:
        await query.message.edit_text(forecast, reply_markup=keyboards.weather_inline_keyboard)


change_city_text = "Меняем город!\n\nНапиши в ответ название своего города, и я его запомню!"
@bot.on_message(filters.command("change_city") | button_filter(buttons.change_city_button))
async def change_city_command(client: CustomClient, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=change_city_text,
        reply_markup=ForceReply(selective=True),
    )


@bot.on_message(filters.reply & reply_text_filter(change_city_text))
async def change_city_reply(client: CustomClient, message: Message):
    city = message.text.strip()
    client.database.set_city(message.from_user.id, city)
    await message.reply("✅ Город успешно изменён!", reply_markup=keyboards.main_keyboard)


@bot.on_message(filters.command("cats") | button_filter(buttons.cats_button))
async def cats_command(client: CustomClient, message: Message):
    cat_url = get_random_cat()
    await client.send_photo(
        chat_id=message.chat.id,
        photo=cat_url,
        reply_markup=keyboards.cats_inline_keyboard,
    )


@bot.on_callback_query(filters=inline_button_filter(buttons.cats_random_inline_button))
async def cats_random_inline(client: CustomClient, query: CallbackQuery):
    cat_url = get_random_cat()
    await query.message.edit_media(
        media=InputMediaPhoto(cat_url),
        reply_markup=keyboards.cats_inline_keyboard,
    )


@bot.on_message(filters.command("info"))
async def info_command(client: CustomClient, message: Message):
    users_count = client.database.get_users_count()
    await message.reply(f"👥 Всего пользователей: {users_count}", reply_markup=keyboards.main_keyboard)


@bot.on_message()
async def unknown_message(client: CustomClient, message: Message):
    await message.reply("❌ Неизвестная команда. Введите /help для получения списка команд.")


bot.run()
