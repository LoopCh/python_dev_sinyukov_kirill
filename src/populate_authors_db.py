import psycopg2
from faker import Faker
import random
import json

PATH_TO_SETTINGS = "../settings/conf_authors_db.json"

COUNT_USERS = 10
COUNT_BLOG = 5
COUNT_POST = 20

def load_db_config(file_path):
    """
    Загружает конфигурацию базы данных из JSON-файла.

    :param file_path: Путь к файлу с настройками
    :return: Словарь с параметрами подключения
    """
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден.")
        return None
    except json.JSONDecodeError:
        print("Ошибка: Неверный формат JSON в файле.")
        return None

def populate_blog(conn):
    """
    Функция для заполнения случайными данными таблицы blog.
    :param conn: Подключение к базе данных.
    """
    cursor = conn.cursor()

    fake = Faker()

    blogs = []
    for blog_id in range(COUNT_BLOG):
        owner_id = random.randint(0, COUNT_USERS - 1)
        name = fake.company()
        description = fake.text()
        blogs.append((blog_id, owner_id, name, description))
    cursor.executemany("INSERT INTO blog (id, owner_id, name, description) VALUES (%s, %s, %s, %s)", blogs)


def populate_users(conn):
    """
    Функция для заполнения случайными данными таблицы users.
    :param conn: Подключение к базе данных.
    """
    cursor = conn.cursor()

    fake = Faker()

    users = []
    # заполняем таблицу users
    for _ in range(COUNT_USERS):
        user_id = _
        email = fake.email()
        login = fake.user_name()
        users.append((user_id, email, login))
    cursor.executemany("INSERT INTO users (id, email, login) VALUES (%s, %s, %s)", users)

    conn.commit()
    cursor.close()
    conn.close()



def populate_post(conn):
    """
    Функция для заполнения случайными данными таблицы post.
    :param conn: Подключение к базе данных.
    """
    cursor = conn.cursor()

    fake = Faker()

    posts = []
    for post_id in range(COUNT_POST):  # 20 постов
        header = fake.sentence()
        text = fake.paragraph()
        author_id = random.randint(0, COUNT_USERS - 1)
        blog_id = random.randint(0, COUNT_BLOG - 1)
        posts.append((post_id, header, text, author_id, blog_id))
    cursor.executemany("INSERT INTO post (id, header, text, author_id, blog_id) VALUES (%s, %s, %s, %s, %s)", posts)

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':

    params = load_db_config(PATH_TO_SETTINGS)

    conn = psycopg2.connect(
        dbname=params['DB_NAME'],
        user=params['DB_USER'],
        password=params['DB_PASSWORD'],
        host=params['DB_HOST'],
        port=params['DB_PORT']
    )

    populate_blog(conn)
    populate_users(conn)
    populate_post(conn)