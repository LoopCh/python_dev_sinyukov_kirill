# Проект: python_dev_sinyukov_kirill

## Пометки к заданию
В 4 пункте нужно сформировать dataset - comments, который содержит:
- логин пользователя, 
- заголовок поста (header) к которому он оставлял комментарии
- логин автора поста
- кол-во комментариев

Проблема в том, что по таблицам в базе данных logs, невозможно узнать к какому ПОСТУ сделал комментарий пользователь.
Известно лишь, то, что он сделал комментарий, можно узнать какие есть ПОСТЫ у него.
Но к какому ПОСТУ был сделан комментарий узнать невозможно.

Для решения этой проблемы, я добавил в таблицу `logs`, колонку `target_id`.
Это **ID конкретного поста или блога**, где произошло событие.
- Если пользователь оставил `comment` → `target_id` хранит `post.id`.
- Если действие в блоге (`create_post`, `delete_post`) → `target_id` хранит `blog.id`
- Если действие в `global` (`login`, `logout`) → `target_id` - **NULL**.


## Описание
Этот проект демонстрирует работу с базой данных PostgreSQL и получение двух dataset по двум endpoint. Он включает в себя: 
- Создание баз данных `author_database` и `logs_database`
- Создание таблиц `users`, `blog`, `post` для `author_database`, `logs`, `space_type`, `event_type` для `logs_database`
- Заполнение таблиц случайными данными (параметры подключений к базам находятся в файлах `populate_authors_db.py` и `populate_logs_db.py`).
- Получение dataset comments и dataset general по двум endpoint.

## Установка и запуск
1. Установите зависимости:
    ```bash
       pip install - r requirements.txt
    ```
2. Создать базы данных logs_database и authors_database, настроить свои параметры подключения, в файлах `conf_authors_db.json` и `conf_logs_bs.json`
3. Запустить два скрипта для генерации случайных данных `populate_authors_db.py` и `populate_logs_db.py`
4. Настроить параметры для uvicorn, в файле `conf_uvicorn.json`
5. Запустить main.py. Обратиться по адресу **http://<your_ip_addr>/comments/?login=your_login** для получения dataset comment и по адресу **http://<your_ip_addr>/general/?login=your_login** для получения dataset general.