import time
import random
import operator

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InputMediaPhoto

import config
import buttons
import keyboards
from custom_filters import button_filter, inline_button_filter
from weather import get_current_weather, get_forecast
from random_cat import get_random_cat
from database import Database
from pyrogram import Client


class MyBot(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = Database()

    def stop(self, *args, **kwargs):
        self.database.close()
        return super().stop(*args, **kwargs)


bot = MyBot(
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    name="my_cool_bot"
)


@bot.on_message(filters.command("start") | button_filter(buttons.back_button))
async def start_command(client: MyBot, message: Message):
    user = client.database.get_user(message.from_user.id)
    if user is None:
        client.database.create_user(message.from_user.id)

    await message.reply(
        "Привет! Я бот, который умеет считать, показывать время, погоду и котиков!\n"
        f"Нажми на кнопку {buttons.help_button.text} для получения списка команд.",
        reply_markup=keyboards.main_keyboard
    )


@bot.on_message(filters.command("time") | button_filter(buttons.time_button))
async def time_command(client: MyBot, message: Message):
    current_time = time.strftime("%H:%M:%S")
    await message.reply(
        f"Текущее время: {current_time}",
        reply_markup=keyboards.main_keyboard
    )


@bot.on_message(filters.command("calc"))
async def calc_command(client: MyBot, message: Message):
    ops = {
        "+": operator.add, "-": operator.sub,
        "*": operator.mul, "/": operator.truediv,
    }

    if len(message.command) != 4:
        return await message.reply(
            "Неверное количество аргументов\n"
            "Пример: /calc 5 * 7"
        )

    _, left, op_symbol, right = message.command
    op = ops.get(op_symbol)
    try:
        left = float(left)
        right = float(right)
    except ValueError:
        return await message.reply("Аргументы должны быть числами")

    if op is None:
        return await message.reply("Неизвестный оператор")

    result = op(left, right)
    await message.reply(f"Результат: {result}")


@bot.on_message(filters.command("help") | button_filter(buttons.help_button))
async def help_command(client: MyBot, message: Message):
    text_commands = (
        "Список доступных команд:\n\n"
        "/start - Перезапустить бота\n"
        "/time - Узнать текущее время\n"
        "/calc - Калькулятор (пример: /calc 2 + 2)\n"
        "/weather - Погода в вашем городе\n"
        "/setcity - Установить свой город\n"
        "/cats - Получить случайного котика\n"
        "/help - Показать это сообщение\n"
    )
    await message.reply(text_commands, reply_markup=keyboards.main_keyboard)


@bot.on_message(filters.command("weather") | button_filter(buttons.weather_button))
async def weather_command(client: MyBot, message: Message):
    user = client.database.get_user(message.from_user.id)
    city = user.city or "Москва"
    weather = get_current_weather(city)
    await message.reply(
        weather,
        reply_markup=keyboards.weather_inline_keyboard
    )


@bot.on_message(filters.command("setcity"))
async def set_city_command(client: MyBot, message: Message):
    if len(message.command) < 2:
        return await message.reply("Пример: /setcity Санкт-Петербург")
    city = " ".join(message.command[1:])
    client.database.set_city(message.from_user.id, city)
    await message.reply(f"Город успешно установлен: {city}")


@bot.on_callback_query(filters=inline_button_filter(buttons.weather_current_inline_button))
async def weather_current_inline_button_callback(client: MyBot, query: CallbackQuery):
    user = client.database.get_user(query.from_user.id)
    city = user.city or "Москва"
    weather = get_current_weather(city)
    if weather == query.message.text:
        return
    await query.message.edit_text(
        weather,
        reply_markup=keyboards.weather_inline_keyboard
    )


@bot.on_callback_query(filters=inline_button_filter(buttons.weather_forecast_inline_button))
async def weather_forecast_inline_button_callback(client: MyBot, query: CallbackQuery):
    user = client.database.get_user(query.from_user.id)
    city = user.city or "Москва"
    forecast = get_forecast(city)
    if forecast == query.message.text:
        return
    await query.message.edit_text(
        forecast,
        reply_markup=keyboards.weather_inline_keyboard
    )


@bot.on_message(filters.command("cats") | button_filter(buttons.cats_button))
async def cats_command(client: MyBot, message: Message):
    cat = get_random_cat()
    await client.send_photo(
        chat_id=message.chat.id,
        photo=cat,
        reply_markup=keyboards.cats_inline_keyboard
    )


@bot.on_callback_query(filters=inline_button_filter(buttons.cats_random_inline_button))
async def cats_random_inline_button_callback(client: MyBot, query: CallbackQuery):
    cat = get_random_cat()
    await query.message.edit_media(
        media=InputMediaPhoto(cat),
        reply_markup=keyboards.cats_inline_keyboard,
    )


@bot.on_message()
async def echo(client: MyBot, message: Message):
    text = message.text
    if random.choice([True, False]):
        await message.reply(text)
    else:
        await message.reply(text[::-1])


bot.run()
