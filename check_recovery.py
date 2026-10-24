import json

with open("database/recovery_export.json", encoding="utf-8") as file:
    data = json.load(file)

print("Backup users:", len(data.get("users", [])))
print("Backup patients:", len(data.get("patients", [])))
print("Backup predictions:", len(data.get("predictions", [])))