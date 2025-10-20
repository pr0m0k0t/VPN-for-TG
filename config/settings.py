import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
PAYMENTS_PROVIDER_TOKEN = os.getenv('PAYMENTS_PROVIDER_TOKEN')

# 3x-ui API настройки
X_UI_HOST = os.getenv('X_UI_HOST')
X_UI_PORT = os.getenv('X_UI_PORT')
X_UI_USERNAME = os.getenv('X_UI_USERNAME')
X_UI_PASSWORD = os.getenv('X_UI_PASSWORD')
X_UI_INBOUND_ID = int(os.getenv('X_UI_INBOUND_ID'))
X_UI_INBOUND_NAME = os.getenv('X_UI_INBOUND_NAME')
X_UI_URL = os.getenv('X_UI_URL')
X_UI_PUBLIC_KEY = os.getenv('X_UI_PUBLICKEY')

# VPN настройки
VPN_SERVER_IP = os.getenv('VPN_SERVER_IP')
VPN_PORT = int(os.getenv('VPN_PORT'))
REDIRECT_PORT = int(os.getenv('REDIRECT_PORT'))
#Настройки БД
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')


