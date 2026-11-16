
import os
import hashlib
import hmac
import secrets
import string

import psycopg
from dotenv import load_dotenv

load_dotenv()

# PBKDF2 configuration
PBKDF2_ITERATIONS = 600_000
HASH_ALGORITHM = "sha256"


def get_auth_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from .env")

    return psycopg.connect(database_url)


def validate_password(password):
    """
    Return a list of password requirements that are not satisfied.
    An empty list means the password is valid.
    """
    errors = []

    if len(password) < 8:
        errors.append("At least 8 characters")

    if not any(ch.isupper() for ch in password):
        errors.append("At least one uppercase letter (A-Z)")

    if not any(ch.islower() for ch in password):
        errors.append("At least one lowercase letter (a-z)")

    if not any(ch.isdigit() for ch in password):
        errors.append("At least one number (0-9)")

    if not any(ch in string.punctuation for ch in password):
        errors.append("At least one special character (e.g. @, #, $)")

    return errors


def hash_password(password):
    """Create a salted PBKDF2 password hash."""
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}"
        f"${salt.hex()}${password_hash.hex()}"
    )


def verify_password(password, stored_hash):
    """Verify both new PBKDF2 and existing SHA-256 hashes."""

    if stored_hash.startswith("pbkdf2_sha256$"):
        try:
            algorithm, iterations, salt_hex, hash_hex = (
                stored_hash.split("$")
            )

            if algorithm != "pbkdf2_sha256":
                return False

            iterations = int(iterations)
            if not 1 <= iterations <= 10_000_000:
                return False

            salt = bytes.fromhex(salt_hex)
            expected_hash = bytes.fromhex(hash_hex)

            actual_hash = hashlib.pbkdf2_hmac(
                HASH_ALGORITHM,
                password.encode("utf-8"),
                salt,
                iterations,
            )

            return hmac.compare_digest(
                actual_hash,
                expected_hash,
            )

        except (ValueError, TypeError):
            return False

    # Legacy SHA-256 verification for existing accounts
    legacy_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    return hmac.compare_digest(legacy_hash, stored_hash)


def create_user(name, email, password):
    # Enforce password requirements at the backend level
    errors = validate_password(password)

    if errors:
        raise ValueError(
            "Password does not meet the requirements: "
            + ", ".join(errors)
        )

    name = name.strip()
    email = email.strip().lower()

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
    email = email.strip().lower()

    with get_auth_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, role, password
                FROM public.users
                WHERE email = %s
                """,
                (email,),
            )

            user = cursor.fetchone()

            if not user:
                return None

            user_id, name, email, role, stored_hash = user

            if not verify_password(password, stored_hash):
                return None

            # Upgrade legacy SHA-256 hashes after successful login
            if not stored_hash.startswith("pbkdf2_sha256$"):
                new_hash = hash_password(password)

                cursor.execute(
                    """
                    UPDATE public.users
                    SET password = %s
                    WHERE id = %s
                    """,
                    (new_hash, user_id),
                )

            # Preserve the existing return format:
            # user[0] = id
            # user[1] = name
            # user[2] = email
            # user[3] = role
            return user_id, name, email, role
