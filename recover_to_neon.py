
import json
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

EXPORT_PATH = "database/recovery_export.json"


def recover():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing from .env")

    with open(EXPORT_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    if (
        len(data["users"]) != 3
        or len(data["patients"]) != 1
        or len(data["predictions"]) != 14
    ):
        raise RuntimeError("Export counts are incorrect. Cancelled.")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM public.users),
                    (SELECT COUNT(*) FROM public.patients),
                    (SELECT COUNT(*) FROM public.predictions)
            """)
            counts = cur.fetchone()

            if counts != (0, 0, 0):
                raise RuntimeError(
                    f"Neon is not empty: {counts}. Import cancelled."
                )

            # Restore users first.
            for user in data["users"]:
                cur.execute("""
                    INSERT INTO public.users
                        (id, name, email, password, role)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    user["id"], user["name"], user["email"],
                    user["password"], user["role"]
                ))

            # Restore patients next.
            for patient in data["patients"]:
                cur.execute("""
                    INSERT INTO public.patients
                        (id, doctor_id, patient_code, name,
                         age, sex, contact, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    patient["id"], patient["doctor_id"],
                    patient["patient_code"], patient["name"],
                    patient["age"], patient["sex"],
                    patient.get("contact"), patient["created_at"]
                ))

            # Restore predictions.
            for prediction in data["predictions"]:
                cur.execute("""
                    INSERT INTO public.predictions
                        (id, user_id, condition_name, result,
                         risk, timestamp, inputs_json, patient_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    prediction["id"], prediction["user_id"],
                    prediction["condition_name"], prediction["result"],
                    prediction["risk"], prediction["timestamp"],
                    prediction.get("inputs_json"),
                    prediction.get("patient_id")
                ))

            # Synchronize ID generators for future inserts.
            for table in ("users", "patients", "predictions"):
                cur.execute(
                    "SELECT setval("
                    "pg_get_serial_sequence(%s, 'id'), "
                    "COALESCE((SELECT MAX(id) FROM public."
                    + table + "), 1), "
                    "EXISTS (SELECT 1 FROM public." + table + ")"
                    ")",
                    (f"public.{table}",)
                )

            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM public.users),
                    (SELECT COUNT(*) FROM public.patients),
                    (SELECT COUNT(*) FROM public.predictions)
            """)
            final_counts = cur.fetchone()

            if final_counts != (3, 1, 14):
                raise RuntimeError(
                    f"Unexpected counts: {final_counts}"
                )

    print("Recovery completed successfully!")
    print("Users:", final_counts[0])
    print("Patients:", final_counts[1])
    print("Predictions:", final_counts[2])


if __name__ == "__main__":
    recover()
