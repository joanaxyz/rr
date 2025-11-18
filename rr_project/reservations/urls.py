from django.urls import path
from .views import *
from .api import api_get_reservation
app_name = 'reservations'

urlpatterns = [
    path('reservations/', reservation_management_view, name='reservation_management'),
    path('restaurant/<int:restaurant_id>/reserve/', reservation, name='reserve'),
    path('<int:reservation_id>/edit/', edit_reservation, name='edit_reservation'),
    
    path('api/get/<int:reservation_id>/', api_get_reservation, name='reservation_api'),
]

