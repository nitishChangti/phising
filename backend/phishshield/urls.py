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
]
