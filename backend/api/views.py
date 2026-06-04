"""
API Views for PhishShield AI
Provides endpoints for URL prediction, stats, and model comparison.
"""

import json
import os
import numpy as np
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import joblib

from .feature_extractor import FeatureExtractor


# Load model and scaler at module level for performance. Real-world model loaded.
_model = None
_scaler = None
_metrics = None
_extractor = FeatureExtractor()


def _load_model():
    """Lazy-load the ML model and scaler."""
    global _model, _scaler, _metrics
    if _model is None:
        model_path = settings.ML_MODEL_PATH
        scaler_path = settings.ML_SCALER_PATH
        metrics_path = settings.ML_METRICS_PATH

        if model_path.exists():
            _model = joblib.load(model_path)
            print(f"[PhishShield] Model loaded from {model_path}")
        else:
            print(f"[PhishShield] WARNING: Model not found at {model_path}")
            print("[PhishShield] Run 'python ml/train_model.py' to train the model first.")

        if scaler_path.exists():
            _scaler = joblib.load(scaler_path)

        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                _metrics = json.load(f)


@csrf_exempt
@require_http_methods(["POST"])
def predict_url(request):
    """
    Predict whether a URL is phishing or legitimate.
    
    POST /api/predict/
    Body: {"url": "https://example.com"}
    
    Returns: prediction result with confidence and feature analysis
    """
    _load_model()

    try:
        data = json.loads(request.body)
        url = data.get('url', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({
            'error': 'Invalid JSON body. Send {"url": "https://example.com"}'
        }, status=400)

    if not url:
        return JsonResponse({
            'error': 'URL is required'
        }, status=400)

    if _model is None:
        return JsonResponse({
            'error': 'Model not loaded. Run train_model.py first.'
        }, status=503)

    # Extract features
    features = _extractor.extract_features(url)
    feature_vector = list(features.values())
    feature_names = list(features.keys())

    # Make prediction
    try:
        feature_array = np.array([feature_vector])
        prediction = _model.predict(feature_array)[0]
        probabilities = _model.predict_proba(feature_array)[0]

        confidence = float(max(probabilities)) * 100
        is_phishing = int(prediction) == 1

        # Get feature importance for explanation
        importances = _model.feature_importances_
        top_features = sorted(
            zip(feature_names, importances, feature_vector),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        result = {
            'url': url,
            'prediction': 'phishing' if is_phishing else 'legitimate',
            'is_phishing': is_phishing,
            'confidence': round(confidence, 1),
            'phishing_probability': round(float(probabilities[1]) * 100, 1),
            'legitimate_probability': round(float(probabilities[0]) * 100, 1),
            'risk_level': _get_risk_level(float(probabilities[1])),
            'features_analyzed': len(features),
            'top_features': [
                {
                    'name': name.replace('_', ' ').title(),
                    'importance': round(float(imp) * 100, 1),
                    'value': float(val) if not isinstance(val, (int, np.integer)) else int(val)
                }
                for name, imp, val in top_features
            ],
            'all_features': {
                name.replace('_', ' ').title(): (
                    float(val) if not isinstance(val, (int, np.integer)) else int(val)
                )
                for name, val in features.items()
            }
        }

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'error': f'Prediction error: {str(e)}'
        }, status=500)


def _get_risk_level(phishing_prob):
    """Determine risk level from phishing probability."""
    if phishing_prob >= 0.8:
        return 'critical'
    elif phishing_prob >= 0.6:
        return 'high'
    elif phishing_prob >= 0.4:
        return 'medium'
    elif phishing_prob >= 0.2:
        return 'low'
    return 'safe'


@require_http_methods(["GET"])
def get_stats(request):
    """
    Get model statistics and dataset information.
    
    GET /api/stats/
    """
    _load_model()

    if _metrics is None:
        return JsonResponse({
            'error': 'Metrics not available. Run train_model.py first.'
        }, status=503)

    return JsonResponse(_metrics)


@require_http_methods(["GET"])
def get_model_comparison(request):
    """
    Get accuracy comparison of all trained models.
    
    GET /api/models/
    """
    _load_model()

    if _metrics is None:
        return JsonResponse({
            'error': 'Metrics not available. Run train_model.py first.'
        }, status=503)

    return JsonResponse({
        'models': _metrics.get('model_results', {}),
        'best_model': _metrics.get('best_model', 'Random Forest'),
        'dataset_stats': _metrics.get('dataset_stats', {})
    })
