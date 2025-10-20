import re
import time

def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


def start_message(username):
    username = escape_markdown_v2(username)
    message = (f"👋 Привет, {username}\\!"
               f"\n\nТвоя *пробная подписка* уже активирована ✅\n"
               f"🎉 _3 дня бесплатного доступа_ к нашему VPN 🚀\n"
               f"Подключай устройство и наслаждайся свободой интернета 🌍")
    return message

def unsuccess_message(username):
    username = escape_markdown_v2(username)
    message = (f"👋 Привет, {username}\\!"
               f"\n\nВаша подписка закончилась."
               f"\nДля продолжения работы бота её необходимо продлить:" )
    return message

def success_message(username, expiry_time):
    username = escape_markdown_v2(username)
    strf = escape_markdown_v2(time.strftime('%d.%m.%Y', time.localtime(expiry_time)))
    message = (f"👋 Привет, {username}\\!"
               f"\n\nТвоя *подписка* активна до {strf}✅\n"
               f"Подключай устройство и наслаждайся свободой интернета 🌍")
    return message


def choose_device():
    message = (f" Выбери *устройство*, которое хочешь подключить:"
               f"\n\n📱 IPhone\n"
               f"☎️ Смартфон Android\n"
               f"🖥️ Компьютер Windows\n"
               f"💻 Компьютер MacOS\n")
    return message


def help_message():
    supp_link = escape_markdown_v2("@vpn_supp0rtbot")
    message = (f"⚠️ Возникли *проблемы*\\?\n"  
                f"📩 Напиши в поддержку, и мы поможем решить всё максимально быстро 🛠\n\n️"
                f"{supp_link}\n\n"
                f"_Мы всегда на связи\\!_")
    return message


def ref_link(ref_link):
    ref = escape_markdown_v2(ref_link)
    message = (f"🤝 Делись свободой интернета с друзьями\\!\n\n"  
                f"🔗 Ваша *пригласительная ссылка*: {ref}\n\n"  
                f"🎁 За каждого друга мы дарим тебе _3 дополнительных дня_ подписки 🚀\n"  
                f"*Больше друзей → больше интернета без границ\\!*")
    return message

def success_pay(new_expiry):
    strf = escape_markdown_v2(time.strftime('%d.%m.%Y', time.localtime(new_expiry)))
    message = (f"Спасибо за оплату\\! Подписка продлена до {strf}✅\n\n"
            f"Для установки VPN на своё устройство следуйте инструкциям")

    return message

def ref_send(referral_name, new_expiry):
    referral_name = escape_markdown_v2(referral_name)
    start = escape_markdown_v2("/start")
    expiry_time = escape_markdown_v2(time.strftime('%d.%m.%Y', time.localtime(new_expiry)))
    message = (f"Здравствуйте\\!\n\n"
               f"Ваш друг @{referral_name} теперь в нашей семье\n"
               f"За это мы уже начислили вам *3 дополнительных дня*\n"
               f"Теперь ваша подписка активна до: {expiry_time}\n"
               f"Для продолжения работы с ботом нажмите {start}\n")
    return message

def remind_message(username):
    username = escape_markdown_v2(username)
    message = (f"Уважаемый {username}\n"
               f"Ваша подписка подходит к концу\n"
               f"Для того, чтоб продолжать получать доступ к "
               f"интернету её необходимо продлить")
    return message

def remind_for_deactivate(username):
    username = escape_markdown_v2(username)
    message = (f"Уважаемый {username}\n"
               f"Ваша подписка _закончилась_, но это *не повод* расстраиваться\n"
               f"По кнопкам ниже вы можете произвести оплату\n"
               f"Мы будем рады, если вы *снова* будете пользоваться нашим сервисом"
               )
    return message