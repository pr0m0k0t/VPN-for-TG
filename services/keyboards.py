from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#from database.database_mysql import UserDatabaseMySQL
from services.vpn_service import VPNService
from services.add_links import *
#from config.settings import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

#db = UserDatabaseMySQL(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
vpn_service= VPNService()

# Клавиатура главного меню
main_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔗 Подключиться", callback_data="select_dev")],
    [InlineKeyboardButton(text="✅ Продлить подписку", callback_data="subscribe")],
    [InlineKeyboardButton(text="👤 Пригласить друзей", callback_data="invite")],
    [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
])


# Клавиатура выбора тарифа
subscribe_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ месяц - 99 руб", callback_data="plan_1")],
    [InlineKeyboardButton(text="3️⃣ месяца - 249 руб", callback_data="plan_3")],
    [InlineKeyboardButton(text="6️⃣ месяцев - 449 руб", callback_data="plan_6")],
    [InlineKeyboardButton(text="1️⃣2️⃣ месяцев - 799 руб", callback_data="plan_12")],
    [InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_menu")]
])

subscribe_deactivate_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ месяц - 99 руб", callback_data="plandeactivate_1")],
    [InlineKeyboardButton(text="3️⃣ месяца - 249 руб", callback_data="plandeactivate_3")],
    [InlineKeyboardButton(text="6️⃣ месяцев - 449 руб", callback_data="plandeactivate_6")],
    [InlineKeyboardButton(text="1️⃣2️⃣ месяцев - 799 руб", callback_data="plandeactivate_12")]
])

menu_back_kb1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В главное меню ⬅️", callback_data="menu_1")],
])

menu_back_kb2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В главное меню ⬅️", callback_data="menu_2")],
])

back_to_subs_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_subs")],
])

back_to_subs_deactivate_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_subs_deactivate")],
])

back_to_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_menu")],
])

begin_pay_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Перейти к оплате", callback_data="begin")],
])

select_device_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 Iphone", callback_data="select_device_1")],
    [InlineKeyboardButton(text="☎️ Android", callback_data="select_device_2")],
    [InlineKeyboardButton(text="🖥️ Windows", callback_data="select_device_3")],
    [InlineKeyboardButton(text="💻 MacOS", callback_data="select_device_4")],
    [InlineKeyboardButton(text="Вернуться в меню ⬅️", callback_data="back_to_menu")],
])


async def device1_kb(user_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ Скачайте приложение", url='https://apps.apple.com/app/id6476628951')],
    [InlineKeyboardButton(text="2️⃣ Установите профиль", url=await iphone_link(user_id))],
    [InlineKeyboardButton(text="Вернуться назад ⬅️", callback_data="back_to_device")],
    ])
    return kb


async def device2_kb(user_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ Скачайте приложение", url='https://play.google.com/store/apps/details?id=app.hiddify.com')],
    [InlineKeyboardButton(text="2️⃣ Установите профиль", url=await android_link(user_id))],
    [InlineKeyboardButton(text="Вернуться назад ⬅️", callback_data="back_to_device")],
    ])
    return kb


async def device3_kb(user_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ Скачайте приложение", url='https://github.com/hiddify/hiddify-next/releases/download/v2.5.7/Hiddify-Windows-Setup-x64.exe')],
    [InlineKeyboardButton(text="2️⃣ Установите профиль", url=await PC_link(user_id))],
    [InlineKeyboardButton(text="Вернуться назад ⬅️", callback_data="back_to_device")],
    ])
    return kb