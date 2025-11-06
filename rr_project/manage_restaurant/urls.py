from django.urls import path
from . import views

app_name = "manage_restaurant"

urlpatterns = [
    path("", views.view_restaurants, name="list"),
    path("<int:restaurant_id>/dashboard/", views.dashboard, name="dashboard"),
    path("<int:restaurant_id>/reservations/", views.manage_reservations, name="reservations"),
    path("<int:restaurant_id>/tables/", views.manage_tables, name="tables"),
    path("<int:restaurant_id>/details/", views.manage_details, name="details"),
]
