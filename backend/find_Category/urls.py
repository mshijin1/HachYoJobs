from django.urls import path
from . import views
from .views import find_Type
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('find_Type/',views.find_Type,name='find_Type'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)