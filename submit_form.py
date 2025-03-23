#!/usr/bin/env python3

import cgi
import http.cookies
import re
import pymysql
from datetime import datetime, timedelta

# Создание подключения к базе данных
def create_connection():
    try:
        return pymysql.connect(
            host='158.160.150.89',
            user='u68593',
            password='9258357',
            database='web_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Валидация полей формы с использованием регулярных выражений
def validate_form(data):
    errors = {}
    patterns = {
        'last_name': r'^[А-Яа-яЁё\s\-]+$',
        'first_name': r'^[А-Яа-яЁё\s\-]+$',
        'patronymic': r'^[А-Яа-яЁё\s\-]*$',
        'phone': r'^\+?\d{10,15}$',
        'email': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
        'birthdate': r'^\d{4}-\d{2}-\d{2}$',
        'bio': r'^.{10,}$'
    }
    messages = {
        'last_name': "Фамилия должна содержать только буквы, пробелы и дефис.",
        'first_name': "Имя должно содержать только буквы, пробелы и дефис.",
        'patronymic': "Отчество должно содержать только буквы, пробелы и дефис (если указано).",
        'phone': "Телефон должен быть длиной от 10 до 15 цифр и может начинаться с '+'",
        'email': "Некорректный email. Пример: example@domain.com",
        'birthdate': "Дата рождения должна быть в формате YYYY-MM-DD.",
        'bio': "Биография должна содержать не менее 10 символов."
    }

    for field, pattern in patterns.items():
        if field in data and not re.match(pattern, data[field]):
            errors[field] = messages[field]

    if 'gender' not in data or data['gender'] not in ['male', 'female']:
        errors['gender'] = "Выберите пол."

    if 'languages' not in data or not data['languages']:
        errors['languages'] = "Выберите хотя бы один язык программирования."

    if 'contract' not in data or data['contract'] != 'on':
        errors['contract'] = "Необходимо подтвердить ознакомление с контрактом."

    return errors

# Сохранение данных в базу данных
def insert_user_data(connection, data):
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO applications (last_name, first_name, patronymic, phone, email, birthdate, gender, bio, contract)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['last_name'], data['first_name'], data['patronymic'],
            data['phone'], data['email'], data['birthdate'],
            data['gender'], data['bio'], data['contract']
        ))

        application_id = cursor.lastrowid

        language_ids = {
            'Pascal': 1, 'C': 2, 'C++': 3, 'JavaScript': 4, 'PHP': 5,
            'Python': 6, 'Java': 7, 'Haskel': 8, 'Clojure': 9, 'Prolog': 10,
            'Scala': 11, 'Go': 12
        }

        for language in data['languages']:
            if language in language_ids:
                cursor.execute("""
                    INSERT INTO application_languages (application_id, language_id)
                    VALUES (%s, %s)
                """, (application_id, language_ids[language]))

        connection.commit()
    except pymysql.Error as e:
        print(f"Ошибка при вставке данных: {e}")
    finally:
        cursor.close()

# Главная функция
if __name__ == "__main__":
    print("Content-Type: text/html; charset=utf-8\n")

    form = cgi.FieldStorage()
    cookie = http.cookies.SimpleCookie()
    cookie.load(os.environ.get('HTTP_COOKIE', ''))

    # Получение данных из формы
    data = {
        'last_name': form.getvalue('last_name', '').strip(),
        'first_name': form.getvalue('first_name', '').strip(),
        'patronymic': form.getvalue('patronymic', '').strip(),
        'phone': form.getvalue('phone', '').strip(),
        'email': form.getvalue('email', '').strip(),
        'birthdate': form.getvalue('birthdate', '').strip(),
        'gender': form.getvalue('gender', '').strip(),
        'languages': form.getlist('languages[]'),
        'bio': form.getvalue('bio', '').strip(),
        'contract': form.getvalue('contract', '') == 'on'
    }

    # Валидация данных
    errors = validate_form(data)

    if errors:
        # Сохранение ошибок в Cookies
        for field, message in errors.items():
            cookie[field + '_error'] = message
            cookie[field + '_error']['path'] = '/'
            cookie[field + '_error']['expires'] = 0  # Удаляем после использования

        # Перенаправление на форму с GET-запросом
        print("<html><body><script>window.location.href='index.html';</script></body></html>")
    else:
        # Удаление старых ошибок из Cookies
        for field in data.keys():
            if f'{field}_error' in cookie:
                del cookie[f'{field}_error']

        # Сохранение успешных данных в Cookies на год
        for field, value in data.items():
            cookie[field] = value
            cookie[field]['path'] = '/'
            cookie[field]['expires'] = (datetime.now() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Сохранение данных в базу данных
        connection = create_connection()
        if connection:
            insert_user_data(connection, data)
            connection.close()

        print("<h1>Данные успешно сохранены</h1>")
