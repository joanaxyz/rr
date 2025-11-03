from django.urls import path
from . import views

app_name = "manage_restaurant"

urlpatterns = [
    path("", views.manage_restaurants, name="list"),
    path("<int:restaurant_id>/", views.manage_restaurant_detail, name="detail"),
]
