import asyncio
from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.types import LabeledPrice

from config.messages import *
from services.keyboards import *
from config.settings import PAYMENTS_PROVIDER_TOKEN, BOT_TOKEN
from aiogram.enums import ParseMode
from database.database_mysql import UserDatabaseMySQL
from config.settings import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

db = UserDatabaseMySQL(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

client_router = Router()
vpn_service = VPNService()

bot = Bot(token=BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))


@client_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):

    user_id = message.from_user.id
    FREE_DAYS_SECONDS = 3 * 60 * 60 * 24
    text = message.text or ""
    parts = text.split("_")
    ref = parts[-1] if len(parts) > 1 else None
    user = db.get_user(user_id)
    now = int(time.time())
    expiry_time = now + FREE_DAYS_SECONDS
    username = message.from_user.username or f"user{user_id}"

    if not user:
        vpn_data = await vpn_service.create_vpn_user(user_id, username)

        if vpn_data is not None:
            if 'uuid' in vpn_data and 'config' in vpn_data:
                db.add_user(user_id, username, vpn_data['uuid'], vpn_data['config'], expiry_time)
                caption = start_message(username)
                await message.answer_photo(photo=FSInputFile("logo.jpg"),
                                             caption=caption,
                                             parse_mode=ParseMode.MARKDOWN_V2,
                                             reply_markup=main_menu_kb)
                if ref is not None:
                    referral = db.get_user(int(ref))

                    old_expiry = referral.get("expiry_time", 0)
                    base_time = old_expiry if old_expiry > now else now
                    new_expiry_for_db = base_time + 3 * 24 * 3600 # +3 дня

                    db.update_expiry(ref, new_expiry_for_db)

                    expiry_time_3 = base_time + FREE_DAYS_SECONDS

                    await vpn_service.update_expiry_time_3xui(ref, expiry_time_3 * 1000)
                    await state.update_data(ref=ref)
                    await bot.send_message(chat_id = ref,
                                           text= ref_send(username, expiry_time_3))
            else:
                print("Ошибка: В vpn_data отсутствует ключ uuid или config")
        else:
            print("Ошибка: vpn_service.create_vpn_user вернул None")
    else:
        if user.get('expiry_time', 0) > now:
            await message.answer_photo(photo= FSInputFile("logo.jpg"),
                caption= success_message(username, user.get('expiry_time', 0)),
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=main_menu_kb)
        else:
            db.deactivate_user(user_id)
            await message.answer_photo(photo= FSInputFile("logo.jpg"),
                                 caption = "👋 Ваша подписка закончилась. Для продолжения работы бота её необходимо продлить:",
                                 reply_markup=subscribe_kb)
@client_router.callback_query(F.data == "menu_1")
async def cmd_menu(call: CallbackQuery):
    user_id = call.message.from_user.id
    user = db.get_user(user_id)
    now = int(time.time())
    username = call.message.from_user.username or f"user{user_id}"
    if user.get('expiry_time', 0) > now:
        await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                                        caption=success_message(username, user.get('expiry_time', 0)),
                                        parse_mode=ParseMode.MARKDOWN_V2,
                                        reply_markup=main_menu_kb)
    else:
        await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                                        caption=unsuccess_message(username),
                                        reply_markup=subscribe_kb)


@client_router.callback_query(F.data == "menu_2")
async def cmd_menu2(call: CallbackQuery, state: FSMContext):
    user_id = state.get_state()
    user = db.get_user(user_id)
    username = call.message.from_user.username or f"user{user_id}"
    await call.message.delete()
    await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                                    caption=success_message(username, user.get('expiry_time', 0)),
                                    parse_mode=ParseMode.MARKDOWN_V2,
                                    reply_markup=main_menu_kb)

@client_router.callback_query(F.data == "back_to_subs")
async def back_to_subs(call: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(data['chat_id'], data['message1_id'])
        await bot.delete_message(data['chat_id'], data['message_id'])
        await state.clear()
    except:
        pass
    await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                                    caption="Выберите тариф подписки:",
                                    reply_markup=subscribe_kb)


@client_router.callback_query(lambda c: c.data == "subscribe")
async def process_subscribe(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await state.update_data(user_id=user_id)
    await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
        caption= "Выберите тариф подписки:",
        reply_markup=subscribe_kb)

@client_router.callback_query(F.data == "back_to_device")
@client_router.callback_query(F.data=="select_dev")
async def select_dev(call: CallbackQuery):
    await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                              caption= choose_device(),
                              parse_mode=ParseMode.MARKDOWN_V2,
                              reply_markup=select_device_kb)


@client_router.callback_query(lambda c: c.data == "invite")
async def process_invite(call: CallbackQuery):
    user_id= call.from_user.id

    # Генерируем уникальную реферальную ссылку
    referral_link = f"https://t.me/{(await bot.me()).username}?start=ref_{user_id}"

    await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                              caption= ref_link(referral_link),
                              parse_mode=ParseMode.MARKDOWN_V2,
                              reply_markup=back_to_menu_kb)


@client_router.callback_query(lambda c: c.data == "help")
async def process_help(call: CallbackQuery):
    await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                              caption= help_message(),
                              parse_mode=ParseMode.MARKDOWN_V2,
                              reply_markup=back_to_menu_kb)


@client_router.callback_query(lambda c: c.data == "back_to_menu")
async def process_back(call: CallbackQuery):
    username = call.from_user.username
    user_id = call.from_user.id

    user = db.get_user(user_id)
    expiry_time = user.get("expiry_time", 0)

    await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                              caption = success_message(username, expiry_time),
                              parse_mode=ParseMode.MARKDOWN_V2,
                              reply_markup=main_menu_kb)


@client_router.callback_query(lambda c: c.data.startswith("plan_"))
async def process_plan(call: CallbackQuery, state: FSMContext):
    user= await state.get_data()
    user_id = user["user_id"]
    print(user_id)
    months = int(call.data.split("_")[1])
    await call.message.delete()
    mes1 = await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                              caption= f"Вы выбрали подписку на {months} месяцев. Оформление платежа...")
    await state.update_data(message1_id=mes1.message_id)
    await asyncio.sleep(3)
    #await call.message.delete()
    if months == 1:
        amount = 9900  # amount в копейках (99 рублей)
        description = "Доступ на месяц"
    elif months == 3:
        amount = 24900
        description = 'Доступ на 3 месяца'
    elif months == 6:
        amount = 44900 # 75%
        description = 'Доступ на полгода'
    elif months == 12:
        amount = 79900 # 66%
        description = 'Доступ на год'

    prices = [LabeledPrice(label="Подписка на VPN", amount=amount)]
    invoice = await call.message.answer_invoice(
        title="VPN Подписка",
        description=description,
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="vpn-subscription",
        payload=f"{user_id}:{months}"
    )
    await state.update_data(chat_id =invoice.chat.id, message_id = invoice.message_id)
    await call.message.answer('Если хотите изменить выбор подписки, то нажмите кнопку ниже',
                              reply_markup=back_to_subs_kb)


@client_router.pre_checkout_query(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@client_router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    user_id, months = map(int, message.successful_payment.invoice_payload.split(":"))
    now = int(time.time())
    user = db.get_user(user_id)

    current_expiry = user.get("expiry_time", 0) if user else 0
    base_time = current_expiry if current_expiry > now else now

    # Добавляем месяцы (30 дней на месяц в секундах)
    new_expiry = base_time + months * 30 * 24 * 3600
    new_vpn_expiry = new_expiry * 1000
    # Обновляем в базе
    await vpn_service.update_expiry_time_3xui(user_id, new_vpn_expiry)
    db.update_expiry(user_id, new_expiry)
    await state.clear()
    await message.answer_photo(photo=FSInputFile("logo.jpg"),
                               caption= success_pay(new_expiry),
                               reply_markup=select_device_kb)


@client_router.callback_query(F.data.startswith("select_device_"))
async def select_device(call: CallbackQuery):
    device = call.data.split("_")[2]
    user_id = call.from_user.id

    if device == "1":
        await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                                        caption='Для подключения вашего IPhone следуйте инструкциям',
                                        reply_markup=await device1_kb(user_id))
    elif device == "2":
        await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                                        caption='Для подключения вашего телефона следуйте инструкциям',
                                        reply_markup=await device2_kb(user_id))
    elif device == "3":
        await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                                        caption='Для подключения вашего ПК следуйте инструкциям',
                                        reply_markup=await device3_kb(user_id))
    elif device == "4":
        await call.message.edit_caption(photo=FSInputFile("logo.jpg"),
                                        caption='Для подключения вашего Mac следуйте инструкциям',
                                        reply_markup=await device1_kb(user_id))


@client_router.callback_query(lambda c: c.data.startswith("plandeactivate_"))
async def process_plan(call: CallbackQuery, state: FSMContext):
    user= await state.get_data()
    user_id = user["user_id"]
    print(user_id)
    months = int(call.data.split("_")[1])
    await call.message.delete()
    mes1 = await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                              caption= f"Вы выбрали подписку на {months} месяцев. Оформление платежа...")
    await state.update_data(message1_id=mes1.message_id)
    await asyncio.sleep(3)
    #await call.message.delete()
    if months == 1:
        amount = 9900  # amount в копейках (99 рублей)
        description = "Доступ на месяц"
    elif months == 3:
        amount = 24900
        description = 'Доступ на 3 месяца'
    elif months == 6:
        amount = 44900 # 75%
        description = 'Доступ на полгода'
    elif months == 12:
        amount = 79900 # 66%
        description = 'Доступ на год'

    prices = [LabeledPrice(label="Подписка на VPN", amount=amount)]
    invoice = await call.message.answer_invoice(
        title="VPN Подписка",
        description=description,
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="vpn-subscription",
        payload=f"{user_id}:{months}"
    )
    await state.update_data(chat_id =invoice.chat.id, message_id = invoice.message_id)
    await call.message.answer('Если хотите изменить выбор подписки, то нажмите кнопку ниже',
                              reply_markup=back_to_subs_deactivate_kb)

@client_router.callback_query(F.data == "begin")
@client_router.callback_query(F.data == "back_to_subs_deactivate")
async def back_to_subs(call: CallbackQuery, state: FSMContext):
    user_id = call.message.from_user.id
    await state.update_data(user_id=user_id)
    username = call.from_user.username
    try:
        await call.message.delete()
    except:
        pass
    try:
        data = await state.get_data()
        await bot.delete_message(data['chat_id'], data['message1_id'])
        await bot.delete_message(data['chat_id'], data['message_id'])
        await state.clear()
    except:
        pass
    await call.message.answer_photo(photo=FSInputFile("logo.jpg"),
                                    caption=remind_for_deactivate(username),
                                    parse_mode=ParseMode.MARKDOWN_V2,
                                    reply_markup=subscribe_deactivate_kb)