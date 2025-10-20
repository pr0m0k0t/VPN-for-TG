import os
import uuid
import json
from email.policy import default

import qrcode
import io
import base64
import json
import aiohttp
import time
from typing import Optional, Dict
from database.database_mysql import UserDatabaseMySQL
import aiohttp
from config.settings import *

db = UserDatabaseMySQL(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)


class VPNService:
    def __init__(self):
        self.base_url = f"http://{X_UI_HOST}:{X_UI_PORT}{X_UI_URL}"
        self.inbound_id = X_UI_INBOUND_ID
        self.update_url = "http://72.56.64.215:56732/GBeLFthurQCSZHiaZY/panel/api/inbounds/update/1"
        self.session_cookie = None

    async def login(self) -> bool:
        """Авторизация в 3x-ui панели"""
        async with aiohttp.ClientSession() as session:
            login_data = {
                'username': X_UI_USERNAME,
                'password': X_UI_PASSWORD
            }
            try:
                async with session.post(f"{self.base_url}/login", data=login_data) as response:
                    if response.status == 200:
                        self.session_cookie = response.cookies
                        return True
                    else:
                        print(f"[VPNService] Ошибка логина: статус {response.status}")

            except Exception as e:
                print(f"[VPNService] Исключение при логине: {e}")
                return False


    async def create_vpn_user(self, user_id: int, username: str) -> Optional[Dict]:
        """Создание нового пользователя VPN"""
        if not await self.login():
            print("[VPNService] Не удалось авторизоваться в 3x-ui")
            return None

        user_uuid = str(uuid.uuid4())
        current_time = int(time.time())
        three_days_seconds = 3 * 24 * 60 * 60 * 1000
        expiry_time = current_time* 1000 + three_days_seconds

        client_data = {
            "id": user_uuid,
            "email": f"{user_id}",
            "flow": "xtls-rprx-vision",
            "limitIp": 1,
            "totalGB": 0,
            "enable": True,
            "tgId": user_id,
            "port": VPN_PORT,
            "expiryTime": expiry_time,
        }

        async with aiohttp.ClientSession(cookies=self.session_cookie) as session:
            # Добавляем клиента к существующему inbound
            add_client_url = f"{self.base_url}/panel/api/inbounds/addClient"

            payload = {
                "id": X_UI_INBOUND_ID,
                "settings": json.dumps({
                    "clients": [client_data]
                    })
                }

            async with session.post(add_client_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            # Генерируем конфигурацию для клиента
                            config = await self._generate_vless_config(user_uuid, user_id)

                            return {
                                'uuid': user_uuid,
                                'config': config,
                                'qr_code': self._generate_qr_code(config)
                            }

                        else:
                            print(f"[VPNService] Ответ панели без success: {result}")
                            return None
                    else:
                        print(f"[VPNService] Ошибка запроса add_client: статус {response.status}")
                        return None

    async def _generate_vless_config(self, user_uuid: str, user_id: int) -> str:
            async with aiohttp.ClientSession(cookies=self.session_cookie) as session:
                async with session.get(f"{self.base_url}/panel/api/inbounds/get/{X_UI_INBOUND_ID}") as response:
                    if response.status == 200:
                        inbound_data = await response.json()
                        settings = json.loads(inbound_data['obj']['settings'])
                        stream_settings = json.loads(inbound_data['obj']['streamSettings'])

                        reality_settings = stream_settings.get('realitySettings')
                        if not reality_settings:
                            raise Exception('Нет блока realitySettings!')

                        settings = reality_settings.get('settings')
                        if not settings or 'publicKey' not in settings:
                            print('realitySettings:', reality_settings)
                            raise Exception('publicKey отсутствует в realitySettings.settings')

                        public_key = settings['publicKey']
                        # Далее используйте public_key для формирования ключа

                        fingerprint = reality_settings.get('fingerprint', 'chrome')
                        server_names = reality_settings.get('serverNames', ['main'])[0]
                        short_ids = reality_settings.get('shortIds', [''])[0]

                        # Формируем ссылку с проверенными полями
                        vless_url = (
                            f"vless://{user_uuid}@{VPN_SERVER_IP}:{VPN_PORT}"
                            f"?type={stream_settings.get('network', 'tcp')}"
                            f"&encryption=none"
                            f"&security={stream_settings.get('security', 'reality')}"
                            f"&pbk={public_key}"
                            f"&fp={fingerprint}"
                            f"&sni={server_names}"
                            f"&sid={short_ids}"
                            f"&spx=%2F"
                            f"&flow=xtls-rprx-vision"
                            f"#{X_UI_INBOUND_NAME}-{user_id}"
                        )

                        return vless_url
                    return ""

    def _generate_qr_code(self, config: str) -> str:
        """Генерация QR-кода для конфигурации"""

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(config)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)

        return base64.b64encode(bio.getvalue()).decode()

    async def update_expiry_time_3xui(self, client_id: str, new_expiry_time: int) -> bool:
        """
        Обновление expiry_time клиента
        """

        if not await self.login():
            print("VPNService: Авторизация не удалась")
            return False

        async with aiohttp.ClientSession(cookies=self.session_cookie) as session:
            # Получаем список inbound
            async with session.get(f"{self.base_url}/panel/api/inbounds/list") as resp:
                if resp.status != 200:
                    print(f"VPNService: ошибка получения inbound list {resp.status}")
                    return False
                data = await resp.json()

            inbounds = data.get("obj", [])
            inbound = next((i for i in inbounds if i["id"] == self.inbound_id), None)
            if inbound is None:
                print(f"VPNService: inbound с id={self.inbound_id} не найден")
                return False

            # Парсим settings, модифицируем expiryTime нужного клиента
            settings = json.loads(inbound["settings"])
            clients = settings.get("clients", [])
            found = False
            for client in clients:
                if client["email"] == client_id:
                    old_expiry_time = client["expiryTime"]
                    client["expiryTime"] = new_expiry_time
                    found = True
                    break
            if not found:
                print(f"VPNService: клиент с username={client_id} не найден")
                return False

            # Делаем обновлённый payload
            inbound["settings"] = json.dumps(settings)
            update_url = f"{self.base_url}/panel/api/inbounds/update/{inbound['id']}"
            async with session.post(update_url, json=inbound) as update_resp:
                if update_resp.status == 200:
                    return await update_resp.json()
                else:
                    print(f"VPNService: ошибка обновления expiryTime {update_resp.status}")
                    return None


    async def delete_vpn_user(self, user_uuid: str) -> bool:
        """Удаление пользователя VPN"""
        if not await self.login():
            return False

        async with aiohttp.ClientSession(cookies=self.session_cookie) as session:
            delete_url = f"{self.base_url}/panel/api/inbounds/{X_UI_INBOUND_ID}/delClient/{user_uuid}"

            async with session.post(delete_url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('success', False)

        return False