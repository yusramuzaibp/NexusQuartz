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
    # Migration safety net: if predictions already existed from the
    # earlier version of this app (before inputs were tracked), add the
    # missing column instead of erroring out.
    cursor.execute("PRAGMA table_info(predictions)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if 'inputs_json' not in existing_cols:
        cursor.execute("ALTER TABLE predictions ADD COLUMN inputs_json TEXT")
    conn.commit()
    conn.close()

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

def save_prediction_to_db(user_id, condition, result, risk, timestamp, inputs):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (user_id, condition_name, result, risk, timestamp, inputs_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, condition, result, risk, timestamp, json.dumps(inputs)),
    )
    conn.commit()
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

