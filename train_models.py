
import os
import pickle
import shutil

import pandas as pd
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (accuracy_score, confusion_matrix, precision_score,
                             recall_score, f1_score, roc_auc_score)

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
    print(f'Rows: {len(data)}   Features: {X.shape[1]}   '
          f'Positive cases: {int(Y.sum())} ({Y.mean():.0%})')

    X_train, X_test, Y_train, Y_test = train_test_split(
        X, Y, test_size=0.2, stratify=Y, random_state=2)

    model.fit(X_train, Y_train)

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
        svm.SVC(kernel='linear', probability=True),
        'diabetes_model.sav')

    train_and_report(
        'Heart disease', 'heart.csv', 'target', [],
        LogisticRegression(max_iter=5000),
        'heart_disease_model.sav')

    train_and_report(
        "Parkinson's", 'parkinsons.csv', 'status', ['name'],
        svm.SVC(kernel='linear', probability=True),
        'parkinsons_model.sav')

    print('Done. Restart the Streamlit app to use the new models.')
