# Machine Learning Model Training & Evaluation Guide

This guide outlines the step-by-step procedure to train, evaluate, and deploy a classical ML (Random Forest/XGBoost) or temporal neural network (LSTM/GRU) model for cricket shot classification.

## 1. Feature Extraction & Dataset Export

Run the feature extraction tool across all annotated raw video clips in `data/raw/`:

```bash
python backend/app/ml/dataset_exporter.py --input_dir data/raw/ --output_csv data/processed/cricket_features.csv
```

The exporter constructs a 12-dimensional feature vector per clip:
1. `head_instability_score`
2. `min_knee_flex_angle`
3. `avg_trunk_inclination`
4. `max_elbow_extension`
5. `trunk_mean`, `trunk_std`
6. `min_left_knee`, `min_right_knee`
7. `max_left_elbow`, `max_right_elbow`
8. `mean_left_knee`, `mean_right_knee`

---

## 2. Model Training Protocol

Train a Random Forest / SVM classifier using scikit-learn:

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pickle

# Load dataset
X_train, y_train, X_test, y_test = load_dataset("data/processed/cricket_features.csv")

# Train Random Forest Classifier
clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# Save serialized model artifact
with open("models/shot_classifier.pkl", "wb") as f:
    pickle.dump(clf, f)
```

---

## 3. Pluggable Integration into System

Once saved to `models/shot_classifier.pkl`, the `ShotClassifier` service in `backend/app/ml/shot_classifier.py` automatically detects and loads the ML model on backend startup.
