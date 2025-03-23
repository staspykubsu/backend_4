#!/usr/bin/env python3

import cgi
import http.cookies
import re
import pymysql
from datetime import datetime, timedelta
import os

# Создание подключения к базе данных
def create_connection():
    try:
        return pymysql.connect(
            host='130.193.44.145',
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

    if 'contract' not in data or not data['contract']:
        errors['contract'] = "Необходимо подтвердить ознакомление с контрактом."

    return errors

# Генерация HTML-формы
def generate_html_form(data, errors):
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Форма</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <form action="" method="POST">
            <label for="last_name">Фамилия:</label>
            <input type="text" id="last_name" name="last_name" maxlength="50" required
                   value="{last_name}" class="{last_name_error_class}">
            <span class="error-message">{last_name_error}</span><br>

            <label for="first_name">Имя:</label>
            <input type="text" id="first_name" name="first_name" maxlength="50" required
                   value="{first_name}" class="{first_name_error_class}">
            <span class="error-message">{first_name_error}</span><br>

            <label for="patronymic">Отчество:</label>
            <input type="text" id="patronymic" name="patronymic" maxlength="50"
                   value="{patronymic}" class="{patronymic_error_class}">
            <span class="error-message">{patronymic_error}</span><br>

            <label for="phone">Телефон:</label>
            <input type="tel" id="phone" name="phone" required
                   value="{phone}" class="{phone_error_class}">
            <span class="error-message">{phone_error}</span><br>

            <label for="email">E-mail:</label>
            <input type="email" id="email" name="email" required
                   value="{email}" class="{email_error_class}">
            <span class="error-message">{email_error}</span><br>

            <label for="birthdate">Дата рождения:</label>
            <input type="date" id="birthdate" name="birthdate" required
                   value="{birthdate}" class="{birthdate_error_class}">
            <span class="error-message">{birthdate_error}</span><br>

            <label>Пол:</label>
            <label for="male">Мужской</label>
            <input type="radio" id="male" name="gender" value="male" required {male_checked}>
            <label for="female">Женский</label>
            <input type="radio" id="female" name="gender" value="female" required {female_checked}>
            <span class="error-message">{gender_error}</span><br>

            <label for="languages">Любимый язык программирования:</label>
            <select id="languages" name="languages[]" multiple required>
                <option value="Pascal" {pascal_selected}>Pascal</option>
                <option value="C" {c_selected}>C</option>
                <option value="C++" {cpp_selected}>C++</option>
                <option value="JavaScript" {javascript_selected}>JavaScript</option>
                <option value="PHP" {php_selected}>PHP</option>
                <option value="Python" {python_selected}>Python</option>
                <option value="Java" {java_selected}>Java</option>
                <option value="Haskel" {haskel_selected}>Haskel</option>
                <option value="Clojure" {clojure_selected}>Clojure</option>
                <option value="Prolog" {prolog_selected}>Prolog</option>
                <option value="Scala" {scala_selected}>Scala</option>
                <option value="Go" {go_selected}>Go</option>
            </select>
            <span class="error-message">{languages_error}</span><br>

            <label for="bio">Биография:</label>
            <textarea id="bio" name="bio" rows="4" required class="{bio_error_class}">{bio}</textarea>
            <span class="error-message">{bio_error}</span><br>

            <label for="contract">С контрактом ознакомлен(а)</label>
            <input type="checkbox" id="contract" name="contract" required {contract_checked}>
            <span class="error-message">{contract_error}</span><br>

            <button type="submit">Сохранить</button>
        </form>
    </body>
    </html>
    """

    # Подготовка данных для подстановки
    context = {
        'last_name': data.get('last_name', ''),
        'first_name': data.get('first_name', ''),
        'patronymic': data.get('patronymic', ''),
        'phone': data.get('phone', ''),
        'email': data.get('email', ''),
        'birthdate': data.get('birthdate', ''),
        'male_checked': 'checked' if data.get('gender') == 'male' else '',
        'female_checked': 'checked' if data.get('gender') == 'female' else '',
        'pascal_selected': 'selected' if 'Pascal' in data.get('languages', []) else '',
        'c_selected': 'selected' if 'C' in data.get('languages', []) else '',
        'cpp_selected': 'selected' if 'C++' in data.get('languages', []) else '',
        'javascript_selected': 'selected' if 'JavaScript' in data.get('languages', []) else '',
        'php_selected': 'selected' if 'PHP' in data.get('languages', []) else '',
        'python_selected': 'selected' if 'Python' in data.get('languages', []) else '',
        'java_selected': 'selected' if 'Java' in data.get('languages', []) else '',
        'haskel_selected': 'selected' if 'Haskel' in data.get('languages', []) else '',
        'clojure_selected': 'selected' if 'Clojure' in data.get('languages', []) else '',
        'prolog_selected': 'selected' if 'Prolog' in data.get('languages', []) else '',
        'scala_selected': 'selected' if 'Scala' in data.get('languages', []) else '',
        'go_selected': 'selected' if 'Go' in data.get('languages', []) else '',
        'bio': data.get('bio', ''),
        'contract_checked': 'checked' if data.get('contract') else '',
        'last_name_error': errors.get('last_name', ''),
        'first_name_error': errors.get('first_name', ''),
        'patronymic_error': errors.get('patronymic', ''),
        'phone_error': errors.get('phone', ''),
        'email_error': errors.get('email', ''),
        'birthdate_error': errors.get('birthdate', ''),
        'gender_error': errors.get('gender', ''),
        'languages_error': errors.get('languages', ''),
        'bio_error': errors.get('bio', ''),
        'contract_error': errors.get('contract', ''),
        'last_name_error_class': 'error' if 'last_name' in errors else '',
        'first_name_error_class': 'error' if 'first_name' in errors else '',
        'patronymic_error_class': 'error' if 'patronymic' in errors else '',
        'phone_error_class': 'error' if 'phone' in errors else '',
        'email_error_class': 'error' if 'email' in errors else '',
        'birthdate_error_class': 'error' if 'birthdate' in errors else '',
        'bio_error_class': 'error' if 'bio' in errors else ''
    }

    return html.format(**context)

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
            'Pascal': 1,
            'C': 2,
            'C++': 3,
            'JavaScript': 4,
            'PHP': 5,
            'Python': 6,
            'Java': 7,
            'Haskel': 8,
            'Clojure': 9,
            'Prolog': 10,
            'Scala': 11,
            'Go': 12
        }

        for language in data['languages']:
            language_id = language_ids.get(language)
            if language_id:
                cursor.execute("""
                    INSERT INTO application_languages (application_id, language_id)
                    VALUES (%s, %s)
                """, (application_id, language_id))
        
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
        'contract': 'contract' in form  # Проверяем наличие ключа 'contract'
    }

    # Если данные пустые, берем их из Cookies
    if not any(data.values()):
        for field in data.keys():
            if field in cookie:
                data[field] = cookie[field].value

    # Определяем тип запроса
    request_method = os.environ.get('REQUEST_METHOD', '')

    if request_method == 'POST':
        # Валидация данных
        errors = validate_form(data)

        if errors:
            # Сохранение ошибок в Cookies
            for field, message in errors.items():
                cookie[field + '_error'] = message
                cookie[field + '_error']['path'] = '/'
                cookie[field + '_error']['expires'] = 0  # Удаляем после использования

            # Выводим форму с ошибками
            print(generate_html_form(data, errors))
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
    else:
        # GET-запрос: показываем форму с данными из Cookies
        print(generate_html_form(data, {}))
