import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "eac_system"),
    autocommit=True
)

def get_db():
    global db

    if not db.is_connected():
        db.reconnect(attempts=3, delay=2)

    return db