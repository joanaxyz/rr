# urls.py
from django.urls import path
from .views import home_view

app_name = 'home'

urlpatterns = [
    # Main application URLs
    path('', home_view, name='home'),
]