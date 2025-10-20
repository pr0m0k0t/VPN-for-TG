from urllib.parse import quote_plus, urlencode

from database.database_mysql import UserDatabaseMySQL
from config.settings import VPN_SERVER_IP
from config.settings import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

db = UserDatabaseMySQL(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)


def get_user_config(user_id: int):
    user = db.get_user(user_id)
    if user is None:
            # Например, верните ошибку или лог для отладки
        raise ValueError(f"User with id {user_id} not found")
    profile_url = str(user['vpn_config'])
    base_url = f"http://{VPN_SERVER_IP}/profiles/"
    return f"{base_url}{profile_url}"


async def iphone_link(user_id: int):
    redirect_url = f"http://{VPN_SERVER_IP}/import_profile?id={user_id}"
    return redirect_url

async def android_link(user_id: int):
    redirect_url = f"http://{VPN_SERVER_IP}/hiddify?id={user_id}"
    return redirect_url

async def PC_link(user_id: int):
    redirect_url = f"http://{VPN_SERVER_IP}/hiddify?id={user_id}"
    return redirect_url



