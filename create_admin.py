
import sqlite3
import getpass
from auth.authentication import DB_NAME, hash_password

name = "System Admin"
email = "admin@mdp.local"

print("Create the Multiple Disease Prediction System Admin account")
password = getpass.getpass("Enter a strong admin password: ")
confirm_password = getpass.getpass("Confirm admin password: ")

if len(password) < 12:
    print("Password must be at least 12 characters long.")
elif password != confirm_password:
    print("Passwords do not match.")
else:
    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )
        existing = cursor.fetchone()

        if existing:
            print("An account with this admin email already exists.")
        else:
            cursor.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, 'admin')
                """,
                (name, email, hash_password(password))
            )
            conn.commit()
            print("Admin account created successfully.")
            print("Email:", email)

    finally:
        conn.close()
