import mysql.connector

def db_connection():
    db = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="if_admin",
        password="Sc0reb0@rd54Ev@",
        database="ipswich_futsal_fixtures"
    )
    return db

