import re
import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

from database.db_config import host, db_name, user, password

def remove_special_characters(input_string):
    # Удаляет специальные символы из строки
    clean_string = re.sub(r"[^\w\s]", "", input_string)
    return clean_string


# Параметры подключения к базе данных
db_params = {
    'host': host,
    'database': db_name ,
    'user': user,
    'password': password
}


def user_exists(user_id, game_link):
    # Проверяет, существует ли пользователь с указанным ID и ссылкой на игру
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM games_now WHERE user_id = %s AND game_link = %s", (user_id, game_link))
        result = cursor.fetchall()
    conn.close()
    return bool(len(result))


def add_gamer(user_id, steam_link, game_link, exit_time, whole_time):
    # Добавляет игрока в базу данных
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute('''
            INSERT INTO games_now (user_id,steam_link, game_link, exit_time,whole_time)
            VALUES (%s,%s, %s, %s,%s)
        ''', (user_id, steam_link, game_link, exit_time, whole_time))
    conn.commit()
    conn.close()


def get_gamers(game_link):
    # Возвращает список пользователей, играющих в указанную игру
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM games_now WHERE game_link = %s", (game_link,))
        result = cursor.fetchall()
    conn.close()
    return result


def get_exit_time(user_id):
    # Возвращает время выхода пользователя из игры
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT exit_time FROM games_now WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def get_whole_time(user_id):
    # Возвращает общее время игры пользователя
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT whole_time FROM games_now WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def get_user_by_game(game_link):
    # Возвращает пользователя по ссылке на игру
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM games_now WHERE game_link = %s", (game_link,))
        result = cursor.fetchone()
    conn.close()
    return result


def delete_user(user_id):
    # Удаляет пользователя из базы данных
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM games_now WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
