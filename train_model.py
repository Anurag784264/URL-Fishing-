"""
Phishing URL Detection System - Model Training & Evaluation Pipeline
Course: AI Systems and Applications (AISA) - Mini Project
Department of Computer Engineering and Technology

This script implements:
1. Balanced dataset sampling from the authentic PhiUSIIL benchmark dataset.
2. Fast 15-feature lexical extraction.
3. Training & comparative benchmarking of:
   - Random Forest Classifier (Primary Deployed Model)
   - Decision Tree Classifier (Baseline Comparison)
4. Comprehensive evaluation metrics (Accuracy, Precision, Recall, F1, ROC-AUC).
5. Generation of high-resolution visual plots:
   - Confusion Matrix Heatmap
   - Top Feature Importance Bar Chart
   - Multi-Algorithm Performance Comparison
6. Serialization of trained model (`phishing_model.joblib`) and metrics (`model_metrics.json`).
"""

import os
import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

from feature_extractor import extract_url_features, FEATURE_NAMES

def train():
    print("=" * 70)
    print("      PHISHING URL DETECTION - SIMPLIFIED TRAINING PIPELINE")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)

    # Locate dataset
    dataset_path = os.path.join(base_dir, "fishing dataset.csv")
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join(parent_dir, "fishing dataset.csv")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset 'fishing dataset.csv' not found at {dataset_path}")

    print(f"[*] Loading dataset from: {dataset_path}")
    t0 = time.time()
    df = pd.read_csv(dataset_path, usecols=['URL', 'label'])
    print(f"[+] Loaded {len(df):,} total samples in {time.time() - t0:.2f}s")

    # Balanced sampling: 20,000 legitimate and 20,000 phishing
    print("[*] Creating balanced sample (20,000 Legitimate + 20,000 Phishing = 40,000 URLs)...")
    df_legit = df[df['label'] == 1].sample(n=min(20000, sum(df['label'] == 1)), random_state=42)
    df_phish = df[df['label'] == 0].sample(n=min(20000, sum(df['label'] == 0)), random_state=42)
    df_sample = pd.concat([df_legit, df_phish]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    print(f"[+] Balanced dataset shape: {df_sample.shape}")
    print(f"    - Legitimate (1): {sum(df_sample['label'] == 1):,}")
    print(f"    - Phishing (0):   {sum(df_sample['label'] == 0):,}")

    # Feature extraction
    print("\n[*] Extracting 15 lexical features from URLs...")
    t_feat_start = time.time()
    feature_rows = []
    for url in df_sample['URL']:
        feats, _ = extract_url_features(url)
        feature_rows.append([feats[name] for name in FEATURE_NAMES])

    X = np.array(feature_rows)
    y = df_sample['label'].values
    print(f"[+] Feature matrix created: shape={X.shape} in {time.time() - t_feat_start:.2f}s")

    # 80/20 Stratified Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[+] Train samples: {len(X_train):,}, Test samples: {len(X_test):,}")

    # ----------------- MODEL TRAINING & BENCHMARKING -----------------
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=12,
            random_state=42
        )
    }

    results = {}

    print("\n" + "=" * 70)
    print(f"{'Algorithm':<20} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'ROC-AUC':<10}")
    print("-" * 78)

    for name, clf in models.items():
        t_train_start = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - t_train_start

        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        roc = roc_auc_score(y_test, y_prob)

        results[name] = {
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "roc_auc": float(roc),
            "training_time_sec": round(train_time, 4)
        }

        print(f"{name:<20} | {acc*100:>8.2f}% | {prec*100:>8.2f}% | {rec*100:>8.2f}% | {f1*100:>8.2f}% | {roc:>10.4f}")

    print("=" * 78)

    # Primary model selection: Random Forest
    primary_clf = models["Random Forest"]
    rf_preds = primary_clf.predict(X_test)
    rf_probs = primary_clf.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, rf_preds)
    tn, fp, fn, tp = cm.ravel()
    print(f"\n[+] Confusion Matrix (Random Forest):")
    print(f"    True Negative (Phishing Caught):  {tn:,}")
    print(f"    False Positive (False Alarm):    {fp:,}")
    print(f"    False Negative (Missed Threat):  {fn:,}")
    print(f"    True Positive (Legit Verified):  {tp:,}")

    # ----------------- PLOT 1: Confusion Matrix -----------------
    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion Matrix (Random Forest)", fontsize=13, fontweight='bold', pad=12)
    plt.colorbar(fraction=0.046, pad=0.04)
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ['Phishing (0)', 'Legitimate (1)'], fontsize=10)
    plt.yticks(tick_marks, ['Phishing (0)', 'Legitimate (1)'], fontsize=10)

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "black"
            plt.text(j, i, f"{val:,}", horizontalalignment="center",
                     verticalalignment="center", color=color, fontsize=12, fontweight='bold')

    plt.ylabel('True Class', fontsize=11, fontweight='bold')
    plt.xlabel('Predicted Class', fontsize=11, fontweight='bold')
    plt.tight_layout()
    cm_path = os.path.join(base_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"[+] Saved {cm_path}")

    # ----------------- PLOT 2: Feature Importance -----------------
    importances = primary_clf.feature_importances_
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(8, 5))
    plt.barh(range(len(FEATURE_NAMES)), importances[indices][::-1], color="#2563EB", align="center")
    sorted_names = [FEATURE_NAMES[i] for i in indices][::-1]
    plt.yticks(range(len(FEATURE_NAMES)), sorted_names, fontsize=9)
    plt.xlabel("Gini Feature Importance", fontsize=10, fontweight='bold')
    plt.title("Feature Importance Ranking (Random Forest)", fontsize=12, fontweight='bold', pad=10)
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    fi_path = os.path.join(base_dir, "feature_importance.png")
    plt.savefig(fi_path, dpi=200)
    plt.close()
    print(f"[+] Saved {fi_path}")

    # ----------------- PLOT 3: Model Comparison -----------------
    plt.figure(figsize=(7, 4.5))
    metrics_to_plot = ["accuracy", "precision", "recall", "f1_score"]
    x = np.arange(len(metrics_to_plot))
    width = 0.35

    rf_vals = [results["Random Forest"][m] * 100 for m in metrics_to_plot]
    dt_vals = [results["Decision Tree"][m] * 100 for m in metrics_to_plot]

    plt.bar(x - width/2, rf_vals, width, label='Random Forest', color='#1D4ED8')
    plt.bar(x + width/2, dt_vals, width, label='Decision Tree', color='#059669')

    plt.ylabel('Score (%)', fontsize=10, fontweight='bold')
    plt.title('Algorithm Performance Comparison', fontsize=12, fontweight='bold', pad=10)
    plt.xticks(x, ['Accuracy', 'Precision', 'Recall', 'F1-Score'], fontsize=10)
    plt.ylim(90, 101)
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    mc_path = os.path.join(base_dir, "model_comparison.png")
    plt.savefig(mc_path, dpi=200)
    plt.close()
    print(f"[+] Saved {mc_path}")

    # ----------------- SAVE MODEL ARTIFACTS -----------------
    model_save_path = os.path.join(base_dir, "phishing_model.joblib")
    joblib.dump(primary_clf, model_save_path)
    print(f"[+] Model saved successfully to: {model_save_path}")

    metrics_payload = {
        "dataset_sample_size": len(df_sample),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_names": FEATURE_NAMES,
        "selected_model": "Random Forest Classifier",
        "selected_model_metrics": results["Random Forest"],
        "models_benchmarked": results,
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp)
        }
    }

    metrics_path = os.path.join(base_dir, "model_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)
    print(f"[+] Metrics metadata saved to: {metrics_path}")

    print("\n[SUCCESS] Model training and evaluation completed successfully!")
    return results


if __name__ == "__main__":
    train()
