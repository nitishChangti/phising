"""
API URL configuration for PhishShield AI
"""

from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_url, name='predict_url'),
    path('stats/', views.get_stats, name='get_stats'),
    path('models/', views.get_model_comparison, name='get_model_comparison'),
    path('history/', views.get_history, name='get_history'),
]
