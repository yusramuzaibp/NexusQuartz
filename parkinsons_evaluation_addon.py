# ============================================================
# ADD THIS to "Multiple disease prediction system - Parkinsons.ipynb"
# Paste as a new cell after your existing accuracy_score cells.
# Uses `model`, `X`, `Y`, `X_train`, `X_test`, `Y_train`, `Y_test`
# which already exist earlier in your notebook.
#
# ALSO CHANGE your model creation line to:
#     model = svm.SVC(kernel='linear', probability=True)
# (ROC-AUC needs predicted probabilities, not just 0/1 labels)
#
# NOTE: this dataset is imbalanced (147 positive / 195 total), so
# accuracy alone is especially misleading here -- this is exactly
# the case that motivates adding these metrics.
# ============================================================

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (confusion_matrix, classification_report,
                              precision_score, recall_score, f1_score, roc_auc_score)

Y_test_pred = model.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(Y_test, Y_test_pred))

print("\nClassification Report:")
print(classification_report(Y_test, Y_test_pred, target_names=['Healthy', "Parkinson's"]))

print("Precision:", precision_score(Y_test, Y_test_pred))
print("Recall:", recall_score(Y_test, Y_test_pred))
print("F1 Score:", f1_score(Y_test, Y_test_pred))

Y_test_proba = model.predict_proba(X_test)[:, 1]
print("ROC-AUC Score:", roc_auc_score(Y_test, Y_test_proba))

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
cv_scores = cross_val_score(model, X, Y, cv=cv, scoring='accuracy')
print("\n5-Fold Cross-Validation Accuracy Scores:", cv_scores)
print("Mean CV Accuracy: %.3f (+/- %.3f)" % (cv_scores.mean(), cv_scores.std()))
