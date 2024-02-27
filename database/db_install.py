import psycopg2
import json

import sys, os; sys.path.insert(0, os.path.join(os.getcwd(), ''))

from __init__ import *

from colorama import Fore, Back, Style
from db_config import host, user, password, db_name, port
from time import sleep
PATH_TO_SQL_FILE = "PyAlc/database/tables.sql"
PATH_TO_JSON_FILE = "PyAlc/database/tables.json"

"""
CREATE TABLE IF NOT EXISTS users # SQL команда для создания таблицы если она не существует
""" 


try:
    conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password
)

    # Create a new database
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {db_name}")
    except Exception as e:
        match e:
            case psycopg2.errors.DuplicateDatabase:
                warning("Database already exists.")
            case psycopg2.errors.InFailedSqlTransaction:
                error(f"Error while creating database: {e}")
            case _:
                error(f"Error while creating database: {e}")
    else:
        info("Database created successfully.")

    # Close the cursor and connection
    cur.close()
    conn.close()


        # Connect to the newly created database
except Exception as e:
    match e:
        case psycopg2.Error:
            error(f"Connecting to the database: {e}")
        case _: 
            error(f"Connecting to the database: {e}")
    cur.close()
    conn.close()

try:
        with psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name,
            port=port
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                # Create the tables
                create_table_query = '''
                CREATE TABLE games_now (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL, 
                    steam_link VARCHAR(255) NOT NULL,
                    game_link VARCHAR(255) NOT NULL,
                    exit_time TEXT NOT NULL,
                    whole_time TEXT NOT NULL
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
            
try:
        with psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=db_name,
            port=port
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                # Create the tables
                create_table_query = '''
                CREATE TABLE gameword_users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL, 
                    found_words BIGINT NOT NULL,
                    spelling_mistakes BIGINT NOT NULL,
                    last_three_worlds TEXT NOT NULL
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