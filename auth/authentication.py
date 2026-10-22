
import os
import sqlite3
import hashlib

DB_NAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "users.db"
)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, 'user')
            """,
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

    try:
        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            WHERE email = ? AND password = ?
            """,
            (email, hash_password(password)),
        )
        return cursor.fetchone()

    finally:
        conn.close()
