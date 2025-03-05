import psycopg2
from faker import Faker
import random
import json
from datetime import datetime

PATH_TO_SETTINGS = "../settings/conf_logs_db.json"

COUNT_LOGS = 250
COUNT_USERS = 10

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

def populate_space_type(conn):
    """
    Функция для заполнения случайными данными таблицы space_type.
    :param conn: Подключение к базе данных.
    """
    cursor = conn.cursor()
    space_type_values = ["global", "post", "commit"]
    space_type = [(i, value) for i, value in enumerate(space_type_values)]

    cursor.executemany("INSERT INTO space_type(id, name) VALUES (%s, %s)", space_type)

    conn.commit()
    cursor.close()
    conn.close()

def populate_event_type(conn):
    """
    Функция для заполнения случайными данными таблицы event_type.
    :param conn: Подключение к базе данных.
    """
    cursor = conn.cursor()
    event_type_values = ["login", "comment", "create_post", "delete_post", "logout"]
    event_type = [(i, value) for i, value in enumerate(event_type_values)]

    cursor.executemany("INSERT INTO event_type(id, name) VALUES (%s, %s)", event_type)

    conn.commit()
    cursor.close()
    conn.close()

def populate_logs(conn):
    """
    Функция для заполнения случайными данными таблицы event_type.
    :param conn: Подключение к базе данных.
    """
    cursor = conn.cursor()
    fake = Faker()

    logs = []
    for _ in range(COUNT_LOGS):
        logs_id = _
        date_time = fake.date_time_between_dates(datetime(2025, 1, 1), datetime(2025, 12, 31))
        user_id = random.randint(0, COUNT_USERS - 1)

        space_type_id = random.randint(0, 2)
        space_type_id_to_event_type_id = {
            0: random.choice([0, 4]),
            1: random.choice([2, 3]),
            2: 1
        }
        event_type_id = space_type_id_to_event_type_id[space_type_id]

        space_type_id_to_target_id = {
            0: None,
            1: random.randint(0, 5),
            2: random.randint(0, 20)
        }
        target_id = space_type_id_to_target_id[space_type_id]

        logs.append((logs_id, date_time, user_id, space_type_id, event_type_id, target_id))

    cursor.executemany("INSERT INTO logs(id, datetime, user_id, space_type_id, event_type_id, target_id) VALUES (%s, %s, %s, %s, %s, %s)", logs)

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":

    params = load_db_config(PATH_TO_SETTINGS)

    conn = psycopg2.connect(
        dbname=params['DB_NAME'],
        user=params['DB_USER'],
        password=params['DB_PASSWORD'],
        host=params['DB_HOST'],
        port=params['DB_PORT']
    )
    populate_logs(conn)
