"""
URL configuration for phishshield project.
Serves the frontend at root and API at /api/
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.http import FileResponse
import os


def serve_css(request):
    """Serve the main CSS file"""
    css_path = os.path.join(settings.FRONTEND_DIR, 'css', 'style.css')
    return FileResponse(open(css_path, 'rb'), content_type='text/css')


def serve_js(request):
    """Serve the main JS file"""
    js_path = os.path.join(settings.FRONTEND_DIR, 'js', 'app.js')
    return FileResponse(open(js_path, 'rb'), content_type='application/javascript')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('css/style.css', serve_css, name='serve_css'),
    path('js/app.js', serve_js, name='serve_js'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('index.html', TemplateView.as_view(template_name='index.html')),
    path('detection', TemplateView.as_view(template_name='detection.html'), name='detection'),
    path('detection.html', TemplateView.as_view(template_name='detection.html')),
    path('features', TemplateView.as_view(template_name='features.html'), name='features'),
    path('features.html', TemplateView.as_view(template_name='features.html')),
    path('results', TemplateView.as_view(template_name='results.html'), name='results'),
    path('results.html', TemplateView.as_view(template_name='results.html')),
    path('about', TemplateView.as_view(template_name='about.html'), name='about'),
    path('about.html', TemplateView.as_view(template_name='about.html')),
    path('contact', TemplateView.as_view(template_name='contact.html'), name='contact'),
    path('contact.html', TemplateView.as_view(template_name='contact.html')),
]
