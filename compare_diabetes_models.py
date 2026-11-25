
import os
import joblib
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# Load dataset
data = pd.read_csv("dataset/diabetes.csv")

X = data.drop(columns=["Outcome"])
y = data["Outcome"]

# Define models for comparison
models = {
    "Linear SVM": make_pipeline(
        StandardScaler(),
        SVC(kernel="linear")
    ),

    "Class-Weighted SVM": make_pipeline(
        StandardScaler(),
        SVC(kernel="linear", class_weight="balanced")
    ),

    "Logistic Regression": make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=5000)
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42
    )
}

# Cross-validation
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=2
)

scoring = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "roc_auc"
]

print("\nDIABETES MODEL COMPARISON")
print("=" * 65)

for name, model in models.items():

    results = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=scoring
    )

    print(f"\n{name}")
    print("-" * 40)

    for metric in scoring:
        score = results["test_" + metric].mean()
        print(f"{metric.upper():12}: {score:.3f}")

# Train final Class-Weighted SVM
print("\nTRAINING FINAL CLASS-WEIGHTED SVM")
print("=" * 65)

final_model = make_pipeline(
    StandardScaler(),
    SVC(
        kernel="linear",
        class_weight="balanced",
        probability=True
    )
)

final_model.fit(X, y)

# Save separately without replacing existing model
os.makedirs("saved_models", exist_ok=True)

save_path = "saved_models/diabetes_model_weighted.sav"

joblib.dump(final_model, save_path)

print("\nClass-Weighted SVM saved successfully!")
print("Location:", save_path)
print("\nExisting diabetes_model.sav remains unchanged.")
