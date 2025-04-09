import mysql.connector
from mysql.connector import Error
import os

env = os.getenv("DATABASE")


host, user, password, database = (
    os.getenv("HOST"),
    os.getenv("USER"),
    os.getenv("PASSWORD"),
    "testing_fin_track" if os.getenv("ENV") == "testing" else os.getenv("DATABASE"),
)


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None
