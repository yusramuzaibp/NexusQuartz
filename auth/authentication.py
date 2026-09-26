import os
import sqlite3
import hashlib
import pandas as pd

DB_NAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "users.db"
)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
        (email, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()
    return user