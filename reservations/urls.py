from django.urls import path
from .views import *
from .api import api_get_reservation

app_name = 'reservations'

urlpatterns = [
    path('', reservation_management_view, name='list'),
    path('<int:restaurant_id>/reserve/', reservation, name='create'),
    path('<int:reservation_id>/edit/', edit_reservation, name='edit'),
    
    path('api/get/<int:reservation_id>/', api_get_reservation, name='api_get'),
]

