
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

models = {
    "Diabetes": "diabetes_model.sav",
    "Heart Disease": "heart_disease_model.sav",
    "Parkinson's": "parkinsons_model.sav",
}

for name, filename in models.items():
    path = os.path.join(MODEL_DIR, filename)

    print(f"\nChecking {name}...")

    try:
        with open(path, "rb") as file:
            model = pickle.load(file)

        print(f"SUCCESS: {name} model loaded.")
        print(f"Model type: {type(model).__name__}")

    except FileNotFoundError:
        print(f"FAILED: File not found: {filename}")

    except Exception as error:
        print(f"FAILED: {type(error).__name__}: {error}")
