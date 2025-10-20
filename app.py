from flask_cors import CORS
from flask import Flask, request, redirect, abort, render_template_string
import jinja2
# Импорт или инициализация вашей БД, например UserDatabaseMySQL, UserDatabase и т.д.
from database.database_mysql import UserDatabaseMySQL
from config.settings import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

db = UserDatabaseMySQL(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

app = Flask(__name__)
CORS(app) # Разрешит кросс-доменные запросы
# Пример шаблона HTML с динамической ссылкой
html_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Импорт профиля в Hiddify</title>
</head>
<body>
<h2>Импорт профиля VPN в Hiddify</h2>
<p>Нажмите кнопку ниже для импорта профиля:</p>
<a href="{{ import_link|safe }}">
  <button>Импортировать в Hiddify</button>
</a>
</body>
</html>
"""

# Пример функции, возвращающей диплинк для user_id
def get_vpn_deeplink(user_id, link_for):
    # Здесь запрос к вашей базе данных
    user = db.get_user(int(user_id))
    if not user or 'vpn_config' not in user:
        return None
    if link_for == 'v2raytun':
        deeplink = 'v2raytun://import/' + user['vpn_config']
    elif link_for == 'hiddify':
        deeplink = 'hiddify://import/' + user['vpn_config']
    else:
        deeplink = ''
    return deeplink  # Пусть хранится полноценный диплинк

@app.route('/hiddify', methods=['GET'])
def hiddify():
    # Получаем ключ профиля из параметра запроса
    user_id = request.args.get('id')
    deep_link = get_vpn_deeplink(user_id, 'hiddify')

    # Отдаем HTML с кнопкой и ссылкой
    return render_template_string(html_template, import_link=deep_link)

@app.route('/import_profile', methods=['GET'])
def import_profile():
    user_id = request.args.get('id')
    if not user_id:
        return abort(400, "Missing user ID")
    link_for = 'v2raytun'
    deeplink = get_vpn_deeplink(user_id, link_for)
    if not deeplink:
        return abort(404, "User VPN profile not found")

    # Редирект на диплинк
    return redirect(deeplink, code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
