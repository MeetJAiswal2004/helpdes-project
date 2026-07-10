from dotenv import load_dotenv 
import mysql.connector
import os

# Load credentials from the .env file into environment variables
load_dotenv()

# Opens a new MySQL connection using credentials from .env
# Called fresh each time so every function gets its own clean connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )