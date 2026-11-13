
import os
import pickle
import shutil

import pandas as pd
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, StratifiedKFold
from sklearn.metrics import (accuracy_score, confusion_matrix, precision_score,
                             recall_score, f1_score, roc_auc_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, 'dataset')
MODEL_DIR = os.path.join(BASE, 'saved_models')
os.makedirs(MODEL_DIR, exist_ok=True)


def train_and_report(name, csv_file, target_col, drop_cols, model, save_as):
    print('=' * 60)
    print(name.upper())
    print('=' * 60)

    # utf-8-sig handles the hidden BOM character at the start of heart.csv
    data = pd.read_csv(os.path.join(DATA_DIR, csv_file), encoding='utf-8-sig')
    X = data.drop(columns=drop_cols + [target_col])
    Y = data[target_col]
    if name == 'Diabetes':
        print("Diabetes feature order:", list(X.columns))
        print("Rows matching screenshot values:")
        print(data[
            (data["Pregnancies"] == 2) &
            (data["Glucose"] == 100) &
            (data["BloodPressure"] == 66) &
            (data["SkinThickness"] == 20) &
            (data["Insulin"] == 90) &
            (data["BMI"] == 32.9) &
            (data["DiabetesPedigreeFunction"] == 0.867) &
            (data["Age"] == 28)
      ])

    print(f'Rows: {len(data)}   Features: {X.shape[1]}   '
          f'Positive cases: {int(Y.sum())} ({Y.mean():.0%})')

    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, stratify=Y, random_state=2)
    print("Record 70 in training set:", 70 in X_train.index)
    print("Record 70 in test set:", 70 in X_test.index)

    model.fit(X_train, Y_train)
    if name == 'Diabetes':
        weighted_model = make_pipeline(
            StandardScaler(),
            svm.SVC(
            kernel='linear',
            probability=True,
            class_weight='balanced'
        )
    )

    weighted_model.fit(X_train, Y_train)

    weighted_predictions = weighted_model.predict(X_test)
    weighted_probabilities = weighted_model.predict_proba(X_test)[:, 1]
    weighted_auc = roc_auc_score(Y_test, weighted_probabilities)
    weighted_cm = confusion_matrix(Y_test, weighted_predictions)

    print("ROC-AUC:", weighted_auc)
    print("Confusion Matrix:")
    print(weighted_cm)

    print("\nCLASS-WEIGHTED SVM RESULTS")
    print("Accuracy:", accuracy_score(Y_test, weighted_predictions))
    print("Precision:", precision_score(Y_test, weighted_predictions))
    print("Recall:", recall_score(Y_test, weighted_predictions))
    print("F1 Score:", f1_score(Y_test, weighted_predictions))
    print("\n5-FOLD CROSS-VALIDATION COMPARISON")

    models_to_compare = {
        "Current Scaled SVM": model,
        "Class-Weighted SVM": weighted_model
    }

    scoring = ["accuracy", "precision", "recall", "f1"]

    for model_name, test_model in models_to_compare.items():
        scores = cross_validate(
            test_model,
            X,
            Y,
            cv=StratifiedKFold(
                n_splits=5,
                shuffle=True,
                random_state=2
            ),
            scoring=scoring
        )

        print(f"\n{model_name}")

        for metric in scoring:
            print(
                f"{metric.capitalize()}: "
                f"{scores['test_' + metric].mean():.3f}"
            )

    if name == 'Diabetes':
        sample = X.iloc[[70]]

        print("\nExact dataset record prediction:")
        print("Actual outcome:", Y.iloc[70])
        print("Model prediction:", model.predict(sample)[0])
        print("Model probabilities:", model.predict_proba(sample)[0])

    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    print(f'\nTrain accuracy: {accuracy_score(Y_train, model.predict(X_train)):.3f}')
    print(f'Test accuracy:  {accuracy_score(Y_test, pred):.3f}')
    print('\nConfusion matrix (rows = actual, columns = predicted):')
    print(confusion_matrix(Y_test, pred))
    print(f'\nPrecision: {precision_score(Y_test, pred):.3f}')
    print(f'Recall:    {recall_score(Y_test, pred):.3f}')
    print(f'F1 score:  {f1_score(Y_test, pred):.3f}')
    print(f'ROC-AUC:   {roc_auc_score(Y_test, proba):.3f}')

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
    scores = cross_val_score(model, X, Y, cv=cv, scoring='accuracy')
    print(f'\n5-fold CV accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})')

    # back up the old model before overwriting
    path = os.path.join(MODEL_DIR, save_as)
    if os.path.exists(path):
        shutil.copy(path, path + '.bak')
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    print(f'\nSaved -> saved_models/{save_as}\n')


if __name__ == '__main__':
    train_and_report(
    'Diabetes', 'diabetes.csv', 'Outcome', [],
    make_pipeline(
        StandardScaler(),
        svm.SVC(kernel='linear', probability=True)
    ),
    'diabetes_model.sav')

    #train_and_report(
     #   'Heart disease', 'heart.csv', 'target', [],
      #  LogisticRegression(max_iter=5000),
       # 'heart_disease_model.sav')

    #train_and_report(
     #   "Parkinson's", 'parkinsons.csv', 'status', ['name'],
      #  svm.SVC(kernel='linear', probability=True),
       # 'parkinsons_model.sav')

    print('Done. Restart the Streamlit app to use the new models.')
