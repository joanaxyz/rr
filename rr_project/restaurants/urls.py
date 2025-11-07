from django.urls import path
from . import views  # ✅ this is enough — no need for "from .views import *"

app_name = 'restaurants'

urlpatterns = [
    path('restaurants/', views.restaurants_view, name='restaurants'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail_view, name='restaurant_detail'),
    path('verify-owner/', views.owner_verification, name='owner_verification'),
    path('manage-restaurant/', views.manage_restaurant, name='manage_restaurant'),
]
