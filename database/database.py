import os
import sqlite3
import json
import hashlib

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Stores every prediction ever run, tied to the user who ran it, so
    # "previous records" persist across logins/restarts instead of only
    # living in st.session_state.history for the current session.
    # inputs_json holds every clinical parameter the user typed in
    # (BMI, Pregnancies, Glucose, etc. for Diabetes; age, cp, chol...
    # for Heart Disease; fo, jitter, shimmer... for Parkinson's) so the
    # full record -- not just the verdict -- can be reviewed/exported later.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            condition_name TEXT NOT NULL,
            result TEXT NOT NULL,
            risk TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            inputs_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    # Create a table to store patient details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_code TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            contact TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (doctor_id, patient_code),
            FOREIGN KEY (doctor_id) REFERENCES users (id)
        )
    """)

    # Add patient_id to existing prediction tables if missing
    cursor.execute("PRAGMA table_info(predictions)")
    existing_cols = [col[1] for col in cursor.fetchall()]

    if "patient_id" not in existing_cols:
        cursor.execute(
            "ALTER TABLE predictions ADD COLUMN patient_id INTEGER"
        )

    # Migration safety net: if predictions already existed from the
    # earlier version of this app (before inputs were tracked), add the
    # missing column instead of erroring out.
    cursor.execute("PRAGMA table_info(predictions)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if 'inputs_json' not in existing_cols:
        cursor.execute("ALTER TABLE predictions ADD COLUMN inputs_json TEXT")
    conn.commit()
    conn.close()


def save_prediction_to_db(
    user_id, condition, result, risk, timestamp, inputs, patient_id=None
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO predictions (
                user_id,
                condition_name,
                result,
                risk,
                timestamp,
                inputs_json,
                patient_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                condition,
                result,
                risk,
                timestamp,
                json.dumps(inputs),
                patient_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()

def get_user_predictions(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT condition_name, result, risk, timestamp, inputs_json FROM predictions "
        "WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    records = []
    for cond, result, risk, timestamp, inputs_json in rows:
        try:
            inputs = json.loads(inputs_json) if inputs_json else {}
        except (TypeError, ValueError):
            inputs = {}
        records.append({
            'condition': cond,
            'result': result,
            'risk': risk,
            'timestamp': timestamp,
            'inputs': inputs,
        })
    return records


def clear_user_predictions(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_all_users():
    """Return registered accounts without exposing passwords."""
    import sqlite3

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, email, role
            FROM users
            ORDER BY id ASC
            """
        )

        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()


def get_all_predictions():
    """Get prediction records from all users."""
    import sqlite3

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                predictions.id,
                users.name AS user_name,
                users.email AS user_email,
                predictions.condition_name,
                predictions.result,
                predictions.risk,
                predictions.timestamp
            FROM predictions
            JOIN users ON predictions.user_id = users.id
            ORDER BY predictions.timestamp DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()

def create_patient(doctor_id, patient_code, name, age, sex, contact=""):
    """Register a patient under a user or doctor account."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO patients (
                doctor_id, patient_code, name, age, sex, contact
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                doctor_id,
                patient_code.strip(),
                name.strip(),
                age,
                sex,
                contact.strip(),
            ),
        )
        conn.commit()
        return True, "Patient registered successfully."

    except sqlite3.IntegrityError:
        return False, "This patient code already exists in your account."

    finally:
        conn.close()

def get_patients(doctor_id):
    """Retrieve patients registered under a specific account."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, patient_code, name, age, sex, contact, created_at
            FROM patients
            WHERE doctor_id = ?
            ORDER BY name ASC
            """,
            (doctor_id,),
        )

        return [dict(row) for row in cursor.fetchall()]

    finally:
        conn.close()