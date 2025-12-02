
from django.urls import path
from .views import *

app_name = 'restaurants'

urlpatterns = [
    path('restaurants/', restaurants_view, name='restaurants'),
    path('restaurant/<int:restaurant_id>/', restaurant_detail_view, name='restaurant_detail'),
    path('restaurant/<int:restaurant_id>/bookmark/', toggle_bookmark, name='toggle_bookmark'),
]