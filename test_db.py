from database.db import db

if db.is_connected():
    print("Database Connected Successfully!")