
import sqlite3

from database.database import get_connection


def migrate_data():
    # Read the original SQLite database without modifying it.
    sqlite_conn = sqlite3.connect(
        "file:users.db?mode=ro",
        uri=True,
    )
    sqlite_conn.row_factory = sqlite3.Row

    try:
        users = sqlite_conn.execute(
            "SELECT id, name, email, password FROM users"
        ).fetchall()

        predictions = sqlite_conn.execute(
            """
            SELECT id, user_id, condition_name, result,
                   risk, timestamp, inputs_json
            FROM predictions
            """
        ).fetchall()

        print("Users found in SQLite:", len(users))
        print("Predictions found in SQLite:", len(predictions))

        with get_connection() as pg_conn:
            with pg_conn.cursor() as cursor:

                # Copy users without replacing existing accounts.
                for user in users:
                    cursor.execute(
                        """
                        INSERT INTO users (name, email, password)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (email) DO NOTHING
                        """,
                        (
                            user["name"],
                            user["email"],
                            user["password"],
                        ),
                    )

                # Find the PostgreSQL ID for each original email.
                for prediction in predictions:
                    old_user = sqlite_conn.execute(
                        "SELECT email FROM users WHERE id = ?",
                        (prediction["user_id"],),
                    ).fetchone()

                    if old_user is None:
                        print(
                            "Skipping prediction:",
                            prediction["id"],
                            "- original user not found",
                        )
                        continue

                    cursor.execute(
                        "SELECT id FROM users WHERE email = %s",
                        (old_user["email"],),
                    )
                    new_user = cursor.fetchone()

                    if new_user is None:
                        print(
                            "Skipping prediction:",
                            prediction["id"],
                            "- PostgreSQL user not found",
                        )
                        continue

                    # Avoid inserting the same prediction ID twice.
                    cursor.execute(
                        """
                        SELECT 1 FROM predictions WHERE id = %s
                        """,
                        (prediction["id"],),
                    )

                    if cursor.fetchone() is not None:
                        print(
                            "Prediction already exists; skipped:",
                            prediction["id"],
                        )
                        continue

                    cursor.execute(
                        """
                        INSERT INTO predictions
                        (id, user_id, condition_name, result,
                         risk, timestamp, inputs_json)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            prediction["id"],
                            new_user[0],
                            prediction["condition_name"],
                            prediction["result"],
                            prediction["risk"],
                            prediction["timestamp"],
                            prediction["inputs_json"],
                        ),
                    )

                # Keep the prediction ID sequence ready for new records.
                cursor.execute(
                    """
                    SELECT setval(
                        pg_get_serial_sequence('predictions', 'id'),
                        COALESCE((SELECT MAX(id) FROM predictions), 1),
                        EXISTS(SELECT 1 FROM predictions)
                    )
                    """
                )

        print("Migration completed successfully.")

    finally:
        sqlite_conn.close()


if __name__ == "__main__":
    migrate_data()
