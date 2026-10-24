
import json

EXPORT_PATH = "database/recovery_export.json"

with open(EXPORT_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

print("USERS")
for user in data["users"]:
    print(
        f"ID: {user['id']} | "
        f"Email: {user['email']} | "
        f"Role: {user['role']}"
    )

print("\nPATIENTS")
for patient in data["patients"]:
    print(
        f"ID: {patient['id']} | "
        f"Patient code: {patient['patient_code']}"
    )

print("\nPREDICTION COUNTS")
counts = {}
for prediction in data["predictions"]:
    condition = prediction["condition_name"]
    counts[condition] = counts.get(condition, 0) + 1

for condition, count in sorted(counts.items()):
    print(f"{condition}: {count}")

print(f"\nTotal predictions: {len(data['predictions'])}")
