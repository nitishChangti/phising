"""
API Views for PhishShield AI
Provides endpoints for URL prediction, stats, and model comparison.
"""

import json
import os
import socket
import urllib.parse
import numpy as np
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import joblib

from .feature_extractor import FeatureExtractor
from .models import URLScan


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


# Trigger reload of model.pkl
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

    if not url.startswith(('http://', 'https://')):
        return JsonResponse({
            'error': 'URL must start with http:// or https://'
        }, status=400)

    # Validate domain and check DNS resolution
    try:
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.hostname
        if not domain:
            return JsonResponse({'error': 'Invalid URL format: No domain found.'}, status=400)
        
        # Resolve the domain to ensure it actually exists on the internet
        socket.gethostbyname(domain)
    except socket.gaierror:
        return JsonResponse({
            'error': 'This domain does not exist or is offline. Only live websites can be scanned.'
        }, status=400)
    except Exception as e:
        return JsonResponse({'error': f'URL parsing error: {str(e)}'}, status=400)

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

        # Save to scan history database
        try:
            URLScan.objects.create(
                url=url,
                prediction=result['prediction'],
                confidence=result['confidence'],
                risk_level=result['risk_level']
            )
        except Exception as db_err:
            print(f"[PhishShield] History database save error: {db_err}")

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
    Get accuracy comparison of all trained models and feature importance metrics.
    
    GET /api/models/
    """
    _load_model()
    from .models import SystemMetrics

    # Fetch from database first (dynamic, no restart needed)
    try:
        latest_metrics = SystemMetrics.objects.latest('updated_at')
        metrics_data = latest_metrics.metrics_data
    except SystemMetrics.DoesNotExist:
        # Fallback to the global JSON file loaded in _load_model()
        metrics_data = _metrics

    if not metrics_data:
        return JsonResponse({
            'error': 'Metrics not available. Run train_model.py first.'
        }, status=503)

    # Calculate feature importances dynamically
    feature_importance = []
    if _model is not None:
        try:
            importances = _model.feature_importances_
            feature_names = metrics_data.get('feature_names', [])
            features_zipped = sorted(
                zip(feature_names, importances),
                key=lambda x: x[1],
                reverse=True
            )
            feature_importance = [
                {
                    'name': name.replace('_', ' ').title(),
                    'importance': round(float(imp) * 100, 1)
                }
                for name, imp in features_zipped[:8]
            ]
        except Exception as e:
            print(f"Error extracting feature importances: {e}")

    return JsonResponse({
        'models': metrics_data.get('model_results', {}),
        'best_model': metrics_data.get('best_model', 'Random Forest'),
        'dataset_stats': metrics_data.get('dataset_stats', {}),
        'feature_importance': feature_importance
    })


@require_http_methods(["GET"])
def get_history(request):
    """
    Get the 10 most recent URL scans from the database.
    
    GET /api/history/
    """
    try:
        scans = URLScan.objects.all()[:10]
        history_list = [
            {
                'url': scan.url,
                'prediction': scan.prediction,
                'confidence': scan.confidence,
                'risk_level': scan.risk_level,
                'timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            for scan in scans
        ]
        return JsonResponse({'history': history_list})
    except Exception as e:
        return JsonResponse({'error': f'Database query error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def subscribe_newsletter(request):
    """
    Subscribe an email to Brevo newsletter.
    
    POST /api/subscribe/
    Body: {"email": "user@example.com"}
    """
    import requests
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email or '@' not in email or '.' not in email:
            return JsonResponse({'error': 'Please provide a valid email address'}, status=400)
            
        api_key = getattr(settings, 'BREVO_API_KEY', os.environ.get('BREVO_API_KEY'))
        if not api_key:
            # Fallback for development if API key is missing
            print(f"[PhishShield] Brevo Mock Subscription: {email}")
            return JsonResponse({'message': 'Subscribed successfully (Mock mode)'})
            
        url = "https://api.brevo.com/v3/contacts"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        payload = {
            "email": email,
            "updateEnabled": True
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [201, 204]:
            return JsonResponse({'message': 'Subscribed successfully'})
        elif response.status_code == 400 and 'duplicate' in response.text.lower():
            return JsonResponse({'message': 'Already subscribed!'})
        else:
            return JsonResponse({
                'error': 'Failed to subscribe with Brevo',
                'details': response.json() if response.text else 'Unknown error'
            }, status=response.status_code)
            
    except Exception as e:
        return JsonResponse({'error': f'Subscription error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_contact(request):
    """
    Send contact form message via Brevo Transactional Email API.
    
    POST /api/contact/
    Body: {"name": "John", "email": "john@example.com", "subject": "Hello", "message": "Test"}
    """
    import requests
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        if not all([name, email, subject, message]):
            return JsonResponse({'error': 'All fields are required.'}, status=400)
            
        if '@' not in email or '.' not in email:
            return JsonResponse({'error': 'Please provide a valid email address.'}, status=400)
            
        api_key = getattr(settings, 'BREVO_API_KEY', os.environ.get('BREVO_API_KEY'))
        if not api_key:
            # Fallback for development if API key is missing
            print(f"[PhishShield] Brevo Mock Contact Form: From {name} ({email}) - {subject}\n{message}")
            return JsonResponse({'message': 'Message sent successfully! (Mock mode)'})
            
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        # Send to the site admin (or you can use the sender's email if configured in Brevo)
        # Brevo requires the sender to be a verified domain/email in your account.
        # So we set sender as the site admin, and reply-to as the user.
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'support@phishshield.ai')
        
        payload = {
            "sender": {"name": "PhishShield Contact Form", "email": admin_email},
            "to": [{"email": admin_email, "name": "PhishShield Admin"}],
            "replyTo": {"email": email, "name": name},
            "subject": f"New Contact: {subject}",
            "htmlContent": f"<h3>New message from {name} ({email})</h3><p><strong>Subject:</strong> {subject}</p><hr><p>{message.replace(chr(10), '<br>')}</p>"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [201, 204]:
            return JsonResponse({'message': 'Message sent successfully!'})
        else:
            return JsonResponse({
                'error': 'Failed to send message via Brevo',
                'details': response.json() if response.text else 'Unknown error'
            }, status=response.status_code)
            
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
