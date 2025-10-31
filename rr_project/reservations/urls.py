# urls.py
from django.urls import path
from .views import *
app_name = 'reservations'

urlpatterns = [
    path('restaurant/<int:restaurant_id>/reserve/', reservation, name='reserve'),
    path('reservations/', reservation_management_view, name='reservation_management'),
]