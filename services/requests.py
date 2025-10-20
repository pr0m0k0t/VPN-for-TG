import asyncio
import time
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.messages import remind_for_deactivate, remind_message
from database.database_mysql import UserDatabaseMySQL

from config.settings import *
from services.keyboards import begin_pay_kb, subscribe_kb

db = UserDatabaseMySQL(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
bot = Bot(token=BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))

async def remind_expired_users():
    """Асинхронная проверка срока действия пользователей"""
    While True:
          now = int(time.time())
          users = db.get_all_users()
          expired_users = [u for u in users if u.get("expiry_time") and u["expiry_time"] < now]
          
          if expired_users:
              print(f"Истёкших пользователей: {len(expired_users)}")
              for user in expired_users:
                  user_id = user.get("user_id")
                  username = user.get("username")
                  await bot.send_message(user_id,
                                         remind_for_deactivate(username),
                                         parse_mode=ParseMode.MARKDOWN_V2,
                                         reply_markup=begin_pay_kb)
          else:
              print("Нет пользователей с истекшим сроком.")    
          await asyncio.sleep(1000)

async def check_expired_users():
    """Асинхронная проверка срока действия пользователей"""
    while True:
        now = int(time.time())
        users = db.get_all_users()
        expired_users = [u for u in users if u.get("expiry_time") and u["expiry_time"] < now]

        if expired_users:
            print(f"Истёкших пользователей: {len(expired_users)}")
            for user in expired_users:
                user_id = user.get("user_id")
                if user["active"]:
                    # Пример возможного действия: деактивация
                    db.deactivate_user(user_id)
        await asyncio.sleep(86400 * 3) #3 days


async def remind_about_expiry():
    while True:
        ONE_DAY_SECONDS = 24 * 60 * 60
        now = int(time.time())
        users = db.get_all_users()
        for user in users:
            expiry_time = user.get("expiry_time")
            username = user.get("username")
            active = user.get("active")
            user_id = user.get("user_id")
            if expiry_time and active:
                seconds_left = expiry_time - now
                # Проверяем, остался ли ровно 1 день (или чуть меньше, например, от 1 до 24 часов)
                if 0 < seconds_left <= ONE_DAY_SECONDS:
                    try:
                        await bot.send_message(user_id,
                                               remind_message(username),
                                               parse_mode=ParseMode.MARKDOWN_V2,
                                               reply_markup=subscribe_kb)
                    except Exception as e:
                        print(f"Ошибка для {user_id}: {e}")

        await asyncio.sleep(1000)
