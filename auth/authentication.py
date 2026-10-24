
import hashlib
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_auth_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from .env")

    return psycopg.connect(database_url)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(name, email, password):
    try:
        with get_auth_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.users
                        (name, email, password, role)
                    VALUES (%s, %s, %s, 'user')
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                    """,
                    (name, email, hash_password(password)),
                )

                return cursor.fetchone() is not None

    except psycopg.Error:
        raise


def login_user(email, password):
    with get_auth_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, role
                FROM public.users
                WHERE email = %s AND password = %s
                """,
                (email, hash_password(password)),
            )

            return cursor.fetchone()
