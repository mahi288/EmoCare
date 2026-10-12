import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(override=True)

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "eac_system"),
    autocommit=True
)

def get_db():
    global db

    if not db.is_connected():
        db.reconnect(attempts=3, delay=2)

    return db