from django.urls import path
from .views import *

app_name = 'restaurants'

urlpatterns = [
    path('restaurants/', restaurants_view, name='restaurants'),
    path('restaurant/<int:restaurant_id>/', restaurant_detail_view, name='restaurant_detail'),
    path('create/', create_restaurant, name='create_restaurant'),
    path('success/', restaurant_success, name='restaurant_success'),
    path('manage-restaurant/', create_restaurant, name='manage_restaurant'),
]
