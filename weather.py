import datetime
import pytz
import pyowm.commons.exceptions
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from pyrogram import emoji

import config

def get_omw_client() -> OWM:
    owm_config = get_default_config()
    owm_config["language"] = "ru"
    return OWM(api_key=config.OWM_KEY, config=owm_config)

client = get_omw_client()

weather_emojis = {
    'Thunderstorm': emoji.CLOUD_WITH_LIGHTNING_AND_RAIN,
    'Drizzle': emoji.UMBRELLA_WITH_RAIN_DROPS,
    'Rain': emoji.CLOUD_WITH_RAIN,
    'Snow': emoji.SNOWFLAKE,
    'Clear': emoji.SUN,
    'Clouds': emoji.CLOUD,
}

def get_current_weather(city: str) -> str:
    mgr = client.weather_manager()
    try:
        obs = mgr.weather_at_place(city)
    except pyowm.commons.exceptions.NotFoundError:
        return "❗ Город не найден."
    except Exception:
        return "⚠️ Не удалось получить погоду."

    w = obs.weather
    status = w.detailed_status.capitalize()
    emoji_icon = weather_emojis.get(w.status, "")
    temp = w.temperature('celsius')['temp']
    wind = w.wind()['speed']
    humidity = w.humidity

    temp_sign = "+" if temp > 0 else ""
    msg = f"🌤️ Погода в городе {city}:\n\n"
    msg += f"{status} {emoji_icon}\n"
    msg += f"🌡️ Температура: {temp_sign}{temp:.1f}°C\n"
    msg += f"💨 Ветер: {wind:.1f} м/с\n"
    msg += f"💧 Влажность: {humidity}%"
    return msg


def get_forecast(city: str) -> str:
    mgr = client.weather_manager()
    try:
        forecast = mgr.forecast_at_place(city, '3h')
    except pyowm.commons.exceptions.NotFoundError:
        return "❗ Город не найден."
    except Exception:
        return "⚠️ Ошибка при получении прогноза."

    weather_list = forecast.forecast.weathers

    base_time = datetime.datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    needed = [base_time + datetime.timedelta(days=d, hours=h)
              for d in range(1, 4) for h in (0, 6, 12, 18)]
    data = [w for w in weather_list if w.reference_time('date') in needed]

    hours = {0: "🌙 Ночь", 6: "🌅 Утро", 12: "🌞 День", 18: "🌇 Вечер"}
    day_titles = ['Завтра', 'Послезавтра', 'Через 3 дня']

    msg = f"📆 Прогноз погоды в {city}:\n\n"
    for i in range(3):
        msg += f"{day_titles[i]}:\n"
        for j in range(4):
            w = data[i * 4 + j]
            status = w.detailed_status
            temp = w.temperature('celsius')['temp']
            temp_sign = "+" if temp > 0 else ""
            emoji_icon = weather_emojis.get(w.status, "")
            hour = w.reference_time('date').hour
            msg += f"{hours[hour]}: {temp_sign}{temp:.0f}°C, {status} {emoji_icon}\n"
        msg += "\n"
    return msg
