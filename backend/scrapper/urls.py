from django.urls import path
from . import views
from .views import scrap
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.scrap,name='scrap'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    print("scrapper/urls.py  urlpatterns is :   ", urlpatterns)
    print("\n")