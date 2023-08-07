import mysql.connector
import sqlite3
import os

def db_connection():
    db = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="scoreboard_admin",
        password="Sc0reb0@rd54Ev@",
        database="scoreboard_program"
    )
    return db

def sqlite_connection():
    database_file = 'data/scoreboard_program.db'
    sql_file = 'sqlite_scoreboard_setup.sql'
    db_exists = os.path.exists(database_file)
    conn = sqlite3.connect(database_file)

    # Create the database if it does not exist
    if not db_exists:
        try:
            cursor = conn.cursor()
            with open(sql_file, 'r') as f:
                sql_commands = f.read()
            cursor.executescript(sql_commands)
            cursor.close()
            print("Created database")
        except Exception as e:
            print(str(e))
            return
    
    print("Returned connection")
    return conn