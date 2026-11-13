
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    auc
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")
GRAPH_DIR = os.path.join(BASE_DIR, "evaluation_graphs")

os.makedirs(GRAPH_DIR, exist_ok=True)

models = [
    {
        "name": "Diabetes",
        "file": "diabetes.csv",
        "target": "Outcome",
        "drop": [],
        "model": "diabetes_model.sav"
    },
    {
        "name": "Heart Disease",
        "file": "heart.csv",
        "target": "target",
        "drop": [],
        "model": "heart_disease_model.sav"
    },
    {
        "name": "Parkinsons",
        "file": "parkinsons.csv",
        "target": "status",
        "drop": ["name"],
        "model": "parkinsons_model.sav"
    }
]

results = []

for item in models:

    print("\nEvaluating:", item["name"])

    data = pd.read_csv(
        os.path.join(DATA_DIR, item["file"]),
        encoding="utf-8-sig"
    )

    X = data.drop(columns=item["drop"] + [item["target"]])
    y = data[item["target"]]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=2
    )

    model_path = os.path.join(MODEL_DIR, item["model"])

    with open(model_path, "rb") as file:
        model = pickle.load(file)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    results.append({
        "Disease": item["name"],
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    # Confusion Matrix
    cm = confusion_matrix(y_test, predictions)

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm
    )

    display.plot(cmap="Blues")
    plt.title(item["name"] + " - Confusion Matrix")
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            GRAPH_DIR,
            item["name"].lower().replace(" ", "_") + "_confusion_matrix.png"
        )
    )
    plt.close()

    # ROC Curve
    fpr, tpr, thresholds = roc_curve(y_test, probabilities)
    roc_auc = auc(fpr, tpr)

    plt.figure()
    plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], linestyle="--")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(item["name"] + " - ROC Curve")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        os.path.join(
            GRAPH_DIR,
            item["name"].lower().replace(" ", "_") + "_roc_curve.png"
        )
    )
    plt.close()

# Performance Comparison
results_df = pd.DataFrame(results)

print("\nMODEL PERFORMANCE RESULTS")
print(results_df.to_string(index=False))

results_df.set_index("Disease").plot(
    kind="bar",
    ylim=(0, 1),
    figsize=(10, 6)
)

plt.title("Model Performance Comparison")
plt.ylabel("Score")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    os.path.join(GRAPH_DIR, "model_performance_comparison.png")
)
plt.close()

results_df.to_csv(
    os.path.join(GRAPH_DIR, "model_evaluation_results.csv"),
    index=False
)

print("\nEvaluation completed!")
print("Graphs saved in:", GRAPH_DIR)
