import sys 
import os
import sqlite3
sys.path.insert(0, os.path.join(os.getcwd(), ''))




class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)

    def __del__(self):
        self.conn.close()
    
    def __str__(self):
        return self.db_name

