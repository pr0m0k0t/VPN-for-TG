import mysql.connector
from mysql.connector import Error
import datetime
from typing import Optional, Dict

from config.settings import DB_NAME


class UserDatabaseMySQL:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port="3306",
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            self._create_table_if_not_exists()
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")

    def _create_table_if_not_exists(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id BIGINT ,
            username VARCHAR(255),
            vpn_uuid VARCHAR(255),
            vpn_config TEXT,
            active BOOLEAN,
            expiry_time BIGINT,
            created_at DATETIME
        )
        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        cursor.close()


    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port="3306",
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")


    def add_user(self, user_id: int, username: str, vpn_uuid: str, vpn_config: str, expiry_time: int):
        try:
            query = """
                    INSERT INTO users (user_id, username, vpn_uuid, vpn_config, active, expiry_time, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                      username=VALUES(username),
                      vpn_uuid=VALUES(vpn_uuid),
                      vpn_config=VALUES(vpn_config),
                      active=VALUES(active),
                      expiry_time=VALUES(expiry_time),
                      created_at=VALUES(created_at)
                    """
            try:
                cursor = self.connection.cursor()
                cursor.execute(query, (
                    user_id,
                    username,
                    vpn_uuid,
                    vpn_config,
                    True,
                    expiry_time,
                    datetime.datetime.now()
                ))
                self.connection.commit()
                cursor.close()
                print("[MySQL] Пользователь добавлен/обновлен")
            except Exception as e:
                print(f"[MySQL] Ошибка добавления пользователя: {e}")
        except:
            self._connect()
            query = """
                                INSERT INTO users (user_id, username, vpn_uuid, vpn_config, active, expiry_time, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE
                                  username=VALUES(username),
                                  vpn_uuid=VALUES(vpn_uuid),
                                  vpn_config=VALUES(vpn_config),
                                  active=VALUES(active),
                                  expiry_time=VALUES(expiry_time),
                                  created_at=VALUES(created_at)
                                """
            try:
                cursor = self.connection.cursor()
                cursor.execute(query, (
                    user_id,
                    username,
                    vpn_uuid,
                    vpn_config,
                    True,
                    expiry_time,
                    datetime.datetime.now()
                ))
                self.connection.commit()
                cursor.close()
                print("[MySQL] Пользователь добавлен/обновлен")
            except Exception as e:
                print(f"[MySQL] Ошибка добавления пользователя: {e}")

    def get_user(self, user_id: int) -> Optional[Dict]:
       try:
            query = "SELECT user_id, username, vpn_uuid, vpn_config, active, expiry_time, created_at FROM users WHERE user_id = %s"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result
            return None
       except:
            self._connect()
            self.get_user(user_id)

    def get_user_by_id(self, id: int) -> Optional[Dict]:
       try:
            query = "SELECT user_id, username, vpn_uuid, vpn_config, active, expiry_time, created_at FROM users WHERE id = %s"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (id,))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result
            return None
       except:
            self._connect()
            self.get_user_by_id(id)

    def update_expiry(self, user_id, new_expiry):
        user = self.get_user(user_id)
        if user:
            username = user['username']
            vpn_uuid = user['vpn_uuid']
            vpn_config = user['vpn_config']
            self.delete_user(user_id)
            self.add_user(user_id, username, vpn_uuid, vpn_config, new_expiry)
        return None

    def update_expiry_time(self, user_id: int, new_expiry_time: int) -> bool:
        """
        Обновить поле expiry_time для пользователя с заданным user_id.
        Возвращает True при успехе, иначе False.
        """
        query = "UPDATE users SET expirytime = %s WHERE userid = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (new_expiry_time, user_id))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("DB error (update_expiry_time):", e)
            return False


    def get_all_users(self) -> Optional[Dict]:
        try:
            query = f"SELECT user_id, username, vpn_uuid, vpn_config, active, expiry_time, created_at FROM users"
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            if result:
                return result
            return None
        except:
            self._connect()
            self.get_all_users()

    def delete_user(self, user_id: int):
        try:
            query = "DELETE FROM users WHERE user_id = %s"
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id,))
            cursor.close()
        except:
            self._connect()
            self.delete_user(user_id)

    def deactivate_user(self, user_id: int):
        query = "UPDATE users SET active = FALSE WHERE user_id = %s"
        cursor = self.connection.cursor()
        cursor.execute(query, (user_id,))
        cursor.close()