from django.urls import path
from .views import *

app_name = 'reservations'

urlpatterns = [
    path('reservations/', reservation_management_view, name='reservation_management'),
    path('restaurant/<int:restaurant_id>/reserve/', reservation, name='reserve'),
    path('<int:reservation_id>/edit/', edit_reservation, name='edit_reservation'),
]

