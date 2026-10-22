
import sqlite3
from database.database import DB_NAME, create_database

# Ensure the existing database and tables are initialized.
create_database()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

try:
    # 1. Add a role to existing users.
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]

    if "role" not in user_columns:
        cursor.execute(
            "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
        )
        print("Added role column. Existing users are regular users.")
    else:
        print("Role column already exists.")

    # 2. Create a patients table.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_code TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT,
            contact TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES users(id),
            UNIQUE (doctor_id, patient_code)
        )
    """)

    # 3. Link future prediction records to patients.
    cursor.execute("PRAGMA table_info(predictions)")
    prediction_columns = [
        column[1] for column in cursor.fetchall()
    ]

    if "patient_id" not in prediction_columns:
        cursor.execute(
            "ALTER TABLE predictions ADD COLUMN patient_id INTEGER"
        )
        print("Added patient_id column to predictions.")
    else:
        print("patient_id column already exists.")

    conn.commit()
    print("Database migration completed successfully.")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
