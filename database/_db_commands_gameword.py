import re
import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *
from _con_message_base import *

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



def add_word(table_name, user_id, word):
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Добавление слова в таблицу
                add_word_query = "INSERT INTO {} (user_id, word) VALUES ({}, '{}')"
                try:
                    cursor.execute(add_word_query.format(table_name, user_id, word))
                    conn.commit()
                    info("Word added")
                except psycopg2.Error as e:
                    conn.rollback()
                    error(f"Error while adding word: {e}")
    except psycopg2.Error as e:
        error(f"Connecting to the database: {e}")


def get_last_word(table_name):
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Получение последнего значения из столбца word
                get_last_word_query = f"SELECT word FROM {table_name} ORDER BY id DESC LIMIT 1"
                try:
                    cursor.execute(get_last_word_query)
                    last_word = cursor.fetchone()
                    if last_word:
                        return last_word[0]
                    else:
                        return None
                except psycopg2.Error as e:
                    error(f"Error while getting last word value: {e}")
                    return None
    except psycopg2.Error as e:
        error(f"Connecting to the database: {e}")
        return None
    
def get_word_author(table_name, word):
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Получение user_id по слову из таблицы
                get_word_author_query = f"SELECT user_id FROM {table_name} WHERE word = %s"
                cursor.execute(get_word_author_query, (word,))
                result = cursor.fetchone()

                if result:
                    user_id = result[0]
                    return user_id
                else:
                    return None
    except psycopg2.Error as e:
        error(f"Error while getting word author: {e}")
        return None


def check_word_exists(table_name, word):
    try:
        with psycopg2.connect(**db_params) as conn:
            with conn.cursor() as cursor:
                # Проверка существования слова в таблице
                check_word_query = f"SELECT COUNT(*) FROM {table_name} WHERE word = %s"
                cursor.execute(check_word_query, (word,))
                word_count = cursor.fetchone()[0]
                return word_count > 0
    except psycopg2.Error as e:
        error(f"Error while checking word existence: {e}")
        return False


def check_for_table_exist(table_name):
    try:
        with psycopg2.connect(**db_params) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                # Проверка существования таблицы
                check_table_exist = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}')"
                try:
                    cursor.execute(check_table_exist)
                    exists = cursor.fetchone()[0]
                    return exists
                except psycopg2.Error as e:
                    error(f"Error while checking for table existence: {e}")
                    return None
                
    except psycopg2.Error as e:
        error(f"Connecting to the database: {e}")
        return None

                   
                   
def create_actual_game_table():     
    try:
            with psycopg2.connect(**db_params) as conn:
                conn.autocommit = True
                with conn.cursor() as cursor:
                    # Create the tables
                    create_table_query = '''
                    CREATE TABLE actual_game (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL, 
                        word TEXT NOT NULL
                    )
                    '''
                    try:
                        cursor.execute(create_table_query)
                        conn.commit()
                    except Exception as e:
                        match e:
                            case psycopg2.errors.DuplicateTable:
                                error("Table already exists.")
                            case psycopg2.errors.InFailedSqlTransaction:
                                error(f"Error while creating table: {e}")
                            case _:
                                error(f"Error while creating table: {e}")
                    else:
                        info("Users table created successfully.")
    except Exception as e:
        match e:
            case psycopg2.Error:
                error(f"Connecting to the database: {e}")
            case _: 
                error(f"Connecting to the database: {e}")