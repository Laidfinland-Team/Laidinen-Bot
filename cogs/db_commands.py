import psycopg2
from datetime import datetime
import re


def remove_special_characters(input_string):
    clean_string = re.sub(r"[^\w\s]", "", input_string)
    return clean_string


# Параметры подключения к базе данных
db_params = {
    'host': '127.0.0.1',
    'database': 'games',
    'user': 'postgres',
    'password': ''
}


def user_exists(user_id, game_link):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM games_now WHERE user_id = %s AND game_link = %s", (user_id, game_link))
        result = cursor.fetchall()
    conn.close()
    return bool(len(result))


def add_gamer(user_id, steam_link, game_link, exit_time, whole_time):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute('''
            INSERT INTO games_now (user_id,steam_link, game_link, exit_time,whole_time)
            VALUES (%s,%s, %s, %s,%s)
        ''', (user_id, steam_link, game_link, exit_time, whole_time))
    conn.commit()
    conn.close()


def get_gamers(game_link):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM games_now WHERE game_link = %s", (game_link,))
        result = cursor.fetchall()
    conn.close()
    return result


def get_exit_time(user_id):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT exit_time FROM games_now WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def get_whole_time(user_id):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT whole_time FROM games_now WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
    conn.close()
    return result


def get_user_by_game(game_link):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM games_now WHERE game_link = %s", (game_link,))
        result = cursor.fetchone()
    conn.close()
    return result


def delete_user(user_id):
    conn = psycopg2.connect(**db_params)
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM games_now WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
