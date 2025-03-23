#!/usr/bin/env python3

import cgi
import pymysql
import re
from http import cookies
import os

def create_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host='158.160.150.89',
            user='u68593',
            password='9258357',
            database='web_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return connection

def validate_form(data):
    errors = {}
    
    if not re.match(r'^[A-Za-zА-Яа-я\s]+$', data['last_name']):
        errors['last_name'] = "Фамилия должна содержать только буквы и пробелы."
    
    if not re.match(r'^[A-Za-zА-Яа-я\s]+$', data['first_name']):
        errors['first_name'] = "Имя должно содержать только буквы и пробелы."
    
    if data['patronymic'] and not re.match(r'^[A-Za-zА-Яа-я\s]+$', data['patronymic']):
        errors['patronymic'] = "Отчество должно содержать только буквы и пробелы."
    
    if not re.match(r'^\d{10,15}$', data['phone']):
        errors['phone'] = "Телефон должен содержать только цифры и быть длиной от 10 до 15 символов."
    
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', data['email']):
        errors['email'] = "Некорректный email. Пример: example@domain.com"
    
    if not data['birthdate']:
        errors['birthdate'] = "Укажите дату рождения."
    
    if data['gender'] not in ['male', 'female']:
        errors['gender'] = "Выберите пол."
    
    if not data['languages']:
        errors['languages'] = "Выберите хотя бы один язык программирования."
    
    if not data['bio'] or len(data['bio'].strip()) < 10:
        errors['bio'] = "Биография должна содержать не менее 10 символов."

    if not data['contract']:
        errors['contract'] = "Необходимо подтвердить ознакомление с контрактом."
    
    return errors

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

def set_cookie(key, value, max_age=None):
    cookie = cookies.SimpleCookie()
    cookie[key] = value
    if max_age:
        cookie[key]['max-age'] = max_age
    print(cookie.output())

def get_cookie(key):
    cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE', ''))
    if key in cookie:
        return cookie[key].value
    return None

def delete_cookie(key):
    set_cookie(key, '', max_age=0)

def generate_form(errors=None):
    print("Content-Type: text/html; charset=utf-8\n")
    print("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Форма</title>
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
        <form action="submit_form.py" method="POST">
    """)
    
    # Вывод ошибок, если они есть
    if errors:
        print("<h1>Ошибки:</h1>")
        for field, error in errors.items():
            print(f"<p style='color: red;'>{error}</p>")
    
    # Поля формы с подстановкой значений из Cookies
    print(f"""
        <label for="last_name">Фамилия:</label>
        <input type="text" id="last_name" name="last_name" maxlength="50" required value="{get_cookie('last_name') or ''}"><br>

        <label for="first_name">Имя:</label>
        <input type="text" id="first_name" name="first_name" maxlength="50" required value="{get_cookie('first_name') or ''}"><br>

        <label for="patronymic">Отчество:</label>
        <input type="text" id="patronymic" name="patronymic" maxlength="50" value="{get_cookie('patronymic') or ''}"><br>

        <label for="phone">Телефон:</label>
        <input type="tel" id="phone" name="phone" required value="{get_cookie('phone') or ''}"><br>

        <label for="email">E-mail:</label>
        <input type="email" id="email" name="email" required value="{get_cookie('email') or ''}"><br>

        <label for="birthdate">Дата рождения:</label>
        <input type="date" id="birthdate" name="birthdate" required value="{get_cookie('birthdate') or ''}"><br>

        <label>Пол:</label>
        <label for="male">Мужской</label>
        <input type="radio" id="male" name="gender" value="male" required {'checked' if get_cookie('gender') == 'male' else ''}>
        <label for="female">Женский</label>
        <input type="radio" id="female" name="gender" value="female" required {'checked' if get_cookie('gender') == 'female' else ''}><br>

        <label for="languages">Любимый язык программирования:</label>
        <select id="languages" name="languages[]" multiple required>
    """)
    
    languages = ['Pascal', 'C', 'C++', 'JavaScript', 'PHP', 'Python', 'Java', 'Haskel', 'Clojure', 'Prolog', 'Scala', 'Go']
    selected_languages = get_cookie('languages')
    if selected_languages:
        selected_languages = selected_languages.split(',')
    else:
        selected_languages = []
    
    for language in languages:
        selected = 'selected' if language in selected_languages else ''
        print(f"<option value='{language}' {selected}>{language}</option>")
    
    print("""
        </select><br>

        <label for="bio">Биография:</label>
        <textarea id="bio" name="bio" rows="4" required>{get_cookie('bio') or ''}</textarea><br>

        <label for="contract">С контрактом ознакомлен(а)</label>
        <input type="checkbox" id="contract" name="contract" required {'checked' if get_cookie('contract') == 'on' else ''}><br>

        <button type="submit">Сохранить</button>
        </form>
    </body>
    </html>
    """)

if __name__ == "__main__":
    form = cgi.FieldStorage()
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
        'contract': form.getvalue('contract') == 'on'
    }

    errors = validate_form(data)
    if errors:
        for key, value in data.items():
            set_cookie(key, value)
        for key, error in errors.items():
            set_cookie(f'error_{key}', error)
        generate_form(errors)
    else:
        connection = create_connection()
        if connection:
            insert_user_data(connection, data)
            connection.close()
            for key, value in data.items():
                set_cookie(key, value, max_age=31536000)  # 1 год
            generate_form()
