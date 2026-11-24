import hashlib
import hmac
import secrets

from database.database import db_cursor


# ================= PASSWORD CONFIGURATION =================

PBKDF2_ITERATIONS = 600_000
HASH_ALGORITHM = "sha256"


# ================= PASSWORD HASHING =================

def hash_password(password):
    """Create a salted PBKDF2 password hash."""

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )

    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}"
        f"${salt.hex()}${password_hash.hex()}"
    )


# ================= PASSWORD VERIFICATION =================

def verify_password(password, stored_hash):
    """Verify PBKDF2 and legacy SHA-256 password hashes."""

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
                iterations
            )

            return hmac.compare_digest(
                actual_hash,
                expected_hash
            )

        except (ValueError, TypeError):
            return False

    # Legacy SHA-256 verification
    legacy_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    return hmac.compare_digest(
        legacy_hash,
        stored_hash
    )


# ================= PASSWORD VALIDATION =================

def validate_password(password):

    errors = []

    if len(password) < 8:
        errors.append("Password must contain at least 8 characters.")

    if not any(char.isupper() for char in password):
        errors.append("Password must contain an uppercase letter.")

    if not any(char.islower() for char in password):
        errors.append("Password must contain a lowercase letter.")

    if not any(char.isdigit() for char in password):
        errors.append("Password must contain a number.")

    if not any(not char.isalnum() for char in password):
        errors.append("Password must contain a special character.")

    return errors


# ================= CREATE USER =================

def create_user(name, email, password):

    errors = validate_password(password)

    if errors:
        raise ValueError(
            "Password does not meet the requirements: "
            + ", ".join(errors)
        )

    name = name.strip()
    email = email.strip().lower()

    with db_cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO users
                (name, email, password, role)
            VALUES (%s, %s, %s, 'user')
            ON CONFLICT (email) DO NOTHING
            RETURNING id
            """,
            (
                name,
                email,
                hash_password(password)
            )
        )

        return cursor.fetchone() is not None


# ================= LOGIN USER =================

def login_user(email, password):

    email = email.strip().lower()

    with db_cursor() as cursor:

        cursor.execute(
            """
            SELECT id, name, email, role, password, status
            FROM users
            WHERE LOWER(email) = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return None

        user_id, name, email, role, stored_hash, status = user

        # Verify password
        if not verify_password(password, stored_hash):
            return None

        # Check account status
        status = (status or "").strip().lower()

        if status != "active":
            return {
                "account_status": status
            }

        # Upgrade legacy SHA-256 hashes
        if not stored_hash.startswith("pbkdf2_sha256$"):

            new_hash = hash_password(password)

            cursor.execute(
                """
                UPDATE users
                SET password = %s
                WHERE id = %s
                """,
                (new_hash, user_id)
            )

        # Preserve existing four-field login format
        return user_id, name, email, role


# ================= RESET PASSWORD =================

def reset_password(email, new_password):

    errors = validate_password(new_password)

    if errors:
        raise ValueError(
            "Password does not meet the requirements: "
            + ", ".join(errors)
        )

    email = email.strip().lower()
    new_hash = hash_password(new_password)

    with db_cursor() as cursor:

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE LOWER(email) = %s
            """,
            (new_hash, email)
        )

        return cursor.rowcount > 0


# ================= CHECK EMAIL EXISTS =================

def email_exists(email):

    email = email.strip().lower()

    with db_cursor() as cursor:

        cursor.execute(
            """
            SELECT 1
            FROM users
            WHERE LOWER(email) = %s
            LIMIT 1
            """,
            (email,)
        )

        return cursor.fetchone() is not None