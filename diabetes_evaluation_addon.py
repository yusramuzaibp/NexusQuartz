# ============================================================
# ADD THIS to "Multiple disease prediction system - diabetes.ipynb"
# Paste it as a new cell right after your existing accuracy_score cells.
# Uses `classifier`, `X`, `Y`, `X_train`, `X_test`, `Y_train`, `Y_test`
# which already exist earlier in your notebook -- no other changes needed,
# EXCEPT: change your model creation line to add probability=True:
#     classifier = svm.SVC(kernel='linear', probability=True)
# (ROC-AUC needs predicted probabilities, not just 0/1 labels)
# ============================================================

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (confusion_matrix, classification_report,
                              precision_score, recall_score, f1_score, roc_auc_score)

# ---- Confusion matrix + precision/recall/F1 on the held-out test set ----
Y_test_pred = classifier.predict(X_test)

print("Confusion Matrix:")
print(confusion_matrix(Y_test, Y_test_pred))
# Rows = actual class, Columns = predicted class
# [[True Negative,  False Positive],
#  [False Negative, True Positive]]

print("\nClassification Report:")
print(classification_report(Y_test, Y_test_pred, target_names=['Non-Diabetic', 'Diabetic']))

print("Precision:", precision_score(Y_test, Y_test_pred))
print("Recall:", recall_score(Y_test, Y_test_pred))
print("F1 Score:", f1_score(Y_test, Y_test_pred))

# ---- ROC-AUC (needs predicted probabilities) ----
Y_test_proba = classifier.predict_proba(X_test)[:, 1]
print("ROC-AUC Score:", roc_auc_score(Y_test, Y_test_proba))

# ---- 5-fold cross-validation (more trustworthy than one train/test split) ----
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)
cv_scores = cross_val_score(classifier, X, Y, cv=cv, scoring='accuracy')
print("\n5-Fold Cross-Validation Accuracy Scores:", cv_scores)
print("Mean CV Accuracy: %.3f (+/- %.3f)" % (cv_scores.mean(), cv_scores.std()))
