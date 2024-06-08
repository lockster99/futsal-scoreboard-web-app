from model.db import sqlite_connection
import os

conn = sqlite_connection()
print(conn)
conn.close()
#os.remove("data/scoreboard_program.db")

