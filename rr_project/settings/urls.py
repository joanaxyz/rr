
from django.urls import path
from .views import settings_view, update_profile, change_password

app_name = 'settings'

urlpatterns = [
    path('', settings_view, name='settings'),
    path('update-profile/', update_profile, name='update_profile'),
    path('change-password/', change_password, name='change_password'),
]