"""
ML Model Training Script for PhishShield AI
Trains Random Forest, Decision Tree, Naive Bayes, and Logistic Regression
on phishing URL dataset and saves the best model.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Add parent to path so we can import feature_extractor
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
import joblib


def generate_synthetic_dataset(n_samples=11055):
    """
    Generate a synthetic phishing URL dataset with realistic feature distributions.
    This mirrors the Kaggle 'Web page Phishing Detection Dataset' structure.
    
    For production: replace this with the actual Kaggle dataset CSV.
    """
    np.random.seed(42)

    n_phishing = int(n_samples * 0.443)  # ~44.3% phishing
    n_legitimate = n_samples - n_phishing

    def generate_legitimate(n):
        return pd.DataFrame({
            'url_length': np.random.normal(45, 15, n).clip(15, 100).astype(int),
            'domain_length': np.random.normal(12, 4, n).clip(4, 30).astype(int),
            'path_length': np.random.normal(15, 8, n).clip(0, 60).astype(int),
            'num_dots': np.random.choice([1, 2, 3], n, p=[0.4, 0.45, 0.15]),
            'num_hyphens': np.random.choice([0, 1, 2], n, p=[0.6, 0.3, 0.1]),
            'num_underscores': np.random.choice([0, 1], n, p=[0.85, 0.15]),
            'num_slashes': np.random.choice([2, 3, 4, 5], n, p=[0.3, 0.35, 0.25, 0.1]),
            'num_query_marks': np.random.choice([0, 1], n, p=[0.6, 0.4]),
            'num_ampersands': np.random.choice([0, 1, 2, 3], n, p=[0.5, 0.3, 0.15, 0.05]),
            'num_equals': np.random.choice([0, 1, 2, 3], n, p=[0.45, 0.3, 0.15, 0.1]),
            'has_at_symbol': np.random.choice([0, 1], n, p=[0.99, 0.01]),
            'has_ip_address': np.random.choice([0, 1], n, p=[0.98, 0.02]),
            'uses_https': np.random.choice([0, 1], n, p=[0.15, 0.85]),
            'num_subdomains': np.random.choice([0, 1, 2], n, p=[0.5, 0.4, 0.1]),
            'has_suspicious_tld': np.random.choice([0, 1], n, p=[0.95, 0.05]),
            'num_digits': np.random.normal(3, 2, n).clip(0, 15).astype(int),
            'num_digits_domain': np.random.choice([0, 1, 2], n, p=[0.7, 0.2, 0.1]),
            'num_special_chars': np.random.normal(4, 2, n).clip(0, 15).astype(int),
            'has_port': np.random.choice([0, 1], n, p=[0.98, 0.02]),
            'url_entropy': np.random.normal(3.5, 0.5, n).clip(1.5, 5.0).round(4),
            'domain_entropy': np.random.normal(2.8, 0.4, n).clip(1.0, 4.5).round(4),
            'num_suspicious_keywords': np.random.choice([0, 1], n, p=[0.85, 0.15]),
            'is_shortened': np.random.choice([0, 1], n, p=[0.97, 0.03]),
            'path_double_slash': np.random.choice([0, 1], n, p=[0.95, 0.05]),
            'has_redirect': np.random.choice([0, 1], n, p=[0.97, 0.03]),
            'domain_has_numbers': np.random.choice([0, 1], n, p=[0.8, 0.2]),
            'query_length': np.random.normal(10, 12, n).clip(0, 80).astype(int),
            'num_query_params': np.random.choice([0, 1, 2, 3], n, p=[0.4, 0.3, 0.2, 0.1]),
            'has_fragment': np.random.choice([0, 1], n, p=[0.9, 0.1]),
            'url_depth': np.random.choice([1, 2, 3, 4], n, p=[0.25, 0.35, 0.25, 0.15]),
            'label': np.zeros(n, dtype=int)
        })

    def generate_phishing(n):
        return pd.DataFrame({
            'url_length': np.random.normal(75, 25, n).clip(30, 200).astype(int),
            'domain_length': np.random.normal(22, 8, n).clip(8, 60).astype(int),
            'path_length': np.random.normal(30, 15, n).clip(5, 100).astype(int),
            'num_dots': np.random.choice([2, 3, 4, 5], n, p=[0.2, 0.35, 0.3, 0.15]),
            'num_hyphens': np.random.choice([0, 1, 2, 3, 4], n, p=[0.2, 0.3, 0.25, 0.15, 0.1]),
            'num_underscores': np.random.choice([0, 1, 2], n, p=[0.5, 0.3, 0.2]),
            'num_slashes': np.random.choice([3, 4, 5, 6, 7], n, p=[0.15, 0.25, 0.3, 0.2, 0.1]),
            'num_query_marks': np.random.choice([0, 1, 2], n, p=[0.3, 0.4, 0.3]),
            'num_ampersands': np.random.choice([0, 1, 2, 3, 4], n, p=[0.25, 0.3, 0.2, 0.15, 0.1]),
            'num_equals': np.random.choice([0, 1, 2, 3, 4], n, p=[0.2, 0.25, 0.25, 0.2, 0.1]),
            'has_at_symbol': np.random.choice([0, 1], n, p=[0.85, 0.15]),
            'has_ip_address': np.random.choice([0, 1], n, p=[0.75, 0.25]),
            'uses_https': np.random.choice([0, 1], n, p=[0.55, 0.45]),
            'num_subdomains': np.random.choice([0, 1, 2, 3, 4], n, p=[0.15, 0.25, 0.3, 0.2, 0.1]),
            'has_suspicious_tld': np.random.choice([0, 1], n, p=[0.45, 0.55]),
            'num_digits': np.random.normal(8, 4, n).clip(0, 25).astype(int),
            'num_digits_domain': np.random.choice([0, 1, 2, 3, 4], n, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
            'num_special_chars': np.random.normal(8, 4, n).clip(1, 25).astype(int),
            'has_port': np.random.choice([0, 1], n, p=[0.85, 0.15]),
            'url_entropy': np.random.normal(4.2, 0.5, n).clip(2.5, 5.5).round(4),
            'domain_entropy': np.random.normal(3.5, 0.5, n).clip(2.0, 5.0).round(4),
            'num_suspicious_keywords': np.random.choice([0, 1, 2, 3], n, p=[0.2, 0.35, 0.3, 0.15]),
            'is_shortened': np.random.choice([0, 1], n, p=[0.8, 0.2]),
            'path_double_slash': np.random.choice([0, 1], n, p=[0.7, 0.3]),
            'has_redirect': np.random.choice([0, 1], n, p=[0.75, 0.25]),
            'domain_has_numbers': np.random.choice([0, 1], n, p=[0.4, 0.6]),
            'query_length': np.random.normal(25, 18, n).clip(0, 120).astype(int),
            'num_query_params': np.random.choice([0, 1, 2, 3, 4, 5], n, p=[0.15, 0.2, 0.25, 0.2, 0.12, 0.08]),
            'has_fragment': np.random.choice([0, 1], n, p=[0.7, 0.3]),
            'url_depth': np.random.choice([2, 3, 4, 5, 6], n, p=[0.15, 0.25, 0.3, 0.2, 0.1]),
            'label': np.ones(n, dtype=int)
        })

    legitimate = generate_legitimate(n_legitimate)
    phishing = generate_phishing(n_phishing)

    # Combine and shuffle
    dataset = pd.concat([legitimate, phishing], ignore_index=True)
    dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)

    return dataset


def train_models(dataset):
    """Train all models and return metrics."""
    feature_cols = [col for col in dataset.columns if col != 'label']
    X = dataset[feature_cols].values
    y = dataset['label'].values

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Define models
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),
        'Decision Tree': DecisionTreeClassifier(
            max_depth=15,
            min_samples_split=5,
            random_state=42
        ),
        'Naive Bayes': GaussianNB(),
        'Logistic Regression': LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    }

    results = {}

    for name, model in models.items():
        print(f"\n{'='*50}")
        print(f"Training {name}...")
        print(f"{'='*50}")

        # Train
        if name in ['Logistic Regression', 'Naive Bayes']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            'accuracy': round(accuracy * 100, 1),
            'precision': round(precision * 100, 1),
            'recall': round(recall * 100, 1),
            'f1_score': round(f1 * 100, 1),
            'confusion_matrix': {
                'true_negative': int(cm[0][0]),
                'false_positive': int(cm[0][1]),
                'false_negative': int(cm[1][0]),
                'true_positive': int(cm[1][1])
            }
        }

        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1 Score:  {f1:.4f}")
        print(f"\nConfusion Matrix:\n{cm}")
        print(f"\n{classification_report(y_test, y_pred)}")

    # Cross-validation for Random Forest
    print("\n" + "="*50)
    print("Cross-Validation (Random Forest, 10-fold)")
    print("="*50)
    rf_model = models['Random Forest']
    cv_scores = cross_val_score(rf_model, X, y, cv=10, scoring='accuracy')
    print(f"CV Scores: {cv_scores}")
    print(f"Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    return models, scaler, results, feature_cols


def main():
    """Main training pipeline."""
    # Paths
    ml_dir = Path(__file__).resolve().parent
    data_dir = ml_dir.parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    # Check for custom dataset file in command line arguments
    dataset_filename = 'dataset.csv'
    if len(sys.argv) > 1:
        dataset_filename = sys.argv[1]

    dataset_path = data_dir / dataset_filename

    # Generate or load dataset
    if dataset_path.exists():
        print(f"Loading existing dataset from {dataset_path}...")
        dataset = pd.read_csv(dataset_path)
    else:
        if dataset_filename != 'dataset.csv':
            print(f"Error: Custom dataset file {dataset_path} not found.")
            sys.exit(1)
        print("Generating synthetic phishing URL dataset...")
        dataset = generate_synthetic_dataset()
        dataset.to_csv(dataset_path, index=False)
        print(f"Dataset saved to {dataset_path}")

    print(f"\nDataset shape: {dataset.shape}")
    print(f"Phishing URLs: {(dataset['label'] == 1).sum()}")
    print(f"Legitimate URLs: {(dataset['label'] == 0).sum()}")

    # Train models
    models, scaler, results, feature_cols = train_models(dataset)

    # Save the best model (Random Forest)
    rf_model = models['Random Forest']
    model_path = ml_dir / 'model.pkl'
    scaler_path = ml_dir / 'scaler.pkl'
    metrics_path = ml_dir / 'metrics.json'

    joblib.dump(rf_model, model_path)
    print(f"\nRandom Forest model saved to {model_path}")

    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to {scaler_path}")

    # Save all metrics
    metrics = {
        'model_results': results,
        'feature_names': feature_cols,
        'dataset_stats': {
            'total_samples': len(dataset),
            'phishing_urls': int((dataset['label'] == 1).sum()),
            'legitimate_urls': int((dataset['label'] == 0).sum()),
            'training_split': '80% / 20%',
            'cross_validation': '10-fold'
        },
        'best_model': 'Random Forest',
        'best_accuracy': results['Random Forest']['accuracy']
    }

    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")

    print("\n" + "="*50)
    print("TRAINING COMPLETE!")
    print(f"Best Model: Random Forest ({results['Random Forest']['accuracy']}% accuracy)")
    print("="*50)


if __name__ == '__main__':
    main()
