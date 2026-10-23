<<<<<<< HEAD
=======

import os
import sqlite3
>>>>>>> dev1
import hashlib
from database.database import get_connection

<<<<<<< HEAD
=======
DB_NAME = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "users.db"
)
>>>>>>> dev1


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
<<<<<<< HEAD
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (name, email, password)
                    VALUES (%s, %s, %s)
                    """,
                    (name, email, hash_password(password)),
                )
        return True

    except Exception as e:
        # A duplicate email should return False.
        if "unique" in str(e).lower():
            return False
        raise


def login_user(email, password):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email
                FROM users
                WHERE email = %s AND password = %s
                """,
                (email, hash_password(password)),
            )
            user = cursor.fetchone()

    return user
=======
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
>>>>>>> dev1
