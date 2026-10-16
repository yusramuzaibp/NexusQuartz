import hashlib
from database.database import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
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
