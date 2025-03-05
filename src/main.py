import json

import uvicorn
from fastapi import FastAPI, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import pandas as pd

PATH_TO_SETTINGS_AUTHORS_DB = "../settings/conf_authors_db.json"
PATH_TO_SETTINGS_LOGS_DB = "../settings/conf_logs_db.json"
PATH_TO_SETTINGS_UVICORN = "../settings/conf_uvicorn.json"

app = FastAPI()

def get_database_url(config: dict) -> str:
    return (
        f"postgresql+asyncpg://{config['DB_USER']}:{config['DB_PASSWORD']}"
        f"@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"
    )


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

params_authors_db = load_db_config(PATH_TO_SETTINGS_AUTHORS_DB)
params_logs_db = load_db_config(PATH_TO_SETTINGS_LOGS_DB)

authors_db_url = get_database_url(params_authors_db)
logs_db_url = get_database_url(params_logs_db)

engine_authors_db = create_async_engine(authors_db_url, echo=True)
engine_logs_db = create_async_engine(logs_db_url, echo=True)

async_session_maker_authors_db = async_sessionmaker(engine_authors_db, expire_on_commit=False)
async_session_maker_logs_db = async_sessionmaker(engine_logs_db, expire_on_commit=False)


async def get_authors_db():
    async with async_session_maker_authors_db() as session:
        yield session

async def get_logs_db():
    async with async_session_maker_logs_db() as session:
        yield session

async def get_data_from_table(db: AsyncSession, query):
    """
        Выполняет SQL-запрос к базе данных и возвращает результат в виде списка словарей.

        Функция выполняет переданный SQL-запрос с использованием асинхронной сессии базы данных.
        Результат запроса преобразуется в список словарей, где каждый словарь представляет строку
        таблицы с ключами, соответствующими именам колонок.

        :param db: Асинхронная сессия для работы с базой данных.
        :param query: SQL-запрос, который необходимо выполнить.

        :return: list[dict] Список словарей, где каждый словарь содержит данные одной строки результата.
          Ключи словаря соответствуют именам колонок в результате запроса.

        Пример использования:
            data = await get_data_from_table(session, "SELECT id, name FROM users")
            # Результат: [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        """
    result = await db.execute(text(query))
    data = result.mappings().all()
    return data

@app.get("/comments/")
async def get_dataset_comments(
        logs_db: AsyncSession = Depends(get_logs_db),
        authors_db: AsyncSession = Depends(get_authors_db),
        login: str = Query(...)
):
    """
       Получить и обработать данные о комментариях для конкретного пользователя по его логину.

       Основные шаги:

       1. Загружает данные из таблиц `logs`, `post` и `users`.
       2. Объединяет данные из этих таблиц для получения информации о комментариях.
       3. Фильтрует данные, оставляя только записи, связанные с комментариями (event_type_id == 2).
       4. Дополнительно фильтрует данные по логину пользователя.
       5. Группирует данные по логину комментатора, заголовку поста и логину автора поста, подсчитывая количество комментариев для каждой группы.

       :param logs_db: Сессия для работы с базой данных логов.
       :param authors_db: Сессия для работы с базой данных авторов.
       :param login: Логин пользователя, для которого нужно получить данные.

       :return: JSON-ответ, содержащий сгруппированные данные о комментариях в виде списка словарей.
       """
    df_logs = pd.DataFrame(await get_data_from_table(logs_db, 'SELECT * FROM logs'))
    df_post = pd.DataFrame(await get_data_from_table(authors_db, 'SELECT * FROM post'))
    df_users = pd.DataFrame(await get_data_from_table(authors_db, 'SELECT * FROM users'))

    df_logs_with_users = pd.merge(df_logs, df_users, left_on="user_id", right_on = "id", how="inner", suffixes=("_logs", "_users"))
    df_logs_users_posts = pd.merge(df_logs_with_users, df_post, left_on="target_id", right_on="id", how="inner")

    df_comments_only = df_logs_users_posts[df_logs_users_posts['event_type_id'] == 2] # оставляем только тех, кто оставил комментарии

    df_comments_with_authors = pd.merge(df_comments_only, df_users, left_on="author_id", right_on="id", how="inner", suffixes=("_commentator", "_author"))

    df_filtered_by_user = df_comments_with_authors[df_comments_with_authors['login_commentator'] == login]

    df_grouped = df_filtered_by_user.groupby(["login_commentator", "header", "login_author"]).size().reset_index(name='count_comments')

    print(df_grouped)

    return {"result": df_grouped.to_dict('records')}

@app.get("/general/")
async def get_dataset_general(
        logs_db: AsyncSession = Depends(get_logs_db),
        authors_db: AsyncSession = Depends(get_authors_db),
        login: str = Query(...)
):
    """
    Получить общую статистику действий пользователя по его логину.

    Основные шаги:

    1. Загружает данные из таблиц `logs` и `users`.
    2. Объединяет данные для получения информации о действиях пользователя.
    3. Преобразует поле `datetime` в формат даты.
    4. Группирует данные по дате и логину пользователя, подсчитывая количество:

   - входов в систему (event_type_id == 0),
   - выходов из системы (event_type_id == 4),
   - действий в блоге (space_type_id == 1).

    5. Фильтрует данные, удаляя даты, в которых не было активности (вход/выход/действия в блоге).
    6. Возвращает статистику только для указанного пользователя.

    :param logs_db: Сессия для работы с базой данных логов.
    :param authors_db: Сессия для работы с базой данных авторов.
    :param login: Логин пользователя, для которого нужно получить данные.

    :return: JSON-ответ, содержащий статистику действий пользователя в виде списка словарей.
    """
    df_logs = pd.DataFrame(await get_data_from_table(logs_db, 'SELECT * FROM logs'))
    df_users = pd.DataFrame(await get_data_from_table(authors_db, 'SELECT * FROM users'))

    df_merge_logs_users = pd.merge(df_logs, df_users, left_on='user_id', right_on = 'id', how="inner", suffixes=("_logs", "_user"))
    df_merge_logs_users["datetime"] = pd.to_datetime(df_merge_logs_users["datetime"]).dt.date

    df_grouped = df_merge_logs_users.groupby(["datetime", "login"]).agg(
        count_login=("event_type_id", lambda x: (x == 0).sum()),
        count_logout=("event_type_id", lambda x: (x == 4).sum()),
        count_actions_blog=("space_type_id", lambda x: (x == 1).sum()),
    ).reset_index()

    df_filtered = df_grouped[
        ~df_grouped[['count_login', 'count_logout', 'count_actions_blog']].eq(0).all(axis=1) # Убираем даты в которых было комментирование (т.е. login,logout,create_post,delete_post не было)
    ]

    print(df_filtered)

    return {"result": df_filtered[df_grouped['login'] == login].to_dict('records')}

if __name__ == '__main__':

    params = load_db_config(PATH_TO_SETTINGS_UVICORN)

    uvicorn.run(app, host=params['host'], port=params['port'])











